from datetime import datetime
from bson import ObjectId
from ...database import db_manager
from notifications.services import notification_service
from .promotionCon import PromoConnection
from ..batch_service import BatchService
from ..product_service import ProductService
import logging

logger = logging.getLogger(__name__)

class SalesService:
    """
    Unified service that combines POS transactions and sales logging
    Works with both PromoConnection and SalesLogService
    """
    def __init__(self):
        self.db = db_manager.get_database()
        self.sales_collection = self.db.sales  # POS transactions
        self.sales_log_collection = self.db.sales_log  # Imported/manual sales
        self.products_collection = self.db.products
        self.promotions_collection = self.db.promotions
        self.customers_collection = self.db.customers
        self.users_collection = self.db.users
        self.promo_connection = PromoConnection()
        
        # ✅ Enhanced services for FIFO and loyalty points
        self.batch_service = BatchService()
        self.product_service = ProductService()

    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization - Enhanced version"""
        if document is None:
            return document
        
        if isinstance(document, list):
            return [self.convert_object_id(item) for item in document]
        
        if isinstance(document, dict):
            converted = {}
            for key, value in document.items():
                if isinstance(value, ObjectId):
                    converted[key] = str(value)
                elif isinstance(value, (dict, list)):
                    converted[key] = self.convert_object_id(value)
                else:
                    converted[key] = value
            return converted
        
        if isinstance(document, ObjectId):
            return str(document)
        
        return document
    
    def create_unified_sale(self, sale_data, source='pos'):
        """
        Create a sale record that works for both POS and manual entry
        
        Args:
            sale_data: Sale information
            source: 'pos' for POS transactions, 'manual' for manual entry, 'csv' for imports
        """
        try:
            if source == 'pos':
                # Use POS format (your existing PromoConnection.create_sales)
                return self._create_pos_sale(sale_data)
            else:
                # Use sales log format (your existing SalesLogService.create_invoice)
                return self._create_sales_log(sale_data, source)
                
        except Exception as e:
            raise Exception(f"Error creating unified sale: {str(e)}")

    def _create_pos_sale(self, sale_data):
        """Create POS-style sale record"""
        try:
            sales_record = {
                'sale_id': str(ObjectId()),
                'items': sale_data['items'],
                'total_amount': sale_data['total_amount'],
                'total_discount': sale_data.get('total_discount', 0),
                'final_amount': sale_data.get('final_amount', sale_data['total_amount']),
                'promotion_applied': sale_data.get('promotion_applied', None),
                'payment_method': sale_data.get('payment_method', 'cash'),
                'cashier_id': sale_data.get('cashier_id', None),
                'customer_id': sale_data.get('customer_id', None),
                'transaction_date': datetime.utcnow(),
                'status': 'completed',
                'source': 'pos',
                'created_at': datetime.utcnow(),
                'last_updated': datetime.utcnow()
            }

            result = self.sales_collection.insert_one(sales_record)
            sales_record['_id'] = str(result.inserted_id)

            # Send notification
            self._send_sale_notification(sales_record, 'pos_sale_created')

            return {
                'success': True,
                'message': 'POS sale created successfully',
                'data': sales_record
            }

        except Exception as e:
            raise Exception(f"Error creating POS sale: {str(e)}")

    def _create_sales_log(self, sale_data, source):
        """Create sales log style record"""
        try:
            # Convert POS format to sales log format if needed
            if 'items' in sale_data and isinstance(sale_data['items'], list):
                # Convert POS items format to sales log item_list format
                item_list = []
                for item in sale_data['items']:
                    item_list.append({
                        'item_code': item.get('product_id', ''),
                        'item_name': item.get('product_name', ''),
                        'quantity': item.get('quantity', 0),
                        'unit_price': item.get('price', 0),
                        'total_price': item.get('price', 0) * item.get('quantity', 0),
                        'unit_of_measure': item.get('unit', 'pc'),
                        'tax_amount': 0,
                        'imported_from_csv': source == 'csv'
                    })
            else:
                item_list = sale_data.get('item_list', [])

            sales_log_record = {
                'customer_id': ObjectId(sale_data['customer_id']) if sale_data.get('customer_id') else None,
                'user_id': ObjectId(sale_data['user_id']) if sale_data.get('user_id') else None,
                'transaction_date': sale_data.get('transaction_date', datetime.utcnow()),
                'total_amount': sale_data['total_amount'],
                'status': sale_data.get('status', 'completed'),
                'payment_method': sale_data.get('payment_method', 'cash'),
                'sales_type': sale_data.get('sales_type', 'retail'),
                'tax_rate': sale_data.get('tax_rate', 0),
                'tax_amount': sale_data.get('tax_amount', 0),
                'is_taxable': sale_data.get('is_taxable', False),
                'notes': sale_data.get('notes', ''),
                'item_list': item_list,
                'source': source,
                'sync_logs': sale_data.get('sync_logs', [])
            }

            result = self.sales_log_collection.insert_one(sales_log_record)
            sales_log_record['_id'] = str(result.inserted_id)

            # Send notification
            self._send_sale_notification(sales_log_record, f'{source}_sale_created')

            return {
                'success': True,
                'message': f'{source.title()} sale logged successfully',
                'data': self.convert_object_id(sales_log_record)
            }

        except Exception as e:
            raise Exception(f"Error creating sales log: {str(e)}")

    def _send_sale_notification(self, sale_record, notification_type):
        """Send notification for sale creation"""
        try:
            total_amount = sale_record.get('total_amount', 0)
            source = sale_record.get('source', 'unknown')
            
            if notification_type == 'pos_sale_created':
                title = "POS Sale Completed"
                message = f"New POS transaction completed for ₱{total_amount}"
                priority = "low"
            elif notification_type == 'csv_sale_created':
                title = "CSV Sale Imported"
                message = f"Sale imported from CSV for ₱{total_amount}"
                priority = "low"
            elif notification_type == 'manual_sale_created':
                title = "Manual Sale Entered"
                message = f"Manual sale entry for ₱{total_amount}"
                priority = "low"
            else:
                title = "Sale Created"
                message = f"New sale recorded for ₱{total_amount}"
                priority = "low"

            notification_service.create_notification(
                title=title,
                message=message,
                priority=priority,
                notification_type="sales",
                metadata={
                    "sale_id": str(sale_record.get('_id', '')),
                    "total_amount": total_amount,
                    "source": source,
                    "payment_method": sale_record.get('payment_method', ''),
                    "action_type": notification_type
                }
            )

        except Exception as notification_error:
            print(f"Failed to create sale notification: {notification_error}")

    def get_pos_sale_by_id(self, sale_id):
        """Get a POS sale by ID from sales collection only"""
        try:
            # Convert string to ObjectId
            if isinstance(sale_id, str):
                object_id = ObjectId(sale_id)
            else:
                object_id = sale_id
            
            # Correct MongoDB query syntax
            sale = self.sales_collection.find_one({'_id': object_id})
            
            if sale:
                return self.convert_object_id(sale)
            return None
            
        except Exception as e:
            raise Exception(f"Error fetching POS sale by ID: {str(e)}")
    
    def get_recent_sales(self, limit=10):
        """Get recent sales from both POS and sales_log - Fixed version"""
        try:
            all_sales = []
            
            # Get POS sales
            pos_sales = list(self.sales_collection.find({}).sort('transaction_date', -1).limit(limit))
            for sale in pos_sales:
                sale['collection_source'] = 'sales'
                all_sales.append(self.convert_object_id(sale))  # ✅ Fix ObjectId
            
            # Get sales_log sales  
            log_sales = list(self.sales_log_collection.find({}).sort('transaction_date', -1).limit(limit))
            for sale in log_sales:
                sale['collection_source'] = 'sales_log'
                all_sales.append(self.convert_object_id(sale))  # ✅ Fix ObjectId
            
            # Sort by date and limit
            all_sales.sort(key=lambda x: x['transaction_date'], reverse=True)
            return all_sales[:limit]
            
        except Exception as e:
            raise Exception(f"Error fetching recent sales: {str(e)}")
        
    def get_sales_by_date_range(self, start_date, end_date, source=None):
        """Create sales log style record"""
        try:
           
            return

        except Exception as e:
            raise Exception(f"Error Fetching sale by ID: {str(e)}")
        
    def get_sales_log_by_id(self, log_id):
        """
        ✅ MISSING METHOD: Get sales log by ID from sales_log collection
        This is what SalesLogService.get_invoice_by_id() is trying to call
        """
        try:
            if isinstance(log_id, str):
                log_id = ObjectId(log_id)
            
            log_doc = self.sales_log_collection.find_one({"_id": log_id})
            
            if log_doc:
                return self.convert_object_id(log_doc)
            return None
            
        except Exception as e:
            raise Exception(f"Error retrieving sales log by ID: {str(e)}")

    def update_sales_log(self, log_id, update_data):
        """
        ✅ MISSING METHOD: Update an existing sales log
        """
        try:
            if isinstance(log_id, str):
                log_id = ObjectId(log_id)
            
            # Remove _id from update_data if present
            update_data.pop('_id', None)
            
            result = self.sales_log_collection.update_one(
                {"_id": log_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return self.get_sales_log_by_id(log_id)
            else:
                return None
                
        except Exception as e:
            raise Exception(f"Error updating sales log: {str(e)}")

    def delete_sales_log(self, log_id):
        """
        ✅ MISSING METHOD: Delete a sales log
        """
        try:
            if isinstance(log_id, str):
                log_id = ObjectId(log_id)
            
            result = self.sales_log_collection.delete_one({"_id": log_id})
            
            return result.deleted_count > 0
            
        except Exception as e:
            raise Exception(f"Error deleting sales log: {str(e)}")

    def get_all_sales_logs(self, limit=100, skip=0):
        """
        ✅ MISSING METHOD: Get all sales logs with pagination
        """
        try:
            logs = list(self.sales_log_collection.find().skip(skip).limit(limit))
            
            # Convert ObjectIds to strings
            for log in logs:
                self.convert_object_id(log)
            
            return logs
            
        except Exception as e:
            raise Exception(f"Error retrieving sales logs: {str(e)}")

    def get_sales_logs_paginated(self, page=1, page_size=50, filters=None):
        """
        ✅ MISSING METHOD: Get sales logs with advanced pagination and filtering
        """
        try:
            skip = (page - 1) * page_size
            query = {}
            
            # Apply filters if provided
            if filters:
                if filters.get('start_date') and filters.get('end_date'):
                    query['transaction_date'] = {
                        '$gte': filters['start_date'],
                        '$lte': filters['end_date']
                    }
                if filters.get('sales_type'):
                    query['sales_type'] = filters['sales_type']
                if filters.get('source'):
                    query['source'] = filters['source']
                if filters.get('payment_method'):
                    query['payment_method'] = filters['payment_method']
                if filters.get('customer_id'):
                    try:
                        query['customer_id'] = ObjectId(filters['customer_id'])
                    except:
                        pass  # Skip invalid customer_id
            
            # Get logs with pagination
            logs = list(self.sales_log_collection.find(query).skip(skip).limit(page_size))
            total_count = self.sales_log_collection.count_documents(query)
            total_pages = (total_count + page_size - 1) // page_size
            
            # Convert ObjectIds
            for log in logs:
                self.convert_object_id(log)
            
            return {
                "data": logs,
                "pagination": {
                    "current_page": page,
                    "page_size": page_size,
                    "total_records": total_count,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                },
                "filters_applied": filters or {}
            }
            
        except Exception as e:
            raise Exception(f"Error retrieving paginated sales logs: {str(e)}")

    def get_sales_logs_for_export(self, filters=None):
        """
        ✅ MISSING METHOD: Get sales logs for export with filtering
        """
        try:
            query = {}
            
            # Apply filters if provided
            if filters:
                # Date range filtering
                if filters.get('start_date') and filters.get('end_date'):
                    try:
                        from django.utils.dateparse import parse_date
                        from datetime import time
                        
                        # Parse dates
                        if isinstance(filters['start_date'], str):
                            start_date = parse_date(filters['start_date'])
                        else:
                            start_date = filters['start_date']
                        
                        if isinstance(filters['end_date'], str):
                            end_date = parse_date(filters['end_date'])
                        else:
                            end_date = filters['end_date']
                        
                        if start_date and end_date:
                            start_datetime = datetime.combine(start_date, time.min)
                            end_datetime = datetime.combine(end_date, time.max)
                            query['transaction_date'] = {
                                '$gte': start_datetime, 
                                '$lte': end_datetime
                            }
                    except Exception as date_error:
                        print(f"Date parsing error: {date_error}")
                
                # Other filters
                if filters.get('sales_type'):
                    query['sales_type'] = filters['sales_type']
                if filters.get('payment_method'):
                    query['payment_method'] = filters['payment_method']
                if filters.get('status'):
                    query['status'] = filters['status']
                if filters.get('source'):
                    query['source'] = filters['source']
                if filters.get('customer_id'):
                    try:
                        query['customer_id'] = ObjectId(filters['customer_id'])
                    except:
                        pass
            
            print(f"Export query: {query}")
            
            # Get transactions with a reasonable limit for export
            transactions = list(self.sales_log_collection.find(query).limit(10000))
            
            print(f"Found {len(transactions)} transactions for export")
            
            # Convert ObjectIds to strings
            for transaction in transactions:
                self.convert_object_id(transaction)
            
            return transactions
            
        except Exception as e:
            print(f"Error in get_sales_logs_for_export: {str(e)}")
            raise Exception(f"Error retrieving sales logs for export: {str(e)}")

    def get_sales_by_date_range(self, start_date, end_date, source=None):
        """
        ✅ COMPLETE THIS METHOD: Get sales by date range
        """
        try:
            query = {
                'transaction_date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            
            if source:
                query['source'] = source
            
            # Get from both collections
            pos_sales = list(self.sales_collection.find(query))
            log_sales = list(self.sales_log_collection.find(query))
            
            # Combine and convert
            all_sales = []
            
            for sale in pos_sales:
                sale['collection_source'] = 'sales'
                all_sales.append(self.convert_object_id(sale))
            
            for sale in log_sales:
                sale['collection_source'] = 'sales_log'
                all_sales.append(self.convert_object_id(sale))
            
            # Sort by date
            all_sales.sort(key=lambda x: x['transaction_date'], reverse=True)
            
            return all_sales
            
        except Exception as e:
            raise Exception(f"Error fetching sales by date range: {str(e)}")

    # ================================================================
    # ENHANCED POS SALES WITH FIFO INTEGRATION (Backward Compatible)
    # ================================================================
    
    def generate_sale_id(self):
        """Generate sequential SALE-###### ID for enhanced POS sales"""
        try:
            pipeline = [
                {'$match': {'_id': {'$regex': '^SALE-'}}},
                {'$project': {
                    'numericPart': {'$toInt': {'$substr': ['$_id', 5, -1]}}
                }},
                {'$sort': {'numericPart': -1}},
                {'$limit': 1}
            ]
            
            result = list(self.sales_collection.aggregate(pipeline))
            next_number = result[0]['numericPart'] + 1 if result else 1
            
            return f"SALE-{next_number:06d}"
        except Exception:
            count = self.sales_collection.count_documents({}) + 1
            return f"SALE-{count:06d}"

    def calculate_loyalty_points_earned(self, subtotal_after_discount):
        """
        Calculate loyalty points earned (20% of subtotal after discount)
        
        Args:
            subtotal_after_discount: Subtotal after points redemption
        
        Returns:
            int: Points to be earned
        """
        return int(subtotal_after_discount * 0.20)

    def calculate_points_discount(self, points_to_redeem):
        """
        Convert points to discount amount
        4 points = ₱1 discount
        
        Args:
            points_to_redeem: Number of points customer wants to use
        
        Returns:
            float: Discount amount in pesos
        """
        return points_to_redeem / 4.0

    def validate_points_redemption(self, customer_id, points_to_redeem, subtotal):
        """
        Validate loyalty points redemption
        
        Args:
            customer_id: Customer ID
            points_to_redeem: Points customer wants to use
            subtotal: Sale subtotal
        
        Returns:
            dict: {'valid': bool, 'error': str}
        """
        try:
            if points_to_redeem == 0:
                return {'valid': True, 'error': None}
            
            # Minimum redemption: 40 points (₱10)
            if points_to_redeem < 40:
                return {
                    'valid': False,
                    'error': 'Minimum redemption is 40 points (₱10)'
                }
            
            # Get customer
            customer = self.customers_collection.find_one({'_id': customer_id})
            
            if not customer:
                return {'valid': False, 'error': 'Customer not found'}
            
            # Check if customer has enough points
            available_points = customer.get('loyalty_points', 0)
            
            if available_points < points_to_redeem:
                return {
                    'valid': False,
                    'error': f'Insufficient points. Available: {available_points}, Requested: {points_to_redeem}'
                }
            
            # Check max discount: min(₱20, 20% of subtotal)
            points_discount = self.calculate_points_discount(points_to_redeem)
            max_discount = min(20, subtotal * 0.20)
            
            if points_discount > max_discount:
                max_points = int(max_discount * 4)  # Convert back to points
                return {
                    'valid': False,
                    'error': f'Points discount exceeds cap. Maximum: {max_points} points (₱{max_discount:.2f})'
                }
            
            return {'valid': True, 'error': None}
            
        except Exception as e:
            logger.error(f"Points validation error: {str(e)}")
            return {'valid': False, 'error': str(e)}

    def deduct_customer_points(self, customer_id, points_to_deduct, sale_id):
        """
        Deduct loyalty points from customer balance
        
        Args:
            customer_id: Customer ID
            points_to_deduct: Points to deduct
            sale_id: Sale ID for transaction history
        """
        try:
            customer = self.customers_collection.find_one({'_id': customer_id})
            
            if not customer:
                raise ValueError(f"Customer {customer_id} not found")
            
            current_balance = customer.get('loyalty_points', 0)
            new_balance = current_balance - points_to_deduct
            
            # Create points transaction
            points_transaction = {
                'transaction_id': sale_id,
                'transaction_type': 'redeemed',
                'points': -points_to_deduct,
                'balance_before': current_balance,
                'balance_after': new_balance,
                'description': f"Redeemed {points_to_deduct} points on sale {sale_id}",
                'created_at': datetime.utcnow()
            }
            
            # Update customer
            self.customers_collection.update_one(
                {'_id': customer_id},
                {
                    '$set': {'loyalty_points': new_balance},
                    '$push': {'points_transactions': points_transaction}
                }
            )
            
            logger.info(f"Deducted {points_to_deduct} points from {customer_id}")
            
        except Exception as e:
            logger.error(f"Error deducting points: {str(e)}")
            raise

    def award_loyalty_points(self, customer_id, points_to_award, sale_id, sale_amount):
        """
        Award loyalty points to customer when sale is completed
        
        Args:
            customer_id: Customer ID
            points_to_award: Points to award
            sale_id: Sale ID
            sale_amount: Sale subtotal after discount
        """
        try:
            customer = self.customers_collection.find_one({'_id': customer_id})
            
            if not customer:
                raise ValueError(f"Customer {customer_id} not found")
            
            current_balance = customer.get('loyalty_points', 0)
            new_balance = current_balance + points_to_award
            
            # Points expire in 12 months
            expires_at = datetime.utcnow() + timedelta(days=365)
            
            # Create points transaction
            points_transaction = {
                'transaction_id': sale_id,
                'transaction_type': 'earned',
                'points': points_to_award,
                'balance_before': current_balance,
                'balance_after': new_balance,
                'description': f"Earned from sale {sale_id} (₱{sale_amount:.2f} purchase)",
                'earned_at': datetime.utcnow(),
                'expires_at': expires_at,
                'status': 'active',
                'created_at': datetime.utcnow()
            }
            
            # Update customer
            self.customers_collection.update_one(
                {'_id': customer_id},
                {
                    '$set': {
                        'loyalty_points': new_balance,
                        'last_purchase': datetime.utcnow()
                    },
                    '$push': {'points_transactions': points_transaction}
                }
            )
            
            logger.info(f"Awarded {points_to_award} points to {customer_id}")
            
        except Exception as e:
            logger.error(f"Error awarding points: {str(e)}")
            raise

    def create_enhanced_pos_sale(self, sale_data, cashier_id):
        """
        Create a new POS sale transaction with FIFO batch deduction and loyalty points
        
        Args:
            sale_data: Dictionary containing sale information
            cashier_id: ID of the cashier (USER-#### format)
        
        Returns:
            Dictionary with success status and created sale data
        """
        try:
            # Generate sale ID
            sale_id = self.generate_sale_id()
            transaction_date = datetime.utcnow()
            
            print(f"\n{'='*60}")
            print(f"🛒 Creating Enhanced POS Sale: {sale_id}")
            print(f"   Cashier: {cashier_id}")
            print(f"   Items: {len(sale_data.get('items', []))}")
            print(f"{'='*60}\n")
            
            # Get customer details if provided
            customer_id = sale_data.get('customer_id')
            customer = None
            if customer_id:
                customer = self.customers_collection.find_one({'_id': customer_id})
                if not customer:
                    raise ValueError(f"Customer {customer_id} not found")
            
            # Step 1: Calculate initial subtotal
            print("Step 1: Calculating pricing...")
            subtotal = 0
            items_with_prices = []
            
            for item in sale_data.get('items', []):
                product = self.products_collection.find_one({'_id': item['product_id']})
                
                if not product:
                    raise ValueError(f"Product {item['product_id']} not found")
                
                unit_price = product.get('selling_price', 0)
                quantity = item['quantity']
                item_subtotal = unit_price * quantity
                
                items_with_prices.append({
                    'product_id': item['product_id'],
                    'product_name': product.get('product_name'),
                    'sku': product.get('SKU'),
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'subtotal': item_subtotal,
                    'is_taxable': product.get('is_taxable', True)
                })
                
                subtotal += item_subtotal
            
            print(f"   Subtotal: ₱{subtotal:.2f}")
            
            # Step 2: Apply points discount (if any)
            points_to_redeem = sale_data.get('points_to_redeem', 0)
            points_discount = 0
            
            if points_to_redeem > 0 and customer_id:
                print(f"Step 2: Applying points discount ({points_to_redeem} points)...")
                
                # Validate points redemption
                points_validation = self.validate_points_redemption(
                    customer_id, 
                    points_to_redeem, 
                    subtotal
                )
                
                if not points_validation['valid']:
                    raise ValueError(points_validation['error'])
                
                points_discount = self.calculate_points_discount(points_to_redeem)
                
                # Deduct points from customer
                self.deduct_customer_points(customer_id, points_to_redeem, sale_id)
                
                print(f"   Points discount: ₱{points_discount:.2f}")
            
            subtotal_after_discount = subtotal - points_discount
            print(f"   Subtotal after discount: ₱{subtotal_after_discount:.2f}")
            
            # Step 3: Calculate loyalty points to be earned
            loyalty_points_earned = self.calculate_loyalty_points_earned(subtotal_after_discount)
            print(f"Step 3: Loyalty points to earn: {loyalty_points_earned} points\n")
            
            # Step 4: Build sale record
            print("Step 4: Processing sale items with FIFO...\n")
            
            sale_record = {
                '_id': sale_id,
                'cashier_id': cashier_id,
                'customer_id': customer_id,
                'customer_name': customer.get('full_name') if customer else None,
                'transaction_date': transaction_date,
                'items': [],  # Will be populated with batch tracking
                'subtotal': round(subtotal, 2),
                'points_redeemed': points_to_redeem,
                'points_discount': round(points_discount, 2),
                'subtotal_after_discount': round(subtotal_after_discount, 2),
                'total_amount': round(subtotal_after_discount, 2),
                'payment_method': sale_data.get('payment_method', 'cash'),
                'status': 'completed',
                'source': 'pos',
                'created_at': transaction_date,
                'updated_at': transaction_date,
                'is_voided': False,
                'loyalty_points_earned': loyalty_points_earned,
                'loyalty_points_used': points_to_redeem,
                'points_awarded': False
            }
            
            # Step 5: Process each item with FIFO batch deduction
            for item in items_with_prices:
                product_id = item['product_id']
                quantity_needed = item['quantity']
                
                print(f"📦 Processing: {item['product_name']} ({product_id}) x{quantity_needed}")
                
                # Check stock availability
                stock_check = self.batch_service.check_batch_availability(
                    product_id,
                    quantity_needed
                )
                
                if not stock_check['available']:
                    raise ValueError(
                        f"Insufficient stock for {item['product_name']}. "
                        f"Available: {stock_check['total_stock']}, Requested: {quantity_needed}"
                    )
                
                # ✅ PREPARE TRANSACTION INFO FOR USAGE_HISTORY
                transaction_info = {
                    'transaction_id': sale_id,
                    'adjusted_by': cashier_id,
                    'source': 'pos_sale'
                }
                
                # ✅ Deduct from batches using FIFO with transaction tracking
                batch_deductions = self.batch_service.deduct_stock_fifo(
                    product_id,
                    quantity_needed,
                    transaction_date,
                    transaction_info=transaction_info
                )
                
                # Add batches_used to item
                item['batches_used'] = batch_deductions
                
                # Add item to sale
                sale_record['items'].append(item)
                
                # Update product total stock (cached)
                product = self.products_collection.find_one({'_id': product_id})
                new_total_stock = product.get('stock', 0) - quantity_needed
                
                self.products_collection.update_one(
                    {'_id': product_id},
                    {
                        '$set': {
                            'stock': new_total_stock,
                            'updated_at': transaction_date
                        }
                    }
                )
                
                print(f"   ✅ Stock updated: {product.get('stock')} → {new_total_stock}\n")
            
            # Step 6: Insert sale record
            self.sales_collection.insert_one(sale_record)
            
            # Step 7: Award loyalty points to customer
            if customer_id and loyalty_points_earned > 0:
                print(f"Step 5: Awarding {loyalty_points_earned} loyalty points...")
                
                self.award_loyalty_points(
                    customer_id,
                    loyalty_points_earned,
                    sale_id,
                    subtotal_after_discount
                )
                
                # Mark points as awarded
                self.sales_collection.update_one(
                    {'_id': sale_id},
                    {'$set': {'points_awarded': True}}
                )
                
                print("✅ Points awarded\n")
            
            print(f"{'='*60}")
            print(f"✅ Enhanced POS sale created successfully: {sale_id}")
            print(f"{'='*60}\n")
            
            # Send notification
            self._send_sale_notification(sale_record, 'enhanced_pos_sale_created')
            
            return {
                'success': True,
                'message': 'Enhanced POS sale created successfully',
                'data': {
                    'sale': sale_record,
                    'sale_id': sale_id,
                    'points_earned': loyalty_points_earned
                }
            }
            
        except Exception as e:
            print(f"❌ Error creating enhanced POS sale: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Error creating enhanced POS sale: {str(e)}")

    def void_enhanced_sale(self, sale_id, voided_by, reason):
        """
        Void an enhanced POS sale and restore stock to batches
        
        Args:
            sale_id: Sale ID (SALE-######)
            voided_by: User ID who voided the sale
            reason: Reason for voiding
        
        Returns:
            Updated sale document
        """
        try:
            print(f"\n{'='*60}")
            print(f"🚫 Voiding Enhanced Sale: {sale_id}")
            print(f"   Voided by: {voided_by}")
            print(f"   Reason: {reason}")
            print(f"{'='*60}\n")
            
            # Get sale
            sale = self.sales_collection.find_one({'_id': sale_id})
            
            if not sale:
                raise ValueError(f"Sale {sale_id} not found")
            
            if sale.get('is_voided'):
                raise ValueError(f"Sale {sale_id} is already voided")
            
            print("✅ Sale validation passed\n")
            
            # ✅ PREPARE TRANSACTION INFO FOR RESTORATION
            transaction_info = {
                'transaction_id': f"{sale_id}-VOID",
                'adjusted_by': voided_by,
                'reason': f"Sale voided: {reason}"
            }
            
            # Step 1: Restore stock to batches
            print("Step 1: Restoring stock to batches...\n")
            
            for item in sale.get('items', []):
                if 'batches_used' in item:
                    print(f"   Restoring: {item['product_name']} x{item['quantity']}")
                    
                    # ✅ Restore to batches using batch service with tracking
                    self.batch_service.restore_stock_to_batches(
                        item['batches_used'],
                        datetime.utcnow(),
                        transaction_info=transaction_info
                    )
                    
                    # Update product total stock
                    product = self.products_collection.find_one({'_id': item['product_id']})
                    
                    if product:
                        new_stock = product.get('stock', 0) + item['quantity']
                        
                        self.products_collection.update_one(
                            {'_id': item['product_id']},
                            {
                                '$set': {
                                    'stock': new_stock,
                                    'updated_at': datetime.utcnow()
                                }
                            }
                        )
                        
                        print(f"      Stock restored: {product.get('stock')} → {new_stock}")
            
            print("\n✅ Stock restored to batches\n")
            
            # Step 2: Refund loyalty points if used
            if sale.get('loyalty_points_used', 0) > 0 and sale.get('customer_id'):
                print(f"Step 2: Refunding {sale['loyalty_points_used']} loyalty points...")
                
                # Refund points (add them back)
                customer = self.customers_collection.find_one({'_id': sale['customer_id']})
                if customer:
                    current_balance = customer.get('loyalty_points', 0)
                    new_balance = current_balance + sale['loyalty_points_used']
                    
                    # Create refund transaction
                    refund_transaction = {
                        'transaction_id': f"{sale_id}-VOID",
                        'transaction_type': 'refunded',
                        'points': sale['loyalty_points_used'],
                        'balance_before': current_balance,
                        'balance_after': new_balance,
                        'description': f"Refunded {sale['loyalty_points_used']} points from voided sale {sale_id}",
                        'created_at': datetime.utcnow()
                    }
                    
                    self.customers_collection.update_one(
                        {'_id': sale['customer_id']},
                        {
                            '$set': {'loyalty_points': new_balance},
                            '$push': {'points_transactions': refund_transaction}
                        }
                    )
                
                print("✅ Points refunded\n")
            
            # Step 3: Update sale to voided
            print("Step 3: Updating sale status...")
            
            self.sales_collection.update_one(
                {'_id': sale_id},
                {
                    '$set': {
                        'is_voided': True,
                        'status': 'voided',
                        'voided_by': voided_by,
                        'voided_at': datetime.utcnow(),
                        'void_reason': reason,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            print("✅ Sale voided successfully\n")
            
            print(f"{'='*60}")
            print(f"✅ Sale {sale_id} voided successfully")
            print(f"{'='*60}\n")
            
            return self.sales_collection.find_one({'_id': sale_id})
            
        except Exception as e:
            logger.error(f"❌ Void sale failed: {str(e)}")
            raise