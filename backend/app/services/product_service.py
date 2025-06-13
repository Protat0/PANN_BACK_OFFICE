from bson import ObjectId
from datetime import datetime
from ..database import db_manager
from ..models import Product

class ProductService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.product_collection = self.db.products
        self.category_collection = self.db.categories
        self.supplier_collection = self.db.suppliers
        self.branch_collection = self.db.branches
    
    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        # Convert other ObjectId fields
        for field in ['category_id', 'supplier_id', 'branch_id']:
            if document and field in document and isinstance(document[field], ObjectId):
                document[field] = str(document[field])
        return document
    
    def validate_foreign_keys(self, product_data):
        """Validate that foreign key references exist"""
        # Validate category_id
        if 'category_id' in product_data and product_data['category_id']:
            if ObjectId.is_valid(product_data['category_id']):
                category = self.category_collection.find_one({'_id': ObjectId(product_data['category_id'])})
                if not category:
                    raise ValueError(f"Category with ID {product_data['category_id']} not found")
        
        # Validate supplier_id
        if 'supplier_id' in product_data and product_data['supplier_id']:
            if ObjectId.is_valid(product_data['supplier_id']):
                supplier = self.supplier_collection.find_one({'_id': ObjectId(product_data['supplier_id'])})
                if not supplier:
                    raise ValueError(f"Supplier with ID {product_data['supplier_id']} not found")
        
        # Validate branch_id
        if 'branch_id' in product_data and product_data['branch_id']:
            if ObjectId.is_valid(product_data['branch_id']):
                branch = self.branch_collection.find_one({'_id': ObjectId(product_data['branch_id'])})
                if not branch:
                    raise ValueError(f"Branch with ID {product_data['branch_id']} not found")
    
    def add_sync_log(self, source='cloud', status='synced', details=None):
        """Helper method to create sync log entries"""
        return {
            'last_updated': datetime.utcnow(),
            'source': source,  # 'local' or 'cloud'
            'status': status,  # 'synced', 'pending', 'failed'
            'details': details or {}
        }
    
    def update_sync_status(self, product_id, sync_status='pending', source='cloud'):
        """Update sync status for a product - called when data changes"""
        try:
            if not ObjectId.is_valid(product_id):
                return False
            
            sync_log = self.add_sync_log(source=source, status=sync_status)
            
            result = self.product_collection.update_one(
                {'_id': ObjectId(product_id)},
                {'$push': {'sync_logs': sync_log}}
            )
            
            return result.modified_count > 0
        
        except Exception as e:
            print(f"Error updating sync status: {str(e)}")
            return False
    
    def mark_as_synced(self, product_id, source='cloud'):
        """Mark a product as successfully synced"""
        return self.update_sync_status(product_id, sync_status='synced', source=source)
    
    def get_unsynced_products(self, source='local'):
        """Get products that need to be synced from specified source"""
        try:
            # Find products where the latest sync log is not 'synced' for the specified source
            # or where there's no sync log for the specified source
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
            return [self.convert_object_id(product) for product in products]
        
        except Exception as e:
            raise Exception(f"Error getting unsynced products: {str(e)}")
    
    def generate_sku(self, product_name, category_id=None):
        """Generate a unique SKU for the product"""
        try:
            # Get category prefix
            category_prefix = "PROD"
            if category_id and ObjectId.is_valid(category_id):
                category = self.category_collection.find_one({'_id': ObjectId(category_id)})
                if category:
                    category_prefix = category.get('name', 'PROD')[:4].upper()
            
            # Get product name prefix
            name_prefix = ''.join(product_name.split()[:2])[:4].upper()
            
            # Count existing products to generate sequence number
            count = self.product_collection.count_documents({}) + 1
            
            # Generate SKU: CATEGORY-NAME-NUMBER
            sku = f"{category_prefix}-{name_prefix}-{count:03d}"
            
            # Ensure uniqueness
            while self.product_collection.find_one({'SKU': sku}):
                count += 1
                sku = f"{category_prefix}-{name_prefix}-{count:03d}"
            
            return sku
        except Exception as e:
            # Fallback to simple SKU
            count = self.product_collection.count_documents({}) + 1
            return f"PROD-{count:06d}"
    
    def create_product(self, product_data):
        """Create a new product"""
        try:
            # Validate foreign keys
            self.validate_foreign_keys(product_data)
            
            # Generate SKU if not provided
            if not product_data.get('SKU'):
                product_data['SKU'] = self.generate_sku(
                    product_data.get('product_name', 'Product'),
                    product_data.get('category_id')
                )
            
            # Check if SKU already exists
            existing_product = self.product_collection.find_one({'SKU': product_data['SKU']})
            if existing_product:
                raise ValueError(f"Product with SKU '{product_data['SKU']}' already exists")
            
            # Convert string IDs to ObjectIds
            for field in ['category_id', 'supplier_id', 'branch_id']:
                if field in product_data and product_data[field] and ObjectId.is_valid(product_data[field]):
                    product_data[field] = ObjectId(product_data[field])
            
            # Set default values
            current_time = datetime.utcnow()
            product_data.update({
                'date_received': product_data.get('date_received', current_time),
                'status': product_data.get('status', 'active'),
                'is_taxable': product_data.get('is_taxable', True),
                'created_at': current_time,
                'updated_at': current_time
            })
            
            # Initialize sync logs - mark as needing sync since it's a new record
            product_data['sync_logs'] = [
                self.add_sync_log(source='cloud', status='pending', details={'action': 'created'})
            ]
            
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
                        product_data[field] = 0
            
            # Insert product
            result = self.product_collection.insert_one(product_data)
            
            # Return created product
            created_product = self.product_collection.find_one({'_id': result.inserted_id})
            return self.convert_object_id(created_product)
        
        except Exception as e:
            raise Exception(f"Error creating product: {str(e)}")
    
    def get_all_products(self, filters=None):
        """Get all products with optional filters"""
        try:
            query = {}
            
            if filters:
                # Category filter
                if filters.get('category_id'):
                    if ObjectId.is_valid(filters['category_id']):
                        query['category_id'] = ObjectId(filters['category_id'])
                    else:
                        query['category_id'] = filters['category_id']
                
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
            return [self.convert_object_id(product) for product in products]
        
        except Exception as e:
            raise Exception(f"Error getting products: {str(e)}")
    
    def get_product_by_id(self, product_id):
        """Get product by ID"""
        try:
            if not ObjectId.is_valid(product_id):
                return None
            
            product = self.product_collection.find_one({'_id': ObjectId(product_id)})
            return self.convert_object_id(product) if product else None
        
        except Exception as e:
            raise Exception(f"Error getting product: {str(e)}")
    
    def get_product_by_sku(self, sku):
        """Get product by SKU"""
        try:
            product = self.product_collection.find_one({'SKU': sku})
            return self.convert_object_id(product) if product else None
        
        except Exception as e:
            raise Exception(f"Error getting product by SKU: {str(e)}")
    
    def update_product(self, product_id, product_data):
        """Update product"""
        try:
            if not ObjectId.is_valid(product_id):
                return None
            
            # Validate foreign keys if they're being updated
            self.validate_foreign_keys(product_data)
            
            # Convert string IDs to ObjectIds
            for field in ['category_id', 'supplier_id', 'branch_id']:
                if field in product_data and product_data[field] and ObjectId.is_valid(product_data[field]):
                    product_data[field] = ObjectId(product_data[field])
            
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
            
            # Update product
            result = self.product_collection.update_one(
                {'_id': ObjectId(product_id)}, 
                {'$set': product_data}
            )
            
            if result.modified_count > 0:
                # Mark as needing sync since data was updated
                self.update_sync_status(product_id, sync_status='pending', source='cloud')
                
                updated_product = self.product_collection.find_one({'_id': ObjectId(product_id)})
                return self.convert_object_id(updated_product)
            return None
        
        except Exception as e:
            raise Exception(f"Error updating product: {str(e)}")
    
    def update_stock(self, product_id, stock_data):
        """Update product stock with various operation types"""
        try:
            if not ObjectId.is_valid(product_id):
                return None
            
            # Get current product to access current stock
            current_product = self.product_collection.find_one({'_id': ObjectId(product_id)})
            if not current_product:
                raise Exception(f"Product with ID {product_id} not found")
            
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
            
            # Create stock history entry (separate from sync logs)
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
                'updated_at': current_time
            }
            
            result = self.product_collection.update_one(
                {'_id': ObjectId(product_id)}, 
                {
                    '$set': update_data,
                    '$push': {'stock_history': stock_history_entry}
                }
            )
            
            if result.modified_count > 0:
                # Mark as needing sync since stock was updated
                self.update_sync_status(product_id, sync_status='pending', source='cloud')
                
                updated_product = self.product_collection.find_one({'_id': ObjectId(product_id)})
                return self.convert_object_id(updated_product)
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
            
            return results
        
        except Exception as e:
            raise Exception(f"Error in bulk stock update: {str(e)}")
        
    def adjust_stock_for_sale(self, product_id, quantity_sold):
        """Reduce stock when a sale is made"""
        try:
            stock_data = {
                'operation_type': 'remove',
                'quantity': quantity_sold,
                'reason': 'Sale transaction'    
            }
            return self.update_stock(product_id, stock_data)
    
        except Exception as e:
            raise Exception(f"Error adjusting stock for sale: {str(e)}")
    
    def restock_product(self, product_id, quantity_received, supplier_info=None):
        """Add stock when receiving new inventory"""
        try:
            reason = f"Restock from supplier"
            if supplier_info:
                reason += f" - {supplier_info.get('name', 'Unknown')}"
            
            stock_data = {
                'operation_type': 'add',
                'quantity': quantity_received,
                'reason': reason
            }
            return self.update_stock(product_id, stock_data)
        
        except Exception as e:
            raise Exception(f"Error restocking product: {str(e)}")

    def delete_product(self, product_id):
        """Delete product"""
        try:
            if not ObjectId.is_valid(product_id):
                return False
            
            # Mark as needing sync before deletion (for sync to local to handle deletion)
            self.update_sync_status(product_id, sync_status='pending_deletion', source='cloud')
            
            result = self.product_collection.delete_one({'_id': ObjectId(product_id)})
            return result.deleted_count > 0
        
        except Exception as e:
            raise Exception(f"Error deleting product: {str(e)}")
    
    def get_low_stock_products(self, branch_id=None):
        """Get products with low stock"""
        try:
            query = {'$expr': {'$lte': ['$stock', '$low_stock_threshold']}}
            
            if branch_id and ObjectId.is_valid(branch_id):
                query['branch_id'] = ObjectId(branch_id)
            
            products = list(self.product_collection.find(query))
            return [self.convert_object_id(product) for product in products]
        
        except Exception as e:
            raise Exception(f"Error getting low stock products: {str(e)}")
    
    def get_products_by_category(self, category_id):
        """Get products by category"""
        try:
            if not ObjectId.is_valid(category_id):
                return []
            
            products = list(self.product_collection.find({'category_id': ObjectId(category_id)}))
            return [self.convert_object_id(product) for product in products]
        
        except Exception as e:
            raise Exception(f"Error getting products by category: {str(e)}")
    
    def get_expiring_products(self, days_ahead=30):
        """Get products expiring within specified days"""
        try:
            from datetime import timedelta
            
            future_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            query = {
                'expiry_date': {
                    '$lte': future_date,
                    '$gte': datetime.utcnow()
                }
            }
            
            products = list(self.product_collection.find(query).sort('expiry_date', 1))
            return [self.convert_object_id(product) for product in products]
        
        except Exception as e:
            raise Exception(f"Error getting expiring products: {str(e)}")

    # Sync-related methods for future local/cloud synchronization
    
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