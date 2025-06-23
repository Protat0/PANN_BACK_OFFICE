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
                    priority="medium",
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