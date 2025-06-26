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
    
    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    def create_category(self, category_data):
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
            
            try:
                category_name = category.category_name
                
                notification_service.create_notification(
                    title="New Category Created",
                    message=f"A new Category called '{category_name}' has been added to the system",
                    priority="high",
                    notification_type="system",
                    metadata={
                        "category_id": str(category_result.inserted_id),
                        "description": category.description,
                        "category_name": category_name,
                        "registration_source": "category_creation",
                        "action_type": "category_created"
                    }
                )
                
            except Exception as notification_error:
                # Log the notification error but don't fail the category creation
                print(f"Failed to create notification for the new Category: {notification_error}")
                # You can add proper logging here instead of print

            return self.convert_object_id(created_category)
    
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
            
            # Add last_updated timestamp
            update_data['last_updated'] = datetime.utcnow()
            
            result = self.category_collection.update_one(
                {'_id': category_id},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                updated_category = self.category_collection.find_one({'_id': category_id})
                return self.convert_object_id(updated_category)
            return None
            
        except Exception as e:
            raise Exception(f"Error updating category: {str(e)}")
    
    def delete_category(self, category_id):
        """Delete a category (soft delete by setting status to inactive)"""
        try:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            result = self.category_collection.update_one(
                {'_id': category_id},
                {'$set': {'status': 'inactive', 'last_updated': datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            raise Exception(f"Error deleting category: {str(e)}")
        
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
            
            return result.modified_count > 0
            
        except Exception as e:
            raise Exception(f"Error adding subcategory: {str(e)}")
    
    def remove_subcategory(self, category_id, subcategory_data):
        """Remove a subcategory from the sub_categories array"""
        try:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            result = self.category_collection.update_one(
                {'_id': category_id},
                {
                    '$pull': {'sub_categories': subcategory_data},
                    '$set': {'last_updated': datetime.utcnow()}
                }
            )
            
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

    def get_categories_display(self):
        """Get categories with sales data"""
        try:
            print("=== Starting get_categories_display ===")
            
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
            
            print("About to fetch invoices...")
            # Fetch invoices - THIS IS WHERE THE ERROR MIGHT BE
            invoices = list(self.sales_collection.find({}, projection))
            print(f"Fetched {len(invoices)} invoices successfully")

            # Create a lookup dictionary for faster searching
            item_sales_lookup = {}
            print("Building item sales lookup...")

            # Build the lookup dictionary from invoices
            for invoice in invoices:
                print(f"Processing invoice ID: {invoice.get('_id')}")
                for item in invoice.get('item_list', []):
                    item_name = item['item_name']
                    if item_name not in item_sales_lookup:
                        item_sales_lookup[item_name] = {'quantity': 0, 'total_sales': 0}
                    
                    item_total = item['quantity'] * item['unit_price']
                    item_sales_lookup[item_name]['quantity'] += item['quantity']
                    item_sales_lookup[item_name]['total_sales'] += item_total

            print("About to fetch categories...")
            # Now process categories using the lookup - THIS COULD ALSO BE THE ERROR
            categories = list(self.category_collection.find({}))
            print(f"Fetched {len(categories)} categories successfully")
            
            # Create result structure
            categories_with_sales = []

            for category in categories:
                print(f"Processing category: {category.get('category_name')}")
                category_name = category['category_name']
                category_total_sales = 0
                category_total_quantity = 0
                subcategories_data = []
                
                for subcategory in category.get('sub_categories', []):
                    subcategory_name = subcategory['name']
                    
                    # Get data from lookup (much faster)
                    if subcategory_name in item_sales_lookup:
                        subcategory_data = item_sales_lookup[subcategory_name]
                        subcategory_total_quantity = subcategory_data['quantity']
                        subcategory_total_sales = subcategory_data['total_sales']
                    else:
                        subcategory_total_quantity = 0
                        subcategory_total_sales = 0
                    
                    category_total_sales += subcategory_total_sales
                    category_total_quantity += subcategory_total_quantity
                    
                    # Add subcategory data to list
                    subcategories_data.append({
                        'name': subcategory_name,
                        'quantity_sold': subcategory_total_quantity,
                        'total_sales': subcategory_total_sales
                    })
                
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
                    'subcategories': subcategories_data
                })

            print(f"Returning {len(categories_with_sales)} categories with sales data")
            return categories_with_sales
            
        except Exception as e:
            print(f"ERROR in get_categories_display: {e}")
            print(f"ERROR type: {type(e)}")
            import traceback
            print(f"TRACEBACK: {traceback.format_exc()}")
            raise Exception(f"Error getting categories: {str(e)}")