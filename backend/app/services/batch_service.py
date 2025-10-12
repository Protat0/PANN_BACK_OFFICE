from datetime import datetime, timedelta
from ..database import db_manager
from notifications.services import notification_service
import logging

logger = logging.getLogger(__name__)

class BatchService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.batch_collection = self.db.batches
        self.product_collection = self.db.products
        self.supplier_collection = self.db.suppliers
        
    def validate_foreign_keys(self, batch_data):
        """Validate that foreign key references exist"""
        # Validate product_id
        if 'product_id' in batch_data and batch_data['product_id']:
            product = self.product_collection.find_one({
                '_id': batch_data['product_id'],
                'isDeleted': {'$ne': True}
            })
            if not product:
                raise ValueError(f"Product with ID {batch_data['product_id']} not found")
        
        # Validate supplier_id if provided
        if 'supplier_id' in batch_data and batch_data['supplier_id']:
            supplier = self.supplier_collection.find_one({'_id': batch_data['supplier_id']})
            if not supplier:
                raise ValueError(f"Supplier with ID {batch_data['supplier_id']} not found")

    def _send_batch_notification(self, action_type, product_name, additional_metadata=None):
        """Centralized notification helper for batch actions"""
        try:
            titles = {
                'created': "New Batch Added",
                'stock_received': "Stock Received",
                'expiry_warning': "Expiry Warning",
                'batch_expired': "Batch Expired",
                'batch_depleted': "Batch Depleted"
            }
            
            messages = {
                'created': f"New batch created for '{product_name}'",
                'stock_received': f"Stock received for '{product_name}'",
                'expiry_warning': f"Batch expiring soon for '{product_name}'",
                'batch_expired': f"Batch expired for '{product_name}'",
                'batch_depleted': f"Batch depleted for '{product_name}'"
            }
            
            # Set priority based on action type
            if action_type in ['batch_expired', 'expiry_warning']:
                priority = "high"
                notification_type = "alert"
            elif action_type == 'batch_depleted':
                priority = "medium"
                notification_type = "alert"
            else:
                priority = "low"
                notification_type = "system"
            
            metadata = {
                "action_type": f"batch_{action_type}",
                "product_name": product_name
            }
            
            if additional_metadata:
                metadata.update(additional_metadata)
            
            notification_service.create_notification(
                title=titles.get(action_type, "Batch Action"),
                message=messages.get(action_type, f"Batch action '{action_type}' for '{product_name}'"),
                priority=priority,
                notification_type=notification_type,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Failed to send batch notification: {e}")

    def generate_batch_id(self, product_id):
        """Generate sequential batch ID for a product"""
        try:
            # Count existing batches for this product
            count = self.batch_collection.count_documents({'product_id': product_id}) + 1
            
            # Format: BATCH-PROD00001-001
            product_suffix = product_id.replace('PROD-', '')
            return f"BATCH-{product_suffix}-{count:03d}"
        
        except Exception:
            # Fallback
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            return f"BATCH-{product_id}-{timestamp}"

    def add_sync_log(self, source='cloud', status='synced', details=None):
        """Helper method to create sync log entries"""
        return {
            'last_updated': datetime.utcnow(),
            'source': source,
            'status': status,
            'details': details or {}
        }

    # ================================================================
    # CORE BATCH OPERATIONS
    # ================================================================
    
    def create_batch(self, batch_data):
        """Create a new batch when stock is received"""
        try:
            logger.info(f"Creating batch for product: {batch_data.get('product_id')}")
            
            # Validate foreign keys
            self.validate_foreign_keys(batch_data)
            
            # Generate batch ID
            batch_id = self.generate_batch_id(batch_data['product_id'])
            
            current_time = datetime.utcnow()
            
            # Handle expiry_date conversion
            expiry_date = batch_data.get('expiry_date')
            if expiry_date:
                if isinstance(expiry_date, str):
                    try:
                        # Try parsing different date formats
                        from dateutil import parser
                        expiry_date = parser.parse(expiry_date)
                    except Exception as e:
                        logger.warning(f"Could not parse expiry_date '{expiry_date}': {e}")
                        expiry_date = None
                elif not isinstance(expiry_date, datetime):
                    logger.warning(f"Invalid expiry_date type: {type(expiry_date)}")
                    expiry_date = None
            
            # Create batch document
            batch_document = {
                '_id': batch_id,
                'product_id': batch_data['product_id'],
                'batch_number': batch_data.get('batch_number', f"B-{current_time.strftime('%Y%m%d')}"),
                'quantity_received': int(batch_data.get('quantity_received', 0)),
                'quantity_remaining': int(batch_data.get('quantity_received', 0)),
                'cost_price': float(batch_data.get('cost_price', 0)),
                'expiry_date': expiry_date,
                'date_received': batch_data.get('date_received', current_time),
                'supplier_id': batch_data.get('supplier_id'),
                'status': 'active',
                'created_at': current_time,
                'updated_at': current_time,
                'sync_logs': [self.add_sync_log(source='cloud', status='pending', details={'action': 'created'})]
            }
            
            # Insert batch
            self.batch_collection.insert_one(batch_document)
            
            # Update product's simplified expiry tracking
            self.update_product_expiry_summary(batch_data['product_id'])
            
            # Get product name for notification
            product = self.product_collection.find_one({'_id': batch_data['product_id']})
            product_name = product.get('product_name', 'Unknown Product') if product else 'Unknown Product'
            
            # Send notification
            self._send_batch_notification(
                'stock_received',
                product_name,
                {
                    'batch_id': batch_id,
                    'quantity_received': batch_document['quantity_received'],
                    'expiry_date': batch_document['expiry_date'].isoformat() if batch_document['expiry_date'] else None,
                    'supplier_id': batch_document.get('supplier_id')
                }
            )
            
            # Return created batch
            created_batch = self.batch_collection.find_one({'_id': batch_id})
            return created_batch
        
        except Exception as e:
            logger.error(f"Error creating batch: {str(e)}")
            raise Exception(f"Error creating batch: {str(e)}")

    def get_batches_by_product(self, product_id, status=None):
        """Get all batches for a specific product"""
        try:
            query = {'product_id': product_id}
            
            if status:
                query['status'] = status
            
            batches = list(self.batch_collection.find(query).sort('expiry_date', 1))
            return batches
        
        except Exception as e:
            raise Exception(f"Error getting batches: {str(e)}")
    
    def update_product_expiry_summary(self, product_id):
        """Update product's simplified expiry tracking fields"""
        try:
            # Get active batches for this product
            active_batches = list(self.batch_collection.find({
                'product_id': product_id,
                'status': 'active',
                'quantity_remaining': {'$gt': 0}
            }).sort('expiry_date', 1))
            
            # Calculate summary fields
            update_data = {}
            
            if active_batches:
                # Get expiry dates (filter out None values)
                expiry_dates = [batch['expiry_date'] for batch in active_batches if batch.get('expiry_date')]
                
                if expiry_dates:
                    update_data['oldest_batch_expiry'] = min(expiry_dates)
                    update_data['newest_batch_expiry'] = max(expiry_dates)
                    
                    # Check if any batch is expiring within 30 days
                    warning_date = datetime.utcnow() + timedelta(days=30)
                    update_data['expiry_alert'] = any(exp_date <= warning_date for exp_date in expiry_dates)
                else:
                    # No expiry dates available
                    update_data['oldest_batch_expiry'] = None
                    update_data['newest_batch_expiry'] = None
                    update_data['expiry_alert'] = False
                
                # Calculate total stock from active batches
                total_stock = sum(batch['quantity_remaining'] for batch in active_batches)
                update_data['total_stock'] = total_stock
            else:
                # No active batches
                update_data.update({
                    'oldest_batch_expiry': None,
                    'newest_batch_expiry': None,
                    'expiry_alert': False,
                    'total_stock': 0
                })
            
            update_data['updated_at'] = datetime.utcnow()
            
            # Update product
            self.product_collection.update_one(
                {'_id': product_id},
                {'$set': update_data}
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Error updating product expiry summary: {str(e)}")
            return False

    def get_expiring_batches(self, days_ahead=30):
        """Get batches expiring within specified days"""
        try:
            current_time = datetime.utcnow()
            future_date = current_time + timedelta(days=days_ahead)
            
            logger.info(f"Checking for batches expiring between {current_time} and {future_date}")
            
            # First, let's get all active batches and filter in Python to debug
            all_active_batches = list(self.batch_collection.find({
                'status': 'active',
                'quantity_remaining': {'$gt': 0},
                'expiry_date': {'$exists': True, '$ne': None}
            }))
            
            logger.info(f"Found {len(all_active_batches)} active batches with expiry dates")
            
            expiring_batches = []
            
            for batch in all_active_batches:
                try:
                    expiry_date = batch.get('expiry_date')
                    if not expiry_date:
                        continue
                    
                    # Convert string dates to datetime for comparison
                    if isinstance(expiry_date, str):
                        from dateutil import parser
                        expiry_date = parser.parse(expiry_date)
                    
                    # Check if batch expires within the timeframe
                    if current_time < expiry_date <= future_date:
                        # Get product info
                        product = self.product_collection.find_one({'_id': batch['product_id']})
                        if product:
                            batch['product_info'] = product
                            expiring_batches.append(batch)
                            logger.info(f"Batch {batch['_id']} expires {expiry_date}, adding to results")
                    else:
                        logger.info(f"Batch {batch['_id']} expires {expiry_date}, outside timeframe")
                        
                except Exception as batch_error:
                    logger.error(f"Error processing batch {batch.get('_id')}: {str(batch_error)}")
                    continue
            
            # Sort by expiry date
            expiring_batches.sort(key=lambda x: x.get('expiry_date'))
            
            logger.info(f"Found {len(expiring_batches)} expiring batches")
            return expiring_batches
            
        except Exception as e:
            logger.error(f"Error getting expiring batches: {str(e)}")
            raise Exception(f"Error getting expiring batches: {str(e)}")

    def check_and_alert_expiring_batches(self, days_ahead=7):
        """Check for expiring batches and send alerts"""
        try:
            logger.info(f"Checking for batches expiring within {days_ahead} days")
            
            expiring_batches = self.get_expiring_batches(days_ahead)
            logger.info(f"Found {len(expiring_batches)} expiring batches")
            
            alerts_sent = 0
            for batch_info in expiring_batches:
                try:
                    batch = batch_info
                    product_info = batch_info.get('product_info', {})
                    
                    # Calculate days until expiry properly
                    expiry_date = batch.get('expiry_date')
                    if not expiry_date:
                        continue
                        
                    if isinstance(expiry_date, str):
                        from dateutil import parser
                        expiry_date = parser.parse(expiry_date)
                    
                    days_until_expiry = (expiry_date - datetime.utcnow()).days
                    
                    logger.info(f"Sending alert for batch {batch['_id']}, expires in {days_until_expiry} days")
                    
                    self._send_batch_notification(
                        'expiry_warning',
                        product_info.get('product_name', 'Unknown Product'),
                        {
                            'batch_id': batch['_id'],
                            'batch_number': batch.get('batch_number', 'Unknown'),
                            'expiry_date': expiry_date.isoformat(),
                            'days_until_expiry': days_until_expiry,
                            'quantity_remaining': batch.get('quantity_remaining', 0)
                        }
                    )
                    alerts_sent += 1
                    
                except Exception as batch_error:
                    logger.error(f"Error processing batch alert: {str(batch_error)}")
                    continue
            
            logger.info(f"Total alerts sent: {alerts_sent}")
            return alerts_sent
            
        except Exception as e:
            logger.error(f"Error checking expiring batches: {str(e)}")
            raise Exception(f"Error checking expiring batches: {str(e)}")

    # ================================================================
    # BATCH QUERIES AND REPORTING
    # ================================================================
    
    def get_all_batches(self, filters=None):
        """Get all batches with optional filters"""
        try:
            query = {}
            
            if filters:
                if filters.get('product_id'):
                    query['product_id'] = filters['product_id']
                
                if filters.get('status'):
                    query['status'] = filters['status']
                
                if filters.get('supplier_id'):
                    query['supplier_id'] = filters['supplier_id']
                
                if filters.get('expiring_soon'):
                    days = filters.get('days_ahead', 30)
                    future_date = datetime.utcnow() + timedelta(days=days)
                    query['expiry_date'] = {'$lte': future_date}
            
            batches = list(self.batch_collection.find(query).sort('expiry_date', 1))
            return batches
        
        except Exception as e:
            raise Exception(f"Error getting batches: {str(e)}")

    def get_batch_by_id(self, batch_id):
        """Get batch by ID"""
        try:
            batch = self.batch_collection.find_one({'_id': batch_id})
            return batch
        
        except Exception as e:
            raise Exception(f"Error getting batch: {str(e)}")

    def get_products_with_expiry_summary(self):
        """Get products with their expiry summary information"""
        try:
            pipeline = [
                {
                    '$match': {
                        'isDeleted': {'$ne': True}
                    }
                },
                {
                    '$project': {
                        '_id': 1,
                        'product_name': 1,
                        'SKU': 1,
                        'total_stock': 1,
                        'oldest_batch_expiry': 1,
                        'newest_batch_expiry': 1,
                        'expiry_alert': 1,
                        'low_stock_threshold': 1
                    }
                },
                {
                    '$sort': {'oldest_batch_expiry': 1}
                }
            ]
            
            products = list(self.product_collection.aggregate(pipeline))
            return products
        
        except Exception as e:
            raise Exception(f"Error getting products with expiry summary: {str(e)}")
        
    def update_batch_quantity(self, batch_id, quantity_used, adjustment_type="correction", adjusted_by=None, notes=None):
        """Update batch quantity when stock is sold/used - ENHANCED VERSION"""
        try:
            batch = self.batch_collection.find_one({'_id': batch_id})
            if not batch:
                raise Exception(f"Batch with ID {batch_id} not found")
            
            new_quantity = max(0, batch['quantity_remaining'] - quantity_used)
            new_status = 'depleted' if new_quantity == 0 else 'active'
            
            current_time = datetime.utcnow()
            
            # Enhanced usage history entry (NO reason field)
            usage_entry = {
                'timestamp': current_time,
                'quantity_used': quantity_used,
                'remaining_after': new_quantity,
                'adjustment_type': adjustment_type,  # sale, damage, theft, correction, spoilage, return, shrinkage
                'adjusted_by': adjusted_by,
                'approved_by': None,
                'notes': notes,
                'source': 'manual_adjustment'
            }
            
            # Update batch
            result = self.batch_collection.update_one(
                {'_id': batch_id},
                {
                    '$set': {
                        'quantity_remaining': new_quantity,
                        'status': new_status,
                        'updated_at': current_time
                    },
                    '$push': {
                        'usage_history': usage_entry
                    }
                }
            )
            
            if result.modified_count > 0:
                self.update_product_expiry_summary(batch['product_id'])
                
                # Send notification if batch is depleted
                if new_status == 'depleted':
                    product = self.product_collection.find_one({'_id': batch['product_id']})
                    product_name = product.get('product_name', 'Unknown Product') if product else 'Unknown Product'
                    
                    self._send_batch_notification(
                        'batch_depleted',
                        product_name,
                        {
                            'batch_id': batch_id,
                            'batch_number': batch['batch_number']
                        }
                    )
                
                return self.batch_collection.find_one({'_id': batch_id})
            
            return None

        except Exception as e:
            raise Exception(f"Error updating batch quantity: {str(e)}")

    # ================================================================
    # INTEGRATION WITH SALES
    # ================================================================
    
    def process_sale_fifo(self, product_id, quantity_sold):
        """Process a sale using FIFO (First In, First Out) logic"""
        try:
            # Get active batches sorted by expiry date (FIFO)
            active_batches = list(self.batch_collection.find({
                'product_id': product_id,
                'status': 'active',
                'quantity_remaining': {'$gt': 0}
            }).sort('expiry_date', 1))
            
            if not active_batches:
                raise Exception(f"No active batches available for product {product_id}")
            
            remaining_to_sell = quantity_sold
            batches_used = []
            
            for batch in active_batches:
                if remaining_to_sell <= 0:
                    break
                
                quantity_from_batch = min(remaining_to_sell, batch['quantity_remaining'])
                
                # Update batch quantity with SALE type (NO reason parameter)
                self.update_batch_quantity(
                    batch['_id'], 
                    quantity_from_batch,
                    adjustment_type="sale",
                    adjusted_by=None,
                    notes="POS sale transaction"
                )
                
                batches_used.append({
                    'batch_id': batch['_id'],
                    'batch_number': batch['batch_number'],
                    'quantity_used': quantity_from_batch,
                    'cost_price': batch['cost_price'],
                    'expiry_date': batch['expiry_date']
                })
                
                remaining_to_sell -= quantity_from_batch
            
            if remaining_to_sell > 0:
                raise Exception(f"Insufficient stock: {remaining_to_sell} units could not be fulfilled")
            
            return batches_used
        
        except Exception as e:
            raise Exception(f"Error processing FIFO sale: {str(e)}")

    def process_batch_adjustment(self, product_id, quantity_used, adjustment_type, adjusted_by=None, notes=None):
        """Process a batch adjustment using FIFO logic"""
        try:
            logger.info(f"Processing batch adjustment for product {product_id}: {quantity_used} units, type: {adjustment_type}")
            
            # Get active batches sorted by expiry date (FIFO)
            active_batches = list(self.batch_collection.find({
                'product_id': product_id,
                'status': 'active',
                'quantity_remaining': {'$gt': 0}
            }).sort('expiry_date', 1))
            
            if not active_batches:
                raise Exception(f"No active batches available for product {product_id}")
            
            remaining_to_adjust = quantity_used
            batches_adjusted = []
            
            for batch in active_batches:
                if remaining_to_adjust <= 0:
                    break
                
                quantity_from_batch = min(remaining_to_adjust, batch['quantity_remaining'])
                
                logger.info(f"Adjusting batch {batch['_id']}: {quantity_from_batch} units")
                
                # Update batch quantity with the specified adjustment type
                self.update_batch_quantity(
                    batch['_id'], 
                    quantity_from_batch,
                    adjustment_type=adjustment_type,
                    adjusted_by=adjusted_by,
                    notes=notes
                )
                
                batches_adjusted.append({
                    'batch_id': batch['_id'],
                    'batch_number': batch['batch_number'],
                    'quantity_adjusted': quantity_from_batch,
                    'adjustment_type': adjustment_type,
                    'remaining_in_batch': batch['quantity_remaining'] - quantity_from_batch
                })
                
                remaining_to_adjust -= quantity_from_batch
            
            if remaining_to_adjust > 0:
                raise Exception(f"Insufficient stock: {remaining_to_adjust} units could not be adjusted")
            
            logger.info(f"Successfully adjusted {quantity_used} units across {len(batches_adjusted)} batches")
            
            return {
                'product_id': product_id,
                'total_adjusted': quantity_used,
                'adjustment_type': adjustment_type,
                'batches_affected': batches_adjusted,
                'adjusted_by': adjusted_by
            }
        
        except Exception as e:
            logger.error(f"Error processing batch adjustment: {str(e)}")
            raise Exception(f"Error processing batch adjustment: {str(e)}")
    # ================================================================
    # MAINTENANCE AND CLEANUP
    # ================================================================
    
    def mark_expired_batches(self):
        """Mark expired batches as expired"""
        try:
            current_time = datetime.utcnow()
            
            result = self.batch_collection.update_many(
                {
                    'status': 'active',
                    'expiry_date': {'$lt': current_time}
                },
                {
                    '$set': {
                        'status': 'expired',
                        'updated_at': current_time
                    }
                }
            )
            
            # Update product expiry summaries for affected products
            expired_batches = list(self.batch_collection.find({
                'status': 'expired',
                'updated_at': current_time
            }))
            
            affected_products = set(batch['product_id'] for batch in expired_batches)
            
            for product_id in affected_products:
                self.update_product_expiry_summary(product_id)
            
            return result.modified_count
        
        except Exception as e:
            raise Exception(f"Error marking expired batches: {str(e)}")
        
