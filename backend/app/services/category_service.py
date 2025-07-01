from bson import ObjectId
from datetime import datetime
from ..database import db_manager 
from ..models import Category
import bcrypt
from notifications.services import notification_service

class CategoryService:
    def __init__(self):
        self.db = db_manager.get_database()  
        self.category_collection = self.db.category
    
    # ================================================================
    # UTILITY METHODS
    # ================================================================
    
    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    # ================================================================
    # NOTIFICATION METHODS
    # ================================================================
    
    def _send_category_notification(self, action_type, category_data, category_id=None, old_category_data=None):
        """
        Send notification for category-related actions
        
        Args:
            action_type (str): 'created', 'updated', or 'deleted'
            category_data (dict): Current category data
            category_id (str): Category ID (for updates/deletes)
            old_category_data (dict): Previous category data (for updates)
        """
        try:
            category_name = category_data.get('category_name', 'Unknown Category')
            
            # Configure notification based on action type
            if action_type == 'created':
                title = "New Category Created"
                message = f"A new category '{category_name}' has been added to the system"
                priority = "high"
                metadata = {
                    "category_id": str(category_id) if category_id else str(category_data.get('_id', '')),
                    "category_name": category_name,
                    "description": category_data.get('description', ''),
                    "status": category_data.get('status', 'active'),
                    "action_type": "category_created",
                    "registration_source": "category_creation"
                }
            
            elif action_type == 'updated':
                title = "Category Updated"
                message = f"Category '{category_name}' has been updated"
                priority = "medium"
                
                # Track what was changed
                changes = []
                if old_category_data:
                    if old_category_data.get('category_name') != category_data.get('category_name'):
                        changes.append(f"name: '{old_category_data.get('category_name')}' → '{category_data.get('category_name')}'")
                    if old_category_data.get('description') != category_data.get('description'):
                        changes.append(f"description: '{old_category_data.get('description')}' → '{category_data.get('description')}'")
                    if old_category_data.get('status') != category_data.get('status'):
                        changes.append(f"status: '{old_category_data.get('status')}' → '{category_data.get('status')}'")
                
                if changes:
                    message += f" - Changes: {', '.join(changes)}"
                
                metadata = {
                    "category_id": str(category_id),
                    "category_name": category_name,
                    "description": category_data.get('description', ''),
                    "status": category_data.get('status', 'active'),
                    "action_type": "category_updated",
                    "changes": changes
                }
            
            elif action_type == 'deleted':
                title = "Category Deleted"
                message = f"Category '{category_name}' has been deactivated/deleted"
                priority = "high"
                metadata = {
                    "category_id": str(category_id) if category_id else str(category_data.get('_id', '')),
                    "category_name": category_name,
                    "description": category_data.get('description', ''),
                    "previous_status": category_data.get('status', 'active'),
                    "action_type": "category_deleted"
                }
            
            else:
                return  # Unknown action type
            
            # Send the notification
            notification_service.create_notification(
                title=title,
                message=message,
                priority=priority,
                notification_type="system",
                metadata=metadata
            )
            
        except Exception as notification_error:
            # Log the notification error but don't fail the main operation
            print(f"Failed to create {action_type} notification for category: {notification_error}")
            # TODO: Replace with proper logging
    
    # ================================================================
    # CRUD OPERATIONS
    # ================================================================
    
    def create_category(self, category_data):
        """Create a new category"""
        try:
            # Create Category model instance with updated field names
            category = Category(
                category_name=category_data.get("category_name", category_data.get("name", "")),
                description=category_data.get("description", ''),
                status=category_data.get("status", 'active'),
                sub_categories=category_data.get("sub_categories", [])
            )

            # Insert the category using the model's to_dict method
            category_result = self.category_collection.insert_one(category.to_dict())
            created_category = self.category_collection.find_one({'_id': category_result.inserted_id})
            
            # Convert ObjectId for response
            created_category = self.convert_object_id(created_category)
            
            # Send notification
            self._send_category_notification('created', created_category, category_result.inserted_id)

            return created_category
    
        except Exception as e:
            raise Exception(f"Error creating category: {str(e)}")
    
    def get_category_by_id(self, category_id):
        """Get a category by ID"""
        try:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            category = self.category_collection.find_one({'_id': category_id})
            return self.convert_object_id(category) if category else None
        except Exception as e:
            raise Exception(f"Error getting category: {str(e)}")
        
    def get_all_categories(self):
        """Get all categories"""
        try:
            categories = list(self.category_collection.find())
            return [self.convert_object_id(category) for category in categories]
        except Exception as e:
            raise Exception(f"Error getting categories: {str(e)}")
    
    def update_category(self, category_id, update_data):
        """Update a category"""
        try:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            # Get current category data for notification comparison
            old_category = self.category_collection.find_one({'_id': category_id})
            if not old_category:
                return None
            
            old_category = self.convert_object_id(old_category)
            
            # Add last_updated timestamp
            update_data['last_updated'] = datetime.utcnow()
            
            result = self.category_collection.update_one(
                {'_id': category_id},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                # Get updated category
                updated_category = self.category_collection.find_one({'_id': category_id})
                updated_category = self.convert_object_id(updated_category)
                
                # Send notification
                self._send_category_notification('updated', updated_category, category_id, old_category)
                
                return updated_category
            return None
            
        except Exception as e:
            raise Exception(f"Error updating category: {str(e)}")
    
    def delete_category(self, category_id):
        """Delete a category (soft delete by setting status to inactive)"""
        try:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            # Get category data before deletion for notification
            category_to_delete = self.category_collection.find_one({'_id': category_id})
            if not category_to_delete:
                return False
            
            category_to_delete = self.convert_object_id(category_to_delete)
            
            result = self.category_collection.update_one(
                {'_id': category_id},
                {'$set': {'status': 'inactive', 'last_updated': datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                # Send notification
                self._send_category_notification('deleted', category_to_delete, category_id)
                return True
            
            return False
            
        except Exception as e:
            raise Exception(f"Error deleting category: {str(e)}")
    
    # ================================================================
    # SUBCATEGORY OPERATIONS
    # ================================================================
    
    def add_subcategory(self, category_id, subcategory_data):
        """Add a subcategory to the sub_categories array"""
        try:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            # Check if category exists
            category = self.category_collection.find_one({'_id': category_id})
            if not category:
                raise Exception("Category not found")
            
            # Add subcategory to the array
            result = self.category_collection.update_one(
                {'_id': category_id},
                {
                    '$addToSet': {'sub_categories': subcategory_data},
                    '$set': {'last_updated': datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                # Send notification for subcategory addition
                try:
                    notification_service.create_notification(
                        title="Subcategory Added",
                        message=f"New subcategory '{subcategory_data.get('name', 'Unknown')}' added to category '{category.get('category_name', 'Unknown')}'",
                        priority="low",
                        notification_type="system",
                        metadata={
                            "category_id": str(category_id),
                            "category_name": category.get('category_name', 'Unknown'),
                            "subcategory_name": subcategory_data.get('name', 'Unknown'),
                            "action_type": "subcategory_added"
                        }
                    )
                except Exception as notification_error:
                    print(f"Failed to create subcategory addition notification: {notification_error}")
            
            return result.modified_count > 0
            
        except Exception as e:
            raise Exception(f"Error adding subcategory: {str(e)}")
    
    def remove_subcategory(self, category_id, subcategory_data):
        """Remove a subcategory from the sub_categories array"""
        try:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            # Get category data for notification
            category = self.category_collection.find_one({'_id': category_id})
            if not category:
                raise Exception("Category not found")
            
            result = self.category_collection.update_one(
                {'_id': category_id},
                {
                    '$pull': {'sub_categories': subcategory_data},
                    '$set': {'last_updated': datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                # Send notification for subcategory removal
                try:
                    notification_service.create_notification(
                        title="Subcategory Removed",
                        message=f"Subcategory '{subcategory_data.get('name', 'Unknown')}' removed from category '{category.get('category_name', 'Unknown')}'",
                        priority="low",
                        notification_type="system",
                        metadata={
                            "category_id": str(category_id),
                            "category_name": category.get('category_name', 'Unknown'),
                            "subcategory_name": subcategory_data.get('name', 'Unknown'),
                            "action_type": "subcategory_removed"
                        }
                    )
                except Exception as notification_error:
                    print(f"Failed to create subcategory removal notification: {notification_error}")
            
            return result.modified_count > 0
            
        except Exception as e:
            raise Exception(f"Error removing subcategory: {str(e)}")
    
    def get_subcategories(self, category_id):
        """Get all subcategories for a specific category"""
        try:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            category = self.category_collection.find_one(
                {'_id': category_id},
                {'sub_categories': 1}
            )
            
            return category.get('sub_categories', []) if category else []
            
        except Exception as e:
            raise Exception(f"Error getting subcategories: {str(e)}")
    
    # ================================================================
    # QUERY OPERATIONS
    # ================================================================
    
    def get_active_categories(self):
        """Get only active categories"""
        try:
            categories = list(self.category_collection.find({'status': 'active'}))
            return [self.convert_object_id(category) for category in categories]
        except Exception as e:
            raise Exception(f"Error getting active categories: {str(e)}")
    
    def search_categories(self, search_term):
        """Search categories by name or description"""
        try:
            regex_pattern = {'$regex': search_term, '$options': 'i'}
            categories = list(self.category_collection.find({
                '$or': [
                    {'category_name': regex_pattern},
                    {'description': regex_pattern}
                ]
            }))
            return [self.convert_object_id(category) for category in categories]
        except Exception as e:
            raise Exception(f"Error searching categories: {str(e)}")


class CategoryDisplayService:
    def __init__(self):
        self.db = db_manager.get_database()  
        self.category_collection = self.db.category
        self.sales_collection = self.db.sales_log

    # ================================================================
    # DISPLAY METHODS
    # ================================================================

    def get_categories_display(self):
        """Get categories with sales data - FIXED for nested products structure"""
        try:
            # Lines with this symbol (##) are for debugging
            ## print("=== Starting get_categories_display ===")
            
            # Define projection and fetch invoices
            projection = {
                "_id": 1,
                "item_list.item_name": 1,
                "customer_id": 1,
                "transaction_date": 1,
                "payment_method": 1,
                "sales_type": 1,
                "total_amount": 1,
                "item_list.quantity": 1,
                "item_list.unit_price": 1, 
            }
            
            ## print("About to fetch invoices...")
            invoices = list(self.sales_collection.find({}, projection))
            ## print(f"Fetched {len(invoices)} invoices successfully")

            # Create a lookup dictionary for faster searching
            item_sales_lookup = {}
            ## print("Building item sales lookup...")

            # Build the lookup dictionary from invoices
            for invoice in invoices:
                for item in invoice.get('item_list', []):
                    item_name = item['item_name']
                    if item_name not in item_sales_lookup:
                        item_sales_lookup[item_name] = {'quantity': 0, 'total_sales': 0}
                    
                    item_total = round(item['quantity'] * item['unit_price'], 2)
                    item_sales_lookup[item_name]['quantity'] += item['quantity']
                    item_sales_lookup[item_name]['total_sales'] += item_total

            ## print("About to fetch categories...")
            categories = list(self.category_collection.find({}))
            ## print(f"Fetched {len(categories)} categories successfully")
            
            # Create result structure
            categories_with_sales = []

            for category in categories:
                ## print(f"Processing category: {category.get('category_name')}")
                category_name = category['category_name']
                category_total_sales = 0
                category_total_quantity = 0
                subcategories_data = []
                
                # FIXED: Handle nested sub_categories with products
                for subcategory in category.get('sub_categories', []):
                    subcategory_name = subcategory['name']
                    subcategory_total_quantity = 0
                    subcategory_total_sales = 0
                    
                    # NEW: Process products within each subcategory
                    products_in_subcategory = subcategory.get('products', [])
                    ## print(f"  Processing subcategory '{subcategory_name}' with {len(products_in_subcategory)} products")
                    
                    for product_name in products_in_subcategory:
                        # Get sales data for each individual product
                        if product_name in item_sales_lookup:
                            product_data = item_sales_lookup[product_name]
                            subcategory_total_quantity += product_data['quantity']
                            subcategory_total_sales += product_data['total_sales']
                            ## print(f"    Product '{product_name}': {product_data['quantity']} sold, ₱{product_data['total_sales']}")
                        else:
                            print(f"    Product '{product_name}': No sales data found")
                    
                    # Add subcategory totals to category totals
                    category_total_sales += subcategory_total_sales
                    category_total_quantity += subcategory_total_quantity
                    
                    # Add subcategory data to list
                    subcategories_data.append({
                        'name': subcategory_name,
                        'quantity_sold': subcategory_total_quantity,
                        'total_sales': subcategory_total_sales,
                        'product_count': len(products_in_subcategory)  # NEW: Add product count
                    })
                    
                    ## print(f"  Subcategory '{subcategory_name}' totals: {subcategory_total_quantity} sold, ₱{subcategory_total_sales}")
                
                # Add category data to result
                categories_with_sales.append({
                    '_id': str(category['_id']),  # Convert ObjectId to string
                    'category_name': category_name,
                    'description': category.get('description', ''),
                    'status': category.get('status', ''),
                    'date_created': category.get('date_created'),
                    'last_updated': category.get('last_updated'),
                    'total_quantity_sold': category_total_quantity,
                    'total_sales': category_total_sales,
                    'subcategories': subcategories_data,
                    'subcategory_count': len(subcategories_data)  # NEW: Add subcategory count
                })
                
                ## print(f"Category '{category_name}' totals: {category_total_quantity} sold, ₱{category_total_sales}")

            ## print(f"Returning {len(categories_with_sales)} categories with sales data")
            return categories_with_sales
            
        except Exception as e:
            print(f"ERROR in get_categories_display: {e}")
            print(f"ERROR type: {type(e)}")
            import traceback
            print(f"TRACEBACK: {traceback.format_exc()}")
            raise Exception(f"Error getting categories: {str(e)}")

    def get_categories_display_with_date_filter(self, start_date=None, end_date=None, frequency='monthly'):
        """Get categories with sales data filtered by date range"""
        try:
            print(f"=== Starting get_categories_display with date filter: {start_date} to {end_date} ===")
            
            # Build date filter query
            date_filter = {}
            if start_date or end_date:
                date_filter["transaction_date"] = {}
                if start_date:
                    from datetime import datetime, time
                    if isinstance(start_date, str):
                        from django.utils.dateparse import parse_date
                        start_date = parse_date(start_date)
                    if start_date:
                        start_datetime = datetime.combine(start_date, time.min)
                        date_filter["transaction_date"]["$gte"] = start_datetime
                if end_date:
                    if isinstance(end_date, str):
                        from django.utils.dateparse import parse_date
                        end_date = parse_date(end_date)
                    if end_date:
                        end_datetime = datetime.combine(end_date, time.max)
                        date_filter["transaction_date"]["$lte"] = end_datetime
            
            # Apply the filter to the query
            query_filter = date_filter if date_filter else {}
            print(f"MongoDB Query Filter: {query_filter}")
            
            # Define projection and fetch filtered invoices
            projection = {
                "_id": 1,
                "item_list.item_name": 1,
                "customer_id": 1,
                "transaction_date": 1,
                "payment_method": 1,
                "sales_type": 1,
                "total_amount": 1,
                "item_list.quantity": 1,
                "item_list.unit_price": 1, 
            }
            
            invoices = list(self.sales_collection.find(query_filter, projection))
            print(f"Fetched {len(invoices)} invoices for date range")

            # Rest of the logic is the same as get_categories_display()
            # Create a lookup dictionary for faster searching
            item_sales_lookup = {}

            # Build the lookup dictionary from filtered invoices
            for invoice in invoices:
                for item in invoice.get('item_list', []):
                    item_name = item['item_name']
                    if item_name not in item_sales_lookup:
                        item_sales_lookup[item_name] = {'quantity': 0, 'total_sales': 0}
                    
                    item_total = item['quantity'] * item['unit_price']
                    item_sales_lookup[item_name]['quantity'] += item['quantity']
                    item_sales_lookup[item_name]['total_sales'] += item_total

            # Process categories (same logic as above)
            categories = list(self.category_collection.find({}))
            categories_with_sales = []

            for category in categories:
                category_name = category['category_name']
                category_total_sales = 0
                category_total_quantity = 0
                subcategories_data = []
                
                for subcategory in category.get('sub_categories', []):
                    subcategory_name = subcategory['name']
                    subcategory_total_quantity = 0
                    subcategory_total_sales = 0
                    
                    products_in_subcategory = subcategory.get('products', [])
                    
                    for product_name in products_in_subcategory:
                        if product_name in item_sales_lookup:
                            product_data = item_sales_lookup[product_name]
                            subcategory_total_quantity += product_data['quantity']
                            subcategory_total_sales += product_data['total_sales']
                    
                    category_total_sales += subcategory_total_sales
                    category_total_quantity += subcategory_total_quantity
                    
                    subcategories_data.append({
                        'name': subcategory_name,
                        'quantity_sold': subcategory_total_quantity,
                        'total_sales': subcategory_total_sales,
                        'product_count': len(products_in_subcategory)
                    })
                
                categories_with_sales.append({
                    '_id': str(category['_id']),
                    'category_name': category_name,
                    'description': category.get('description', ''),
                    'status': category.get('status', ''),
                    'date_created': category.get('date_created'),
                    'last_updated': category.get('last_updated'),
                    'total_quantity_sold': category_total_quantity,
                    'total_sales': category_total_sales,
                    'subcategories': subcategories_data,
                    'subcategory_count': len(subcategories_data),
                    'date_filter_applied': bool(start_date or end_date),
                    'frequency': frequency
                })

            return {
                'categories': categories_with_sales,
                'total_categories': len(categories_with_sales),
                'date_filter_applied': bool(start_date or end_date),
                'frequency': frequency,
                'total_invoices': len(invoices)
            }
            
        except Exception as e:
            print(f"ERROR in get_categories_display_with_date_filter: {e}")
            import traceback
            print(f"TRACEBACK: {traceback.format_exc()}")
            raise Exception(f"Error getting categories with date filter: {str(e)}")