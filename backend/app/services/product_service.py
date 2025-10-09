import re 
from datetime import datetime
from ..database import db_manager
from ..models import Product
from notifications.services import notification_service
from .batch_service import BatchService
import logging

logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.product_collection = self.db.products
        self.category_collection = self.db.category
        self.supplier_collection = self.db.suppliers
        self.branch_collection = self.db.branches
        self.batch_service = BatchService()
        
    def validate_foreign_keys(self, product_data):
        """Validate that foreign key references exist - using string IDs"""
        # Validate category_id (string-based lookup)
        if 'category_id' in product_data and product_data['category_id']:
            category = self.category_collection.find_one({'_id': product_data['category_id']})
            if not category:
                raise ValueError(f"Category with ID {product_data['category_id']} not found")
        
        # Validate supplier_id (expecting SUPP-### format)
        if 'supplier_id' in product_data and product_data['supplier_id']:
            supplier = self.supplier_collection.find_one({'_id': product_data['supplier_id']})
            if not supplier:
                raise ValueError(f"Supplier with ID {product_data['supplier_id']} not found")
        
        # Validate branch_id (string-based lookup)
        if 'branch_id' in product_data and product_data['branch_id']:
            branch = self.branch_collection.find_one({'_id': product_data['branch_id']})
            if not branch:
                raise ValueError(f"Branch with ID {product_data['branch_id']} not found")
    
    def _send_product_notification(self, action_type, product_name, product_id=None, additional_metadata=None):
        """Centralized notification helper for product actions"""
        try:
            titles = {
                'created': "New Product Added",
                'updated': "Product Updated",
                'stock_updated': "Stock Updated", 
                'stock_low': "Low Stock Alert",
                'stock_out': "Out of Stock Alert",
                'soft_deleted': "Product Deleted",
                'hard_deleted': "Product Permanently Deleted", 
                'restored': "Product Restored",
                'bulk_created': "Bulk Products Created",
                'bulk_stock_updated': "Bulk Stock Updated",
                'import_completed': "Product Import Completed"
            }
            
            messages = {
                'created': f"Product '{product_name}' has been added to the system",
                'updated': f"Product '{product_name}' has been updated",
                'stock_updated': f"Stock updated for product '{product_name}'",
                'stock_low': f"Low stock warning for product '{product_name}'",
                'stock_out': f"Product '{product_name}' is out of stock",
                'soft_deleted': f"Product '{product_name}' has been moved to trash",
                'hard_deleted': f"Product '{product_name}' has been permanently removed",
                'restored': f"Product '{product_name}' has been restored from trash",
                'bulk_created': f"Bulk product creation completed",
                'bulk_stock_updated': f"Bulk stock update completed", 
                'import_completed': f"Product import completed"
            }
            
            # Use custom message if provided, otherwise use default
            if additional_metadata and 'custom_message' in additional_metadata:
                message = additional_metadata['custom_message']
            else:
                message = messages.get(action_type, f"Product action '{action_type}' completed for '{product_name}'")
            
            # Set priority and notification type based on action
            if action_type == 'stock_out':
                priority = "high"
                notification_type = "alert"
            elif action_type in ['stock_low', 'hard_deleted']:
                priority = "medium" 
                notification_type = "alert"
            elif action_type in ['soft_deleted', 'bulk_created', 'bulk_stock_updated']:
                priority = "medium"
                notification_type = "system"
            else:
                priority = "low"
                notification_type = "system"
            
            # Base metadata
            metadata = {
                "product_id": str(product_id) if product_id else "",
                "product_name": product_name,
                "action_type": f"product_{action_type}"
            }
            
            # Add additional metadata if provided
            if additional_metadata:
                # Remove custom_message from metadata since we used it for the message
                filtered_metadata = {k: v for k, v in additional_metadata.items() if k != 'custom_message'}
                metadata.update(filtered_metadata)
            
            notification_service.create_notification(
                title=titles.get(action_type, "Product Action"),
                message=message,
                priority=priority,
                notification_type=notification_type,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Failed to send product notification: {e}")
        
    def generate_product_id(self):
        """Generate sequential PROD-##### ID"""
        try:
            # Get the highest existing product ID number
            pipeline = [
                {'$match': {'_id': {'$regex': r'^PROD-\d{5}$'}}},
                {'$project': {
                    'id_number': {
                        '$toInt': {
                            '$substr': ['$_id', 5, -1]  # Extract number after "PROD-"
                        }
                    }
                }},
                {'$sort': {'id_number': -1}},
                {'$limit': 1}
            ]
            
            result = list(self.product_collection.aggregate(pipeline))
            next_number = (result[0]['id_number'] + 1) if result else 1
            
            return f"PROD-{next_number:05d}"
        
        except Exception:
            # Fallback: count all products + 1
            count = self.product_collection.count_documents({}) + 1
            return f"PROD-{count:05d}"

    def add_sync_log(self, source='cloud', status='synced', details=None):
        """Helper method to create sync log entries"""
        return {
            'last_updated': datetime.utcnow(),
            'source': source,  # 'local' or 'cloud'
            'status': status,  # 'synced', 'pending', 'failed'
            'details': details or {}
        }
    
    def _ensure_default_category_assignment(self, product_document):
        """Auto-assign to 'Uncategorized' > 'General' if no category specified"""
        if not product_document.get('category_id'):
            product_document['category_id'] = "UNCTGRY-001"
            product_document['subcategory_name'] = "General"
            logger.debug(f"Auto-assigned product to Uncategorized > General")
        
        # Ensure subcategory_name is set if category is provided
        if product_document.get('category_id') and not product_document.get('subcategory_name'):
            product_document['subcategory_name'] = "General"
            logger.debug(f"Auto-assigned subcategory to General")
        
        return product_document

    def update_sync_status(self, product_id, sync_status='pending', source='cloud'):
        """Update sync status for a product - using string IDs"""
        try:
            sync_log = self.add_sync_log(source=source, status=sync_status)
            
            result = self.product_collection.update_one(
                {'_id': product_id},
                {'$push': {'sync_logs': sync_log}}
            )
            
            return result.modified_count > 0
        
        except Exception as e:
            logger.error(f"Error updating sync status: {str(e)}")
            return False

    def mark_as_synced(self, product_id, source='cloud'):
        """Mark a product as successfully synced"""
        return self.update_sync_status(product_id, sync_status='synced', source=source)
    
    def get_unsynced_products(self, source='local'):
        """Get products that need to be synced from specified source"""
        try:
            pipeline = [
                {
                    '$addFields': {
                        'latest_sync': {
                            '$arrayElemAt': [
                                {
                                    '$filter': {
                                        'input': '$sync_logs',
                                        'cond': {'$eq': ['$$this.source', source]}
                                    }
                                },
                                -1  # Get the latest entry for this source
                            ]
                        }
                    }
                },
                {
                    '$match': {
                        '$or': [
                            {'latest_sync': None},  # No sync log for this source
                            {'latest_sync.status': {'$ne': 'synced'}}  # Not synced
                        ]
                    }
                }
            ]
            
            products = list(self.product_collection.aggregate(pipeline))
            return products
        
        except Exception as e:
            raise Exception(f"Error getting unsynced products: {str(e)}")
    
    def generate_sku(self, product_name, category_id=None):
        """Generate a unique SKU for the product - string-based category lookup"""
        try:
            # Get category prefix
            category_prefix = "PROD"
            if category_id:
                category = self.category_collection.find_one({'_id': category_id})
                if category:
                    category_prefix = category.get('category_name', 'PROD')[:4].upper()
            
            # Get product name prefix
            name_prefix = ''.join(product_name.split()[:2])[:4].upper()
            
            # Count existing products to generate sequence number (exclude deleted products)
            count = self.product_collection.count_documents({'isDeleted': {'$ne': True}}) + 1
            
            # Generate SKU: CATEGORY-NAME-NUMBER
            sku = f"{category_prefix}-{name_prefix}-{count:03d}"
            
            # Ensure uniqueness (check against non-deleted products)
            while self.product_collection.find_one({'SKU': sku, 'isDeleted': {'$ne': True}}):
                count += 1
                sku = f"{category_prefix}-{name_prefix}-{count:03d}"
            
            return sku
        except Exception as e:
            # Fallback to simple SKU
            count = self.product_collection.count_documents({'isDeleted': {'$ne': True}}) + 1
            return f"PROD-{count:06d}"
    
    def calculate_similarity(self, str1, str2):
        """Calculate similarity between two strings (0.0 to 1.0)"""
        try:
            from difflib import SequenceMatcher
            return SequenceMatcher(None, str1, str2).ratio()
        except ImportError:
            # Fallback: simple character comparison
            if str1 == str2:
                return 1.0
            elif str1 in str2 or str2 in str1:
                return 0.8
            else:
                return 0.0
    
    # ================================================================
    # CORE PRODUCT CRUD OPERATIONS
    # ================================================================
    
    def create_product(self, product_data):
        """Create a new product with sequential PROD-##### ID"""
        try:
            logger.info(f"Creating single product: {product_data.get('product_name', 'Unknown')}")
            
            # Generate sequential product ID
            product_id = self.generate_product_id()
            
            # Validate foreign keys
            self.validate_foreign_keys(product_data)
            
            # Generate SKU if not provided
            if not product_data.get('SKU'):
                product_data['SKU'] = self.generate_sku(
                    product_data.get('product_name', 'Product'),
                    product_data.get('category_id')
                )
            
            # ENHANCED DUPLICATE VALIDATION FOR SINGLE PRODUCT
            existing_product = self.product_collection.find_one({
                'SKU': product_data['SKU'], 
                'isDeleted': {'$ne': True}
            })
            if existing_product:
                raise ValueError(f"Product with SKU '{product_data['SKU']}' already exists")
            
            product_name = product_data.get('product_name', '').strip()
            if product_name:
                existing_name = self.product_collection.find_one({
                    'product_name': {'$regex': f'^{re.escape(product_name)}$', '$options': 'i'}, 
                    'isDeleted': {'$ne': True}
                })
                if existing_name:
                    raise ValueError(f"Product with name '{product_name}' already exists")
            
            # Set default values - Create clean product document
            current_time = datetime.utcnow()
            product_document = {
                '_id': product_id,
                'product_name': product_data.get('product_name', ''),
                'category_id': product_data.get('category_id', ''),
                'subcategory_name': product_data.get('subcategory_name', ''),
                'SKU': product_data['SKU'],
                'unit': product_data.get('unit', ''),
                'stock': int(product_data.get('stock', 0)),
                'low_stock_threshold': int(product_data.get('low_stock_threshold', 10)),
                'cost_price': float(product_data.get('cost_price', 0)),
                'selling_price': float(product_data.get('selling_price', 0)),
                'status': product_data.get('status', 'active'),
                'is_taxable': product_data.get('is_taxable', True),
                'date_received': product_data.get('date_received', current_time),
                'isDeleted': False,
                'created_at': current_time,
                'updated_at': current_time,
                # Batch-related fields for simplified expiry tracking
                'total_stock': int(product_data.get('stock', 0)),
                'oldest_batch_expiry': None,
                'newest_batch_expiry': None,
                'expiry_alert': False
            }
            
            # Add optional fields if present
            optional_fields = ['expiry_date', 'barcode', 'description', 'supplier_id', 'branch_id']
            for field in optional_fields:
                if field in product_data and product_data[field]:
                    product_document[field] = product_data[field]
                
            image_fields = ['image', 'image_url', 'image_filename', 'image_size', 'image_type', 'image_uploaded_at']
            for field in image_fields:
                if field in product_data and product_data[field] is not None:
                    product_document[field] = product_data[field]
                        
            # Initialize sync logs
            product_document['sync_logs'] = [
                self.add_sync_log(source='cloud', status='pending', details={'action': 'created'})
            ]
            
            # AUTO-ASSIGN TO CATEGORY/SUBCATEGORY - SIMPLIFIED
            product_document = self._ensure_default_category_assignment(product_document)
            
            # Insert product directly as dict
            self.product_collection.insert_one(product_document)
            
            # Get created product
            created_product = self.product_collection.find_one({'_id': product_id})
            
            # Send notification
            self._send_product_notification(
                'created',
                product_document.get("product_name", product_document.get("SKU", "Unknown Product")),
                product_id,
                {
                    "SKU": product_document["SKU"],
                    "category_id": created_product.get('category_id'),
                    "subcategory_name": created_product.get('subcategory_name')
                }
            )

            return created_product
        
        except Exception as e:
            raise Exception(f"Error creating product: {str(e)}")
    
    def get_all_products(self, filters=None, include_deleted=False):
        """Get all products with optional filters"""
        try:
            query = {}
            
            # By default, exclude deleted products unless specifically requested
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
            
            if filters:
                # Category filter
                if filters.get('category_id'):
                    query['category_id'] = filters['category_id']
                
                # Subcategory filter
                if filters.get('subcategory_name'):
                    query['subcategory_name'] = filters['subcategory_name']
                
                # Status filter
                if filters.get('status'):
                    query['status'] = filters['status']
                
                # Stock level filter
                if filters.get('stock_level'):
                    if filters['stock_level'] == 'out_of_stock':
                        query['stock'] = 0
                    elif filters['stock_level'] == 'low_stock':
                        query['$expr'] = {'$lte': ['$stock', '$low_stock_threshold']}
                
                # Search filter
                if filters.get('search'):
                    search_regex = {'$regex': filters['search'], '$options': 'i'}
                    query['$or'] = [
                        {'product_name': search_regex},
                        {'SKU': search_regex},
                        {'_id': search_regex}
                    ]
            
            products = list(self.product_collection.find(query).sort('product_name', 1))
            return products
        
        except Exception as e:
            raise Exception(f"Error getting products: {str(e)}")
    
    def get_product_by_id(self, product_id, include_deleted=False):
        """Get product by string ID"""
        try:
            query = {'_id': product_id}
            
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
            
            product = self.product_collection.find_one(query)
            return product
        
        except Exception as e:
            raise Exception(f"Error getting product: {str(e)}")
    
    def get_product_by_sku(self, sku, include_deleted=False):
        """Get product by SKU"""
        try:
            query = {'SKU': sku}
            
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
            
            product = self.product_collection.find_one(query)
            return product
        
        except Exception as e:
            raise Exception(f"Error getting product by SKU: {str(e)}")
    
    def update_product(self, product_id, product_data):
        """Update product - SIMPLIFIED without complex category sync"""
        try:
            # Check if product exists and is not deleted
            existing_product = self.get_product_by_id(product_id, include_deleted=False)
            if not existing_product:
                raise Exception(f"Product with ID {product_id} not found or is deleted")
            
            # Validate foreign keys if they're being updated
            self.validate_foreign_keys(product_data)
            
            # Ensure numeric fields are properly typed
            numeric_fields = ['stock', 'low_stock_threshold', 'cost_price', 'selling_price']
            for field in numeric_fields:
                if field in product_data:
                    try:
                        if field in ['stock', 'low_stock_threshold']:
                            product_data[field] = int(product_data[field])
                        else:
                            product_data[field] = float(product_data[field])
                    except (ValueError, TypeError):
                        pass  # Keep original value if conversion fails
            
            # Add updated timestamp
            product_data['updated_at'] = datetime.utcnow()
            
            # Update product (only non-deleted products)
            result = self.product_collection.update_one(
                {'_id': product_id, 'isDeleted': {'$ne': True}}, 
                {'$set': product_data}
            )
            
            if result.modified_count > 0:
                # Mark as needing sync since data was updated
                self.update_sync_status(product_id, sync_status='pending', source='cloud')
                
                updated_product = self.product_collection.find_one({'_id': product_id})
                
                # Send notification
                product_name = updated_product.get("product_name", updated_product.get("SKU", "Unknown Product"))
                
                notification_metadata = {
                    "SKU": updated_product.get("SKU"),
                    "updated_fields": list(product_data.keys()),
                    "category_id": updated_product.get('category_id'),
                    "subcategory_name": updated_product.get('subcategory_name')
                }
                
                self._send_product_notification(
                    'updated',
                    product_name,
                    product_id,
                    notification_metadata
                )
                
                return updated_product
            return None
        
        except Exception as e:
            raise Exception(f"Error updating product: {str(e)}")

    def delete_product(self, product_id, hard_delete=False):
        """Soft delete or hard delete a product"""
        try:
            # Get product details before deletion for notification
            product_to_delete = self.product_collection.find_one({'_id': product_id})
            if not product_to_delete:
                return False
            
            if hard_delete:
                # Hard delete - permanently remove from database
                result = self.product_collection.delete_one({'_id': product_id})
                
                if result.deleted_count > 0:
                    # Send notification for hard deletion
                    product_name = product_to_delete.get("product_name", product_to_delete.get("SKU", "Unknown Product"))
                    
                    self._send_product_notification(
                        'hard_deleted',
                        product_name,
                        product_id,
                        {
                            "SKU": product_to_delete.get("SKU"),
                            "deletion_type": "permanent",
                            "deleted_at": datetime.utcnow().isoformat(),
                            "stock_at_deletion": product_to_delete.get("stock", 0)
                        }
                    )
                    
                    return True
                return False
            else:
                # Soft delete - mark as deleted with timestamp and reason
                current_time = datetime.utcnow()
                
                # Create deletion log entry
                deletion_log = {
                    'deleted_at': current_time,
                    'deleted_by': 'system',  # This could be user ID in the future
                    'reason': 'Manual deletion'
                }
                
                # Update product to mark as deleted
                result = self.product_collection.update_one(
                    {'_id': product_id, 'isDeleted': {'$ne': True}},
                    {
                        '$set': {
                            'isDeleted': True,
                            'updated_at': current_time,
                            'deletion_log': deletion_log
                        }
                    }
                )
                
                if result.modified_count > 0:
                    # Mark as needing sync since product was deleted
                    self.update_sync_status(product_id, sync_status='pending_deletion', source='cloud')
                    
                    # Send notification for soft deletion
                    product_name = product_to_delete.get("product_name", product_to_delete.get("SKU", "Unknown Product"))
                    
                    self._send_product_notification(
                        'soft_deleted',
                        product_name,
                        product_id,
                        {
                            "SKU": product_to_delete.get("SKU"),
                            "deletion_type": "soft",
                            "deleted_at": current_time.isoformat(),
                            "deleted_by": deletion_log["deleted_by"],
                            "deletion_reason": deletion_log["reason"],
                            "stock_at_deletion": product_to_delete.get("stock", 0),
                            "can_be_restored": True
                        }
                    )
                    
                    return True
                
                return False
        
        except Exception as e:
            raise Exception(f"Error deleting product: {str(e)}")

    def restore_product(self, product_id):
        """Restore a soft-deleted product"""
        try:
            current_time = datetime.utcnow()
            
            # Create restoration log entry
            restoration_log = {
                'restored_at': current_time,
                'restored_by': 'system',  # This could be user ID in the future
                'reason': 'Manual restoration'
            }
            
            # Update product to restore it
            result = self.product_collection.update_one(
                {'_id': product_id, 'isDeleted': True},
                {
                    '$set': {
                        'isDeleted': False,
                        'updated_at': current_time,
                        'restoration_log': restoration_log
                    },
                    '$unset': {
                        'deletion_log': 1  # Remove deletion log when restoring
                    }
                }
            )
            
            if result.modified_count > 0:
                # Mark as needing sync since product was restored
                self.update_sync_status(product_id, sync_status='pending', source='cloud')
                
                # Get restored product and send notification
                restored_product = self.product_collection.find_one({'_id': product_id})
                product_name = restored_product.get("product_name", restored_product.get("SKU", "Unknown Product"))
                
                self._send_product_notification(
                    'restored',
                    product_name,
                    product_id,
                    {
                        "SKU": restored_product.get("SKU"),
                        "restored_at": current_time.isoformat(),
                        "restored_by": restoration_log["restored_by"]
                    }
                )
                
                return True
            
            return False
        
        except Exception as e:
            raise Exception(f"Error restoring product: {str(e)}")

    # ================================================================
    # STOCK MANAGEMENT WITH BATCH INTEGRATION
    # ================================================================
    
    def update_stock(self, product_id, stock_data):
        """Update product stock with various operation types"""
        try:
            # Get current product to access current stock (only non-deleted)
            current_product = self.product_collection.find_one({
                '_id': product_id,
                'isDeleted': {'$ne': True}
            })
            if not current_product:
                raise Exception(f"Product with ID {product_id} not found or is deleted")
            
            current_stock = current_product.get('stock', 0)
            
            # Extract operation details
            operation_type = stock_data.get('operation_type', 'set')
            quantity = int(stock_data.get('quantity', 0))
            reason = stock_data.get('reason', 'Manual adjustment')
            
            # Calculate new stock based on operation type
            if operation_type == 'add':
                new_stock = current_stock + quantity
            elif operation_type == 'remove':
                new_stock = max(0, current_stock - quantity)  # Don't allow negative stock
            elif operation_type == 'set':
                new_stock = quantity
            else:
                raise ValueError(f"Invalid operation type: {operation_type}")
            
            # Validate new stock
            if new_stock < 0:
                raise ValueError("Stock cannot be negative")
            
            # Create stock history entry
            current_time = datetime.utcnow()
            stock_history_entry = {
                'timestamp': current_time,
                'operation': operation_type,
                'quantity': quantity,
                'previous_stock': current_stock,
                'new_stock': new_stock,
                'reason': reason,
                'performed_by': 'system'  # This could be user ID in the future
            }
            
            # Update the product
            update_data = {
                'stock': new_stock,
                'total_stock': new_stock,  # Keep both fields in sync
                'updated_at': current_time
            }
            
            result = self.product_collection.update_one(
                {'_id': product_id, 'isDeleted': {'$ne': True}}, 
                {
                    '$set': update_data,
                    '$push': {'stock_history': stock_history_entry}
                }
            )
            
            if result.modified_count > 0:
                # Mark as needing sync since stock was updated
                self.update_sync_status(product_id, sync_status='pending', source='cloud')
                
                updated_product = self.product_collection.find_one({'_id': product_id})
                
                # Prepare notification data
                product_name = updated_product.get("product_name", updated_product.get("SKU", "Unknown Product"))
                low_stock_threshold = updated_product.get('low_stock_threshold', 0)
                
                # Determine notification type and create operation-specific message
                if new_stock == 0:
                    action_type = 'stock_out'
                    message_suffix = " - OUT OF STOCK!"
                elif new_stock <= low_stock_threshold and new_stock > 0:
                    action_type = 'stock_low' 
                    message_suffix = " - LOW STOCK WARNING!"
                else:
                    action_type = 'stock_updated'
                    message_suffix = ""
                
                # Create operation-specific message
                if operation_type == 'add':
                    base_message = f"Stock added to '{product_name}': +{quantity} units (Total: {new_stock})"
                elif operation_type == 'remove':
                    base_message = f"Stock removed from '{product_name}': -{quantity} units (Total: {new_stock})"
                elif operation_type == 'set':
                    base_message = f"Stock set for '{product_name}': {new_stock} units"
                
                custom_message = base_message + message_suffix
                
                # Send notification
                self._send_product_notification(
                    action_type,
                    product_name,
                    product_id,
                    {
                        "SKU": updated_product.get("SKU"),
                        "operation_type": operation_type,
                        "quantity_changed": quantity,
                        "previous_stock": current_stock,
                        "new_stock": new_stock,
                        "reason": reason,
                        "is_low_stock": new_stock <= low_stock_threshold,
                        "is_out_of_stock": new_stock == 0,
                        "low_stock_threshold": low_stock_threshold,
                        "custom_message": custom_message
                    }
                )
                
                return updated_product
            return None
        
        except Exception as e:
            raise Exception(f"Error updating stock: {str(e)}")
        
    def bulk_update_stock(self, stock_updates):
        """Update multiple products' stock in batch"""
        try:
            results = []
            for update in stock_updates:
                product_id = update.get('product_id')
                stock_data = {
                    'operation_type': update.get('operation_type', 'set'),
                    'quantity': update.get('quantity', 0),
                    'reason': update.get('reason', 'Bulk update')
                }
                
                result = self.update_stock(product_id, stock_data)
                results.append({
                    'product_id': product_id,
                    'success': result is not None,
                    'result': result
                })
            
            # Send unified notification for bulk stock update
            successful_count = len([r for r in results if r['success']])
            failed_count = len([r for r in results if not r['success']])
            total_updates = len(stock_updates)
            
            if failed_count == 0:
                message = f"Bulk stock update completed successfully: {successful_count} products updated"
            else:
                message = f"Bulk stock update completed: {successful_count} successful, {failed_count} failed out of {total_updates} total"
            
            self._send_product_notification(
                'bulk_stock_updated',
                f"{successful_count} products",
                None,  # No single product ID for bulk operations
                {
                    "total_products": total_updates,
                    "successful_updates": successful_count,
                    "failed_updates": failed_count,
                    "success_rate": round((successful_count / total_updates) * 100, 2) if total_updates > 0 else 0,
                    "custom_message": message
                }
            )
            
            return results
        
        except Exception as e:
            raise Exception(f"Error in bulk stock update: {str(e)}")
        
    def adjust_stock_for_sale(self, product_id, quantity_sold):
        """Reduce stock when a sale is made - now uses FIFO from batches"""
        try:
            # Process sale using FIFO from batch service
            batches_used = self.batch_service.process_sale_fifo(product_id, quantity_sold)
            
            # Update product stock using existing method
            stock_data = {
                'operation_type': 'remove',
                'quantity': quantity_sold,
                'reason': 'Sale transaction'    
            }
            updated_product = self.update_stock(product_id, stock_data)
            
            return {
                'product': updated_product,
                'batches_used': batches_used
            }

        except Exception as e:
            raise Exception(f"Error adjusting stock for sale: {str(e)}")
    
    def restock_product(self, product_id, quantity_received, supplier_info=None, batch_info=None):
        """Add stock when receiving new inventory - now creates batches"""
        try:
            # Create batch first
            batch_data = {
                'product_id': product_id,
                'quantity_received': quantity_received,
                'cost_price': batch_info.get('cost_price') if batch_info else 0,
                'expiry_date': batch_info.get('expiry_date') if batch_info else None,
                'supplier_id': supplier_info.get('supplier_id') if supplier_info else None,
                'batch_number': batch_info.get('batch_number') if batch_info else None
            }
            
            # Create the batch (this will automatically update product expiry summary)
            batch = self.batch_service.create_batch(batch_data)
            
            # Update product stock using the existing method
            reason = f"Restock from supplier"
            if supplier_info:
                reason += f" - {supplier_info.get('name', 'Unknown')}"
            
            stock_data = {
                'operation_type': 'add',
                'quantity': quantity_received,
                'reason': reason
            }
            
            updated_product = self.update_stock(product_id, stock_data)
            
            return {
                'product': updated_product,
                'batch': batch
            }
            
        except Exception as e:
            raise Exception(f"Error restocking product: {str(e)}")

    def get_product_with_batch_summary(self, product_id):
        """Get product with batch and expiry summary information"""
        try:
            product = self.get_product_by_id(product_id)
            if not product:
                return None
            
            # Get active batches for this product
            batches = self.batch_service.get_batches_by_product(product_id, status='active')
            
            product['active_batches'] = batches
            product['batch_count'] = len(batches)
            
            return product
        
        except Exception as e:
            raise Exception(f"Error getting product with batch summary: {str(e)}")

    def check_expiry_alerts(self, days_ahead=7):
        """Check for products with expiring batches and return alert summary"""
        try:
            return self.batch_service.check_and_alert_expiring_batches(days_ahead)
        
        except Exception as e:
            raise Exception(f"Error checking expiry alerts: {str(e)}")

    # ================================================================
    # PRODUCT QUERIES AND FILTERING
    # ================================================================
    
    def get_deleted_products(self):
        """Get all soft-deleted products"""
        try:
            products = list(self.product_collection.find({'isDeleted': True}).sort('deletion_log.deleted_at', -1))
            return products
        
        except Exception as e:
            raise Exception(f"Error getting deleted products: {str(e)}")
    
    def get_low_stock_products(self, branch_id=None):
        """Get products with low stock (excluding deleted)"""
        try:
            query = {
                '$expr': {'$lte': ['$stock', '$low_stock_threshold']},
                'isDeleted': {'$ne': True}
            }
            
            if branch_id:
                query['branch_id'] = branch_id
            
            products = list(self.product_collection.find(query))
            return products
        
        except Exception as e:
            raise Exception(f"Error getting low stock products: {str(e)}")
    
    def get_products_by_category(self, category_id, subcategory_name=None):
        """Get products by category and optionally by subcategory"""
        try:
            query = {
                'category_id': category_id,
                'isDeleted': {'$ne': True}
            }
            
            if subcategory_name:
                query['subcategory_name'] = subcategory_name
            
            products = list(self.product_collection.find(query))
            return products
        
        except Exception as e:
            raise Exception(f"Error getting products by category: {str(e)}")
    
    def get_expiring_products(self, days_ahead=30):
        """Get products with expiring batches within specified days"""
        try:
            from datetime import timedelta
            
            future_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            query = {
                'oldest_batch_expiry': {
                    '$lte': future_date,
                    '$gte': datetime.utcnow()
                },
                'isDeleted': {'$ne': True}
            }
            
            products = list(self.product_collection.find(query).sort('oldest_batch_expiry', 1))
            return products
        
        except Exception as e:
            raise Exception(f"Error getting expiring products: {str(e)}")

    # ================================================================
    # BULK OPERATIONS
    # ================================================================
        
    def bulk_create_products(self, products_data):
        """Create multiple products in batch with validation"""
        try:
            logger.info(f"Processing {len(products_data)} products for bulk creation")
            
            validated_products = []
            errors = []
            seen_skus = set()
            seen_names = set()
            
            for i, product_data in enumerate(products_data):
                try:
                    logger.debug(f"Processing product {i+1}: {product_data.get('product_name', 'Unknown')}")
                    
                    # Generate sequential product ID for each product
                    product_id = self.generate_product_id()
                    product_data['_id'] = product_id
                    
                    # Validate foreign keys
                    self.validate_foreign_keys(product_data)
                    
                    # Generate SKU if not provided
                    if not product_data.get('SKU'):
                        product_data['SKU'] = self.generate_sku(
                            product_data.get('product_name', 'Product'),
                            product_data.get('category_id')
                        )
                    
                    # DUPLICATE VALIDATION
                    if product_data['SKU'] in seen_skus:
                        raise ValueError(f"Duplicate SKU in current batch: {product_data['SKU']}")
                    
                    existing_sku = self.product_collection.find_one({
                        'SKU': product_data['SKU'], 
                        'isDeleted': {'$ne': True}
                    })
                    if existing_sku:
                        raise ValueError(f"Product with SKU '{product_data['SKU']}' already exists in database")
                    
                    product_name_lower = product_data.get('product_name', '').strip().lower()
                    if product_name_lower in seen_names:
                        raise ValueError(f"Duplicate product name in current batch: {product_data.get('product_name')}")
                    
                    if product_name_lower:
                        existing_name = self.product_collection.find_one({
                            'product_name': {'$regex': f'^{re.escape(product_data.get("product_name", ""))}$', '$options': 'i'}, 
                            'isDeleted': {'$ne': True}
                        })
                        if existing_name:
                            raise ValueError(f"Product with name '{product_data.get('product_name')}' already exists in database")
                    
                    seen_skus.add(product_data['SKU'])
                    seen_names.add(product_name_lower)
                    
                    # AUTO-ASSIGN CATEGORY FOR BULK PRODUCTS - SIMPLIFIED
                    product_data = self._ensure_default_category_assignment(product_data)
                    
                    # Set default values
                    current_time = datetime.utcnow()
                    product_data.update({
                        'date_received': product_data.get('date_received', current_time),
                        'status': product_data.get('status', 'active'),
                        'is_taxable': product_data.get('is_taxable', True),
                        'isDeleted': False,
                        'created_at': current_time,
                        'updated_at': current_time,
                        'sync_logs': [self.add_sync_log(source='cloud', status='pending', details={'action': 'bulk_created'})],
                        # Batch-related fields for simplified expiry tracking
                        'total_stock': int(product_data.get('stock', 0)),
                        'oldest_batch_expiry': None,
                        'newest_batch_expiry': None,
                        'expiry_alert': False
                    })
                    
                    # Handle numeric fields
                    numeric_fields = ['stock', 'low_stock_threshold', 'cost_price', 'selling_price']
                    for field in numeric_fields:
                        if field in product_data:
                            try:
                                if field in ['stock', 'low_stock_threshold']:
                                    product_data[field] = int(product_data[field])
                                else:
                                    price_str = str(product_data[field])
                                    clean_price = price_str.replace('₱', '').replace(',', '').strip()
                                    product_data[field] = float(clean_price)
                            except (ValueError, TypeError):
                                product_data[field] = 0
                    
                    validated_products.append(product_data)
                    logger.debug(f"Product {i+1} validated and ready for creation")
                    
                except Exception as e:
                    logger.error(f"Product {i+1} validation failed: {str(e)}")
                    errors.append({
                        'index': i,
                        'data': product_data,
                        'error': str(e)
                    })
            
            # Perform bulk insert
            results = {
                'successful': [],
                'failed': errors,
                'total_processed': len(products_data),
                'total_successful': 0,
                'total_failed': len(errors)
            }
            
            if validated_products:
                logger.info(f"Inserting {len(validated_products)} validated products...")
                
                insert_result = self.product_collection.insert_many(validated_products, ordered=False)
                
                # Get inserted products
                inserted_products = list(self.product_collection.find({
                    '_id': {'$in': [product['_id'] for product in validated_products]}
                }))
                
                results['successful'] = inserted_products
                results['total_successful'] = len(inserted_products)
                
                # Send notification for bulk creation
                total_processed = len(products_data)
                successful_count = len(inserted_products)
                failed_count = len(errors)
                
                if failed_count == 0:
                    action_type = 'bulk_created'
                    message = f"Bulk product creation completed successfully: {successful_count} products created"
                else:
                    action_type = 'bulk_created'
                    message = f"Bulk product creation completed: {successful_count} successful, {failed_count} failed out of {total_processed} total"
                
                self._send_product_notification(
                    action_type,
                    f"{successful_count} products",
                    None,  # No single product ID for bulk operations
                    {
                        "total_products": total_processed,
                        "successful_creations": successful_count,
                        "failed_creations": failed_count,
                        "success_rate": round((successful_count / total_processed) * 100, 2) if total_processed > 0 else 0,
                        "custom_message": message
                    }
                )
            
            logger.info(f"Bulk creation completed: {results['total_successful']} successful, {results['total_failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Bulk create service error: {str(e)}")
            raise Exception(f"Error in bulk product creation: {str(e)}")

    # ================================================================
    # SYNC-RELATED METHODS
    # ================================================================
    
    def prepare_for_sync_to_local(self):
        """Get all products that need to be synced to local database"""
        return self.get_unsynced_products(source='cloud')
    
    def prepare_for_sync_to_cloud(self):
        """Get all products that need to be synced to cloud database"""
        return self.get_unsynced_products(source='local')
    
    def sync_from_local(self, local_products):
        """Sync products from local database to cloud"""
        try:
            sync_results = []
            
            for product_data in local_products:
                try:
                    product_id = product_data.get('_id')
                    
                    if product_id:
                        # Update existing product
                        result = self.update_product(product_id, product_data)
                        if result:
                            self.mark_as_synced(product_id, source='local')
                            sync_results.append({'product_id': product_id, 'status': 'updated'})
                    else:
                        # Create new product
                        result = self.create_product(product_data)
                        if result:
                            self.mark_as_synced(result['_id'], source='local')
                            sync_results.append({'product_id': result['_id'], 'status': 'created'})
                            
                except Exception as e:
                    sync_results.append({'product_id': product_data.get('_id'), 'status': 'error', 'error': str(e)})
            
            return sync_results
        
        except Exception as e:
            raise Exception(f"Error syncing from local: {str(e)}")
    
    def sync_to_local(self):
        """Prepare cloud products for sync to local database"""
        try:
            # Get all products that need to be synced
            products_to_sync = self.prepare_for_sync_to_local()
            
            # Mark them as synced once they're prepared for sync
            for product in products_to_sync:
                self.mark_as_synced(product['_id'], source='cloud')
            
            return products_to_sync
        
        except Exception as e:
            raise Exception(f"Error preparing sync to local: {str(e)}")

    # ================================================================
    # IMPORT/EXPORT FUNCTIONALITY
    # ================================================================
        
    def parse_import_file(self, file_path, file_type='csv'):
        """Parse CSV or Excel file for product import"""
        try:
            import pandas as pd
            
            # Read file based on type
            if file_type.lower() == 'csv':
                df = pd.read_csv(file_path)
            elif file_type.lower() in ['xlsx', 'xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Define expected columns and their mappings
            column_mapping = {
                'product_name': ['product_name', 'name', 'product', 'item_name'],
                'SKU': ['sku', 'SKU', 'product_code', 'code'],
                'category_id': ['category_id', 'category', 'category_name'],
                'subcategory_name': ['subcategory_name', 'subcategory', 'sub_category'],
                'supplier_id': ['supplier_id', 'supplier', 'supplier_name'],
                'stock': ['stock', 'quantity', 'qty', 'current_stock'],
                'low_stock_threshold': ['low_stock_threshold', 'min_stock', 'reorder_level'],
                'cost_price': ['cost_price', 'cost', 'purchase_price'],
                'selling_price': ['selling_price', 'price', 'sale_price'],
                'unit': ['unit', 'unit_of_measure', 'uom'],
                'expiry_date': ['expiry_date', 'expiration_date', 'exp_date'],
                'status': ['status', 'active', 'enabled']
            }
            
            # Normalize column names and map to expected fields
            products_data = []
            for _, row in df.iterrows():
                product_data = {}
                
                for expected_field, possible_columns in column_mapping.items():
                    value = None
                    for col in possible_columns:
                        if col in df.columns:
                            value = row[col]
                            if pd.notna(value):  # Check if not NaN
                                break
                    
                    if value is not None and pd.notna(value):
                        # Handle category name to ID conversion
                        if expected_field == 'category_id' and not str(value).startswith('CTGY-'):
                            # Look up category by name
                            category = self.category_collection.find_one({'category_name': {'$regex': f'^{value}$', '$options': 'i'}})
                            product_data[expected_field] = category['_id'] if category else None
                        elif expected_field == 'supplier_id' and not str(value).startswith('SUPP-'):
                            # Look up supplier by name
                            supplier = self.supplier_collection.find_one({'name': {'$regex': f'^{value}$', '$options': 'i'}})
                            product_data[expected_field] = supplier['_id'] if supplier else None
                        else:
                            product_data[expected_field] = value
                
                # Only add if required fields are present
                if product_data.get('product_name'):
                    products_data.append(product_data)
            
            return {
                'products_data': products_data,
                'total_rows': len(df),
                'valid_products': len(products_data),
                'columns_found': list(df.columns)
            }
            
        except Exception as e:
            raise Exception(f"Error parsing import file: {str(e)}")
        
    def import_products_from_file(self, file_path, file_type='csv', validate_only=False):
        """Import products from CSV or Excel file"""
        try:
            # Parse the file
            parse_result = self.parse_import_file(file_path, file_type)
            
            if validate_only:
                # Only validate, don't create products
                validation_errors = []
                for i, product_data in enumerate(parse_result['products_data']):
                    try:
                        self.validate_foreign_keys(product_data)
                    except Exception as e:
                        validation_errors.append({
                            'row': i + 2,  # +2 for header and 0-based index
                            'error': str(e),
                            'data': product_data
                        })
                
                return {
                    'validation_only': True,
                    'total_rows': parse_result['total_rows'],
                    'valid_products': parse_result['valid_products'],
                    'validation_errors': validation_errors,
                    'columns_found': parse_result['columns_found']
                }
            
            # Create products in bulk
            bulk_result = self.bulk_create_products(parse_result['products_data'])
            
            # Create import completion notification
            try:
                total_rows = parse_result['total_rows']
                valid_products = parse_result['valid_products']
                successful_imports = bulk_result['total_successful']
                failed_imports = bulk_result['total_failed']
                
                # Determine priority based on success rate
                if failed_imports == 0 and valid_products > 0:
                    priority = "low"
                    notification_type = "system"
                elif failed_imports < successful_imports:
                    priority = "medium"
                    notification_type = "alert"
                else:
                    priority = "high"
                    notification_type = "alert"
                
                # Create summary message
                if failed_imports == 0 and valid_products > 0:
                    message = f"Product import completed successfully: {successful_imports} products imported from {total_rows} rows"
                elif valid_products == 0:
                    message = f"Product import failed: No valid products found in {total_rows} rows"
                else:
                    message = f"Product import completed: {successful_imports} successful, {failed_imports} failed from {valid_products} valid products"
                
                notification_service.create_notification(
                    title="Product Import Completed",
                    message=message,
                    priority=priority,
                    notification_type=notification_type,
                    metadata={
                        "import_source": "file_import",
                        "action_type": "products_imported",
                        "file_type": file_type,
                        "total_rows": total_rows,
                        "valid_products": valid_products,
                        "successful_imports": successful_imports,
                        "failed_imports": failed_imports,
                        "import_success_rate": round((successful_imports / valid_products) * 100, 2) if valid_products > 0 else 0
                    }
                )
            except Exception as notification_error:
                logger.error(f"Failed to create notification for product import: {notification_error}")
            
            return {
                'import_completed': True,
                'file_info': {
                    'total_rows': parse_result['total_rows'],
                    'valid_products': parse_result['valid_products'],
                    'columns_found': parse_result['columns_found']
                },
                'bulk_result': bulk_result
            }
            
        except Exception as e:
            raise Exception(f"Error importing products from file: {str(e)}")
            
    def generate_import_template(self, file_type='csv'):
        """Generate a template file for product import"""
        try:
            import pandas as pd
            
            # Define template columns
            template_data = {
                'product_name': ['Sample Noodle 1', 'Sample Drink 1'],
                'SKU': ['NOOD-SAMP-001', 'DRIN-SAMP-001'],
                'category_id': ['category_name_or_id', 'category_name_or_id'],
                'subcategory_name': ['Noodles', 'Drinks'],
                'supplier_id': ['supplier_name_or_id', 'supplier_name_or_id'],
                'stock': [100, 50],
                'low_stock_threshold': [10, 5],
                'cost_price': [15.00, 25.00],
                'selling_price': [20.00, 30.00],
                'unit': ['piece', 'bottle'],
                'expiry_date': ['2025-12-31', '2025-06-30'],
                'status': ['active', 'active']
            }
            
            df = pd.DataFrame(template_data)
            
            if file_type.lower() == 'csv':
                template_path = 'product_import_template.csv'
                df.to_csv(template_path, index=False)
            elif file_type.lower() == 'xlsx':
                template_path = 'product_import_template.xlsx'
                df.to_excel(template_path, index=False)
            else:
                raise ValueError(f"Unsupported template type: {file_type}")
            
            return template_path
            
        except Exception as e:
            raise Exception(f"Error generating import template: {str(e)}")
        
    @staticmethod
    def bulk_delete_products(product_ids, hard_delete=False):
        deleted_count = 0
        failed_deletions = []
        
        # Create service instance to use existing methods
        service = ProductService()
        
        for product_id in product_ids:
            try:
                # Use your existing delete method that already works
                success = service.delete_product(product_id, hard_delete)
                if success:
                    deleted_count += 1
                else:
                    failed_deletions.append({
                        'product_id': product_id,
                        'error': 'Product not found or delete failed'
                    })
            except Exception as e:
                failed_deletions.append({
                    'product_id': product_id,
                    'error': str(e)
                })
        
        return {
            'deleted_count': deleted_count,
            'failed_count': len(failed_deletions),
            'total_requested': len(product_ids),
            'failed_deletions': failed_deletions,
            'success': deleted_count > 0
        }