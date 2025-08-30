from bson import ObjectId
from datetime import datetime

from ..database import db_manager 
from ..models import Category
import bcrypt
from notifications.services import notification_service
from .audit_service import AuditLogService

class CategoryService:
    def __init__(self):
        self.db = db_manager.get_database()  
        self.category_collection = self.db.category
        
        # ✅ FIXED: Single, clean audit service initialization
        try:
            # Import should be at the top of the file, not inside try block
            self.audit_service = AuditLogService()
            print("✅ Audit service initialized for CategoryService")
        except Exception as e:
            print(f"⚠️ Could not initialize audit service: {e}")
            self.audit_service = None
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
            action_type (str): 'created', 'updated', 'soft_deleted', 'hard_deleted', or 'restored'
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
            
            elif action_type == 'soft_deleted':
                title = "Category Soft Deleted"
                message = f"Category '{category_name}' has been deleted"
                priority = "medium"
                metadata = {
                    "category_id": str(category_id) if category_id else str(category_data.get('_id', '')),
                    "category_name": category_name,
                    "description": category_data.get('description', ''),
                    "previous_status": category_data.get('status', 'active'),
                    "action_type": "category_soft_deleted",
                    "can_restore": True
                }
            
            elif action_type == 'hard_deleted':
                title = "Category Hard Deleted"
                message = f"Category '{category_name}' has been permanently deleted by admin"
                priority = "high"
                metadata = {
                    "category_id": str(category_id) if category_id else str(category_data.get('_id', '')),
                    "category_name": category_name,
                    "description": category_data.get('description', ''),
                    "previous_status": category_data.get('status', 'active'),
                    "action_type": "category_hard_deleted",
                    "can_restore": False
                }
            
            elif action_type == 'restored':
                title = "Category Restored"
                message = f"Category '{category_name}' has been restored from soft delete"
                priority = "medium"
                metadata = {
                    "category_id": str(category_id) if category_id else str(category_data.get('_id', '')),
                    "category_name": category_name,
                    "description": category_data.get('description', ''),
                    "status": category_data.get('status', 'active'),
                    "action_type": "category_restored"
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
    
    def create_category(self, category_data, current_user=None):
        """Create a new category with automatic 'None' subcategory"""
        try:
            # Debug: Print received data
            print(f"\n🔍 CREATE_CATEGORY: Received data keys: {list(category_data.keys())}")
            
            # Check for image fields
            image_fields = ['image_url', 'image_filename', 'image_size', 'image_type', 'image_uploaded_at']
            print("🖼️  Image fields in request:")
            for field in image_fields:
                value = category_data.get(field)
                if value is not None:
                    if field == 'image_url':
                        print(f"  ✅ {field}: Present (length: {len(value)})")
                    else:
                        print(f"  ✅ {field}: {value}")
                else:
                    print(f"  ❌ {field}: Missing/None")
            
            # Get existing sub_categories from input (if any)
            existing_sub_categories = category_data.get("sub_categories", [])
            
            # Create default "None" subcategory
            default_none_subcategory = {
                "name": "None",
                "description": "Products in this category without specific subcategorization",
                "products": [],
                "is_default": True,
                "created_automatically": True,
                "created_at": datetime.utcnow()
            }
            
            # Check if "None" subcategory already exists in the provided data
            none_exists = any(
                sub.get('name', '').lower() == 'none' 
                for sub in existing_sub_categories
            )
            
            # If "None" doesn't exist, add it as the first subcategory
            if not none_exists:
                # Insert at the beginning so "None" appears first
                sub_categories = [default_none_subcategory] + existing_sub_categories
                print(f"✅ Auto-added 'None' subcategory to new category")
            else:
                # Use existing subcategories as-is
                sub_categories = existing_sub_categories
                print(f"ℹ️ 'None' subcategory already exists in provided data")
            
            # Prepare category data for Category model
            category_kwargs = {
                'category_name': category_data.get("category_name", category_data.get("name", "")),
                'description': category_data.get("description", ''),
                'status': category_data.get("status", 'active'),
                'sub_categories': sub_categories,  # Use the updated list with None subcategory
                'isDeleted': False
            }
            
            # ADD IMAGE FIELDS if they exist in the request
            for field in image_fields:
                if field in category_data and category_data[field] is not None:
                    category_kwargs[field] = category_data[field]
                    print(f"✅ Added {field} to category creation")
            
            # Create Category model instance with ALL fields including images
            category = Category(**category_kwargs)
            
            # Debug: Check if category has image
            print(f"📸 Category has image: {category.has_image()}")
            if category.has_image():
                image_info = category.get_image_info()
                print(f"📸 Image info: filename={image_info.get('filename')}, size={image_info.get('size_formatted')}")

            # Insert the category using the model's to_dict method
            category_dict = category.to_dict()
            
            # Debug: Check what's being saved to MongoDB
            print(f"💾 Saving to MongoDB with keys: {list(category_dict.keys())}")
            for field in image_fields:
                if field in category_dict:
                    print(f"  ✅ {field} will be saved to database")
                else:
                    print(f"  ❌ {field} missing from database save")
            
            category_result = self.category_collection.insert_one(category_dict)
            created_category = self.category_collection.find_one({'_id': category_result.inserted_id})
            
            # Debug: Check what was actually saved
            print(f"💾 Saved category keys: {list(created_category.keys())}")
            for field in image_fields:
                if field in created_category:
                    print(f"  ✅ {field} saved successfully")
                else:
                    print(f"  ❌ {field} not found in saved category")
            
            # Convert ObjectId for response
            created_category = self.convert_object_id(created_category)
            
            if current_user:  
                try:
                    audit_category_data = {**created_category, "category_id": str(category_result.inserted_id)}
                    self.audit_service.log_category_create(current_user, audit_category_data)
                    print(f"✅ Audit log created for category creation")
                except Exception as audit_error:
                    print(f"⚠️ Failed to create audit log: {audit_error}")

            # Send notification directly in the method
            try:
                category_name = created_category.get('category_name', 'Unknown Category')
                
                # Check if None subcategory was auto-created
                none_subcategory = next(
                    (sub for sub in sub_categories if sub.get('name') == 'None'), 
                    None
                )
                
                message = f"A new category '{category_name}' has been added to the system"
                if none_subcategory and none_subcategory.get('created_automatically'):
                    message += " with auto-generated 'None' subcategory"
                
                # Include image info in notification metadata
                metadata = {
                    "category_id": str(category_result.inserted_id),
                    "category_name": category_name,
                    "description": created_category.get('description', ''),
                    "status": created_category.get('status', 'active'),
                    "action_type": "category_created",
                    "registration_source": "category_creation",
                    "subcategories_count": len(sub_categories),
                    "has_auto_none_subcategory": bool(none_subcategory and none_subcategory.get('created_automatically')),
                    "subcategories": [sub.get('name') for sub in sub_categories],
                    # ADD IMAGE INFO TO METADATA
                    "has_image": bool(created_category.get('image_url')),
                    "image_filename": created_category.get('image_filename'),
                    "image_size": created_category.get('image_size')
                }
                
                notification_service.create_notification(
                    title="New Category Created",
                    message=message,
                    priority="high",
                    notification_type="system",
                    metadata=metadata
                )
                
            except Exception as notification_error:
                # Log the notification error but don't fail the main operation
                print(f"Failed to create category creation notification: {notification_error}")

            print(f"✅ Category '{category_data.get('category_name')}' created with {len(sub_categories)} subcategories")
            if created_category.get('image_url'):
                print(f"✅ Category created WITH image: {created_category.get('image_filename')}")
            else:
                print(f"ℹ️ Category created WITHOUT image")
            
            return created_category

        except Exception as e:
            print(f"❌ Error creating category: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Error creating category: {str(e)}")
    
    def get_category_by_id(self, category_id, include_deleted=False):
        """
        Get a category by ID
        
        Args:
            category_id: Category ID
            include_deleted: Whether to include soft-deleted categories
        """
        try:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            # Build query filter
            query_filter = {'_id': category_id}
            if not include_deleted:
                query_filter['isDeleted'] = {'$ne': True}  # Exclude soft-deleted
            
            category = self.category_collection.find_one(query_filter)
            return self.convert_object_id(category) if category else None
        except Exception as e:
            raise Exception(f"Error getting category: {str(e)}")
        
    def get_all_categories(self, include_deleted=False):
        """
        Get all categories
        
        Args:
            include_deleted: Whether to include soft-deleted categories
        """
        try:
            # Build query filter
            query_filter = {}
            if not include_deleted:
                query_filter['isDeleted'] = {'$ne': True}  # Exclude soft-deleted
            
            categories = list(self.category_collection.find(query_filter))
            return [self.convert_object_id(category) for category in categories]
        except Exception as e:
            raise Exception(f"Error getting categories: {str(e)}")
    
    def get_active_categories(self, include_deleted=False):
        """
        Get only active categories
        
        Args:
            include_deleted: Whether to include soft-deleted categories
        """
        try:
            # Build query filter
            query_filter = {'status': 'active'}
            if not include_deleted:
                query_filter['isDeleted'] = {'$ne': True}  # Exclude soft-deleted
            
            categories = list(self.category_collection.find(query_filter))
            return [self.convert_object_id(category) for category in categories]
        except Exception as e:
            raise Exception(f"Error getting active categories: {str(e)}")
    
    def get_deleted_categories(self):
        """Get only soft-deleted categories (for admin restore functionality)"""
        try:
            categories = list(self.category_collection.find({'isDeleted': True}))
            return [self.convert_object_id(category) for category in categories]
        except Exception as e:
            raise Exception(f"Error getting deleted categories: {str(e)}")
    
    def update_category(self, category_id, update_data, current_user=None):
        """Update a category with audit logging"""
        try:
            print(f"🔍 Updating category {category_id}")
            print(f"🔍 Update data: {update_data}")
            if current_user:
                print(f"🔍 User: {current_user['username']}")
            
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            # Get old category data for audit logging
            old_category = self.category_collection.find_one({
                '_id': category_id,
                'isDeleted': {'$ne': True}
            })
            
            if not old_category:
                raise Exception("Category not found or is deleted")
            
            # Add last_updated timestamp
            update_data['last_updated'] = datetime.utcnow()
            
            # Update the category
            result = self.category_collection.update_one(
                {'_id': category_id},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                # Send notification for category update
                try:
                    notification_service.create_notification(
                        title="Category Updated",
                        message=f"Category '{old_category.get('category_name', 'Unknown')}' has been updated",
                        priority="low",
                        notification_type="system",
                        metadata={
                            "category_id": str(category_id),
                            "category_name": old_category.get('category_name', 'Unknown'),
                            "updated_fields": list(update_data.keys()),
                            "action_type": "category_updated"
                        }
                    )
                except Exception as notification_error:
                    print(f"Failed to create category update notification: {notification_error}")
                
                # Audit logging for successful update
                if current_user and hasattr(self, 'audit_service'):
                    try:
                        # Create audit log for category update
                        self.audit_service.log_category_update(
                            current_user, 
                            category_id, 
                            old_values=old_category, 
                            new_values=update_data
                        )
                        print(f"✅ Audit log created for category update")
                    except Exception as audit_error:
                        print(f"❌ Audit logging failed: {audit_error}")
            
            # Return updated category
            if result.modified_count > 0:
                updated_category = self.category_collection.find_one({'_id': category_id})
                return self.convert_object_id(updated_category)
            
            return None
            
        except Exception as e:
            raise Exception(f"Error updating category: {str(e)}")
    
    # ================================================================
    # DELETE OPERATIONS (NEW - SOFT AND HARD DELETE)
    # ================================================================
    
    def soft_delete_category(self, category_id, current_user=None):
        """Soft delete a category with audit logging"""
        try:
            print(f"🔍 Soft deleting category {category_id}")
            if current_user:
                print(f"🔍 User: {current_user['username']}")
            
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            # Get category data before deletion for audit logging
            category = self.category_collection.find_one({
                '_id': category_id,
                'isDeleted': {'$ne': True}
            })
            
            if not category:
                raise Exception("Category not found or already deleted")
            
            # Soft delete the category
            result = self.category_collection.update_one(
                {'_id': category_id},
                {
                    '$set': {
                        'isDeleted': True,
                        'deleted_at': datetime.utcnow(),
                        'last_updated': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                # Send notification for category deletion
                try:
                    notification_service.create_notification(
                        title="Category Deleted",
                        message=f"Category '{category.get('category_name', 'Unknown')}' has been soft deleted",
                        priority="medium",
                        notification_type="system",
                        metadata={
                            "category_id": str(category_id),
                            "category_name": category.get('category_name', 'Unknown'),
                            "action_type": "category_soft_deleted",
                            "can_restore": True
                        }
                    )
                except Exception as notification_error:
                    print(f"Failed to create category deletion notification: {notification_error}")
                
                # Audit logging for successful soft delete
                if current_user and hasattr(self, 'audit_service'):
                    try:
                        # Create audit log for category soft delete
                        category_for_audit = category.copy()
                        category_for_audit['deletion_type'] = 'soft_delete'
                        
                        self.audit_service.log_category_delete(current_user, category_for_audit)
                        print(f"✅ Audit log created for category soft delete")
                    except Exception as audit_error:
                        print(f"❌ Audit logging failed: {audit_error}")
            
            return result.modified_count > 0
            
        except Exception as e:
            raise Exception(f"Error soft deleting category: {str(e)}")
    
    def hard_delete_category(self, category_id, admin_user_id=None, current_user=None):
        """Hard delete a category with audit logging (Admin only)"""
        try:
            print(f"🔍 Hard deleting category {category_id}")
            if current_user:
                print(f"🔍 Admin user: {current_user['username']}")
            
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            # Get category data before deletion for audit logging
            category = self.category_collection.find_one({'_id': category_id})
            
            if not category:
                raise Exception("Category not found")
            
            # Hard delete the category (permanent removal)
            result = self.category_collection.delete_one({'_id': category_id})
            
            if result.deleted_count > 0:
                # Send notification for category hard deletion
                try:
                    notification_service.create_notification(
                        title="Category Permanently Deleted",
                        message=f"Category '{category.get('category_name', 'Unknown')}' has been permanently deleted by admin",
                        priority="high",
                        notification_type="system",
                        metadata={
                            "category_id": str(category_id),
                            "category_name": category.get('category_name', 'Unknown'),
                            "action_type": "category_hard_deleted",
                            "admin_user_id": admin_user_id,
                            "can_restore": False
                        }
                    )
                except Exception as notification_error:
                    print(f"Failed to create category hard deletion notification: {notification_error}")
                
                # Audit logging for successful hard delete
                if current_user and hasattr(self, 'audit_service'):
                    try:
                        # Create audit log for category hard delete
                        category_for_audit = category.copy()
                        category_for_audit['deletion_type'] = 'hard_delete'
                        category_for_audit['admin_user_id'] = admin_user_id
                        
                        self.audit_service.log_category_delete(current_user, category_for_audit)
                        print(f"✅ Audit log created for category hard delete")
                    except Exception as audit_error:
                        print(f"❌ Audit logging failed: {audit_error}")
            
            return result.deleted_count > 0
            
        except Exception as e:
            raise Exception(f"Error hard deleting category: {str(e)}")
    
    def restore_category(self, category_id):
        """
        Restore a soft-deleted category (sets isDeleted to False)
        """
        try:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            # Get category data
            category_to_restore = self.category_collection.find_one({'_id': category_id})
            if not category_to_restore:
                return False
            
            # Check if it's actually soft deleted
            if not category_to_restore.get('isDeleted', False):
                raise Exception("Category is not soft deleted")
            
            category_to_restore = self.convert_object_id(category_to_restore)
            
            # Restore the category
            result = self.category_collection.update_one(
                {'_id': category_id},
                {
                    '$set': {
                        'isDeleted': False,
                        'restored_at': datetime.utcnow(),
                        'last_updated': datetime.utcnow()
                    },
                    '$unset': {
                        'deleted_at': ""  # Remove the deleted_at timestamp
                    }
                }
            )
            
            if result.modified_count > 0:
                # Get updated category data
                restored_category = self.category_collection.find_one({'_id': category_id})
                restored_category = self.convert_object_id(restored_category)
                
                # Send notification
                self._send_category_notification('restored', restored_category, category_id)
                return restored_category
            
            return False
            
        except Exception as e:
            raise Exception(f"Error restoring category: {str(e)}")
    
    def delete_category(self, category_id):
        """
        Legacy delete method - now performs soft delete for backward compatibility
        Use soft_delete_category() or hard_delete_category() for explicit control
        """
        return self.soft_delete_category(category_id)
    
    # ================================================================
    # SUBCATEGORY OPERATIONS
    # ================================================================
    
    def add_subcategory(self, category_id, subcategory_data, current_user=None):
        """Add a subcategory to the sub_categories array"""
        try:
            print(f"🔍 Adding subcategory to category {category_id}")
            print(f"🔍 Subcategory data: {subcategory_data}")
            if current_user:
                print(f"🔍 User: {current_user['username']}")
            
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            # Check if category exists and is not deleted
            category = self.category_collection.find_one({
                '_id': category_id,
                'isDeleted': {'$ne': True}
            })
            if not category:
                raise Exception("Category not found or is deleted")
            
            # Add subcategory to the array
            result = self.category_collection.update_one(
                {'_id': category_id},
                {
                    '$addToSet': {'sub_categories': subcategory_data},
                    '$set': {'last_updated': datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                # ✅ FIXED: Send notification for subcategory addition
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
                
                # ✅ FIXED: Audit logging moved inside the success block
                if current_user and hasattr(self, 'audit_service'):
                    try:
                        # Create audit log for subcategory addition
                        self.audit_service.log_category_update(
                            current_user, 
                            category_id, 
                            old_values={}, 
                            new_values={"subcategory_added": subcategory_data}
                        )
                        print(f"✅ Audit log created for subcategory addition")
                    except Exception as audit_error:
                        print(f"❌ Audit logging failed: {audit_error}")
            
            return result.modified_count > 0
            
        except Exception as e:
            raise Exception(f"Error adding subcategory: {str(e)}")
    
    def remove_subcategory(self, category_id, subcategory_data, current_user=None):
        """Remove a subcategory from the sub_categories array"""
        try:
            print(f"🔍 Removing subcategory from category {category_id}")
            print(f"🔍 Subcategory data: {subcategory_data}")
            if current_user:
                print(f"🔍 User: {current_user['username']}")
            
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            # Check if category exists and is not deleted
            category = self.category_collection.find_one({
                '_id': category_id,
                'isDeleted': {'$ne': True}
            })
            if not category:
                raise Exception("Category not found or is deleted")
            
            # Remove subcategory from the array
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
                
                # Audit logging for successful removal
                if current_user and hasattr(self, 'audit_service'):
                    try:
                        # Create audit log for subcategory removal
                        self.audit_service.log_category_update(
                            current_user, 
                            category_id, 
                            old_values={"subcategory_removed": subcategory_data}, 
                            new_values={}
                        )
                        print(f"✅ Audit log created for subcategory removal")
                    except Exception as audit_error:
                        print(f"❌ Audit logging failed: {audit_error}")
            
            return result.modified_count > 0
            
        except Exception as e:
            raise Exception(f"Error removing subcategory: {str(e)}")
    
    def get_subcategories(self, category_id):
        """Get all subcategories for a specific category"""
        try:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            category = self.category_collection.find_one(
                {
                    '_id': category_id,
                    'isDeleted': {'$ne': True}
                },
                {'sub_categories': 1}
            )
            
            return category.get('sub_categories', []) if category else []
            
        except Exception as e:
            raise Exception(f"Error getting subcategories: {str(e)}")
    
    # ================================================================
    # QUERY OPERATIONS
    # ================================================================
    
    def search_categories(self, search_term, include_deleted=False):
        """
        Search categories by name or description
        
        Args:
            search_term: Search term
            include_deleted: Whether to include soft-deleted categories
        """
        try:
            regex_pattern = {'$regex': search_term, '$options': 'i'}
            
            # Build query filter
            query_filter = {
                '$or': [
                    {'category_name': regex_pattern},
                    {'description': regex_pattern}
                ]
            }
            
            if not include_deleted:
                query_filter['isDeleted'] = {'$ne': True}  # Exclude soft-deleted
            
            categories = list(self.category_collection.find(query_filter))
            return [self.convert_object_id(category) for category in categories]
        except Exception as e:
            raise Exception(f"Error searching categories: {str(e)}")
    
    # ================================================================
    # UTILITY METHODS FOR DELETE OPERATIONS
    # ================================================================
    
    def get_category_delete_info(self, category_id):
        """
        Get information about a category before deletion (for confirmation dialogs)
        """
        try:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            category = self.category_collection.find_one({'_id': category_id})
            if not category:
                return None
            
            # Count subcategories and products
            subcategories_count = len(category.get('sub_categories', []))
            products_count = 0
            
            for subcategory in category.get('sub_categories', []):
                products_count += len(subcategory.get('products', []))
            
            return {
                'category_id': str(category['_id']),
                'category_name': category.get('category_name', 'Unknown'),
                'description': category.get('description', ''),
                'status': category.get('status', 'active'),
                'isDeleted': category.get('isDeleted', False),
                'subcategories_count': subcategories_count,
                'products_count': products_count,
                'can_soft_delete': not category.get('isDeleted', False),
                'can_restore': category.get('isDeleted', False),
                'created_at': category.get('date_created'),
                'last_updated': category.get('last_updated'),
                'deleted_at': category.get('deleted_at')
            }
            
        except Exception as e:
            raise Exception(f"Error getting category delete info: {str(e)}")
    
    def bulk_soft_delete_categories(self, category_ids):
        """
        Soft delete multiple categories at once
        
        Args:
            category_ids: List of category IDs to soft delete
        """
        try:
            if not category_ids:
                return {'success': 0, 'failed': 0, 'errors': []}
            
            # Convert string IDs to ObjectId
            object_ids = []
            for cat_id in category_ids:
                if isinstance(cat_id, str):
                    object_ids.append(ObjectId(cat_id))
                else:
                    object_ids.append(cat_id)
            
            # Get categories that can be soft deleted
            categories_to_delete = list(self.category_collection.find({
                '_id': {'$in': object_ids},
                'isDeleted': {'$ne': True}
            }))
            
            success_count = 0
            failed_count = 0
            errors = []
            
            for category in categories_to_delete:
                try:
                    result = self.soft_delete_category(category['_id'])
                    if result:
                        success_count += 1
                    else:
                        failed_count += 1
                        errors.append(f"Failed to soft delete {category.get('category_name', 'Unknown')}")
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Error deleting {category.get('category_name', 'Unknown')}: {str(e)}")
            
            return {
                'success': success_count,
                'failed': failed_count,
                'errors': errors,
                'total_requested': len(category_ids)
            }
            
        except Exception as e:
            raise Exception(f"Error in bulk soft delete: {str(e)}")
    
    def _is_admin_user(self, user_id):
        """
        Check if user is admin (placeholder for actual admin check)
        TODO: Implement actual admin permission check
        """
        # This should check your user/permission system
        # For now, returning True as placeholder
        return True

class CategoryDisplayService:
    def __init__(self):
        self.db = db_manager.get_database()  
        self.category_collection = self.db.category
        self.sales_collection = self.db.sales_log
        try:
            from .audit_service import AuditLogService
            self.audit_service = AuditLogService()
            print("✅ Audit service initialized for CategoryService")
        except Exception as e:
            print(f"⚠️ Could not initialize audit service: {e}")
            self.audit_service = None
    # ================================================================
    # DISPLAY METHODS
    # ================================================================

    def get_categories_display(self, include_deleted=False):
        """
        Get categories with sales data - Updated to support soft delete
        
        Args:
            include_deleted: Whether to include soft-deleted categories
        """
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
            
            # Build query filter for categories
            category_filter = {}
            if not include_deleted:
                category_filter['isDeleted'] = {'$ne': True}  # Exclude soft-deleted categories
            
            categories = list(self.category_collection.find(category_filter))
            ## print(f"Fetched {len(categories)} categories successfully (include_deleted: {include_deleted})")
            
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
                    'isDeleted': category.get('isDeleted', False),  # NEW: Include delete status
                    'deleted_at': category.get('deleted_at'),  # NEW: Include deletion timestamp
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

    def get_categories_display_with_date_filter(self, start_date=None, end_date=None, frequency='monthly', include_deleted=False):
        """
        Get categories with sales data filtered by date range - Updated to support soft delete
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering  
            frequency: Frequency for grouping ('monthly', 'weekly', etc.)
            include_deleted: Whether to include soft-deleted categories
        """
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

            # Process categories (same logic as above but with delete filter)
            category_filter = {}
            if not include_deleted:
                category_filter['isDeleted'] = {'$ne': True}  # Exclude soft-deleted categories
                
            categories = list(self.category_collection.find(category_filter))
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
                    'isDeleted': category.get('isDeleted', False),  # NEW: Include delete status
                    'deleted_at': category.get('deleted_at'),  # NEW: Include deletion timestamp
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
                'total_invoices': len(invoices),
                'include_deleted': include_deleted  # NEW: Include this info in response
            }
            
        except Exception as e:
            print(f"ERROR in get_categories_display_with_date_filter: {e}")
            import traceback
            print(f"TRACEBACK: {traceback.format_exc()}")
            raise Exception(f"Error getting categories with date filter: {str(e)}")
    
    # ================================================================
    # EXPORT OPERATIONS (Updated to support soft delete)
    # ================================================================

    def export_categories_csv(self, include_sales_data=True, date_filter=None, include_deleted=False):
        """
        Export categories to CSV format with optional sales data - Updated to support soft delete
        
        Args:
            include_sales_data: Whether to include sales data
            date_filter: Date filter parameters
            include_deleted: Whether to include soft-deleted categories
        """
        try:
            import csv
            from io import StringIO
            
            # Get categories data
            if include_sales_data:
                # Use the display service for enriched data
                if date_filter:
                    result = self.get_categories_display_with_date_filter(
                        start_date=date_filter.get('start_date'),
                        end_date=date_filter.get('end_date'),
                        frequency=date_filter.get('frequency', 'monthly'),
                        include_deleted=include_deleted
                    )
                    categories = result.get('categories', [])
                else:
                    categories = self.get_categories_display(include_deleted=include_deleted)
            else:
                # Basic category data only - need to get from CategoryService
                category_service = CategoryService()
                categories = category_service.get_all_categories(include_deleted=include_deleted)
            
            # Create CSV content
            output = StringIO()
            writer = csv.writer(output)
            
            # Define headers (updated to include delete status)
            if include_sales_data:
                headers = [
                    'ID',
                    'Category Name', 
                    'Description', 
                    'Status',
                    'Is Deleted',  # NEW
                    'Deleted At',  # NEW
                    'Sub-Categories Count', 
                    'Sub-Categories', 
                    'Total Products',
                    'Total Quantity Sold',
                    'Total Sales (₱)',
                    'Date Created', 
                    'Last Updated'
                ]
            else:
                headers = [
                    'ID',
                    'Category Name', 
                    'Description', 
                    'Status',
                    'Is Deleted',  # NEW
                    'Deleted At',  # NEW
                    'Sub-Categories Count', 
                    'Sub-Categories', 
                    'Total Products',
                    'Date Created', 
                    'Last Updated'
                ]
            
            writer.writerow(headers)
            
            # Write category data
            for category in categories:
                # Calculate sub-categories info
                sub_categories = category.get('sub_categories', []) or category.get('subcategories', [])
                sub_categories_count = len(sub_categories)
                
                # Format sub-categories names
                if sub_categories_count > 0:
                    sub_category_names = '; '.join([sub.get('name', 'Unknown') for sub in sub_categories])
                else:
                    sub_category_names = 'None'
                
                # Calculate total products
                total_products = 0
                if include_sales_data and 'subcategories' in category:
                    # From display service data
                    total_products = sum(sub.get('product_count', 0) for sub in category.get('subcategories', []))
                elif 'sub_categories' in category:
                    # From basic category data
                    total_products = sum(len(sub.get('products', [])) for sub in category.get('sub_categories', []))
                
                # Format dates
                date_created = self._format_export_date(category.get('date_created'))
                last_updated = self._format_export_date(category.get('last_updated'))
                deleted_at = self._format_export_date(category.get('deleted_at')) if category.get('deleted_at') else 'N/A'
                
                # Build row data
                if include_sales_data:
                    row = [
                        category.get('_id', '')[-6:] if category.get('_id') else 'N/A',  # Last 6 chars of ID
                        category.get('category_name', ''),
                        category.get('description', ''),
                        category.get('status', 'active'),
                        'Yes' if category.get('isDeleted', False) else 'No',  # NEW
                        deleted_at,  # NEW
                        sub_categories_count,
                        sub_category_names,
                        total_products,
                        category.get('total_quantity_sold', 0),
                        f"{category.get('total_sales', 0):.2f}",
                        date_created,
                        last_updated
                    ]
                else:
                    row = [
                        category.get('_id', '')[-6:] if category.get('_id') else 'N/A',
                        category.get('category_name', ''),
                        category.get('description', ''),
                        category.get('status', 'active'),
                        'Yes' if category.get('isDeleted', False) else 'No',  # NEW
                        deleted_at,  # NEW
                        sub_categories_count,
                        sub_category_names,
                        total_products,
                        date_created,
                        last_updated
                    ]
                
                writer.writerow(row)
            
            # Get CSV content
            csv_content = output.getvalue()
            output.close()
            
            return {
                'content': csv_content,
                'filename': f"categories_export_{datetime.now().strftime('%Y-%m-%d')}.csv",
                'content_type': 'text/csv',
                'total_records': len(categories),
                'include_deleted': include_deleted  # NEW: Include this info
            }
            
        except Exception as e:
            raise Exception(f"Error exporting categories to CSV: {str(e)}")

    def export_categories_json(self, include_sales_data=True, date_filter=None, include_deleted=False):
        """
        Export categories to JSON format with optional sales data - Updated to support soft delete
        
        Args:
            include_sales_data: Whether to include sales data
            date_filter: Date filter parameters
            include_deleted: Whether to include soft-deleted categories
        """
        try:
            import json
            
            # Get categories data (same logic as CSV export)
            if include_sales_data:
                if date_filter:
                    result = self.get_categories_display_with_date_filter(
                        start_date=date_filter.get('start_date'),
                        end_date=date_filter.get('end_date'),
                        frequency=date_filter.get('frequency', 'monthly'),
                        include_deleted=include_deleted
                    )
                    categories = result.get('categories', [])
                    export_metadata = {
                        'total_categories': result.get('total_categories', 0),
                        'date_filter_applied': result.get('date_filter_applied', False),
                        'frequency': result.get('frequency', 'monthly'),
                        'total_invoices': result.get('total_invoices', 0),
                        'include_deleted': result.get('include_deleted', False)
                    }
                else:
                    categories = self.get_categories_display(include_deleted=include_deleted)
                    export_metadata = {
                        'total_categories': len(categories),
                        'date_filter_applied': False,
                        'include_deleted': include_deleted
                    }
            else:
                category_service = CategoryService()
                categories = category_service.get_all_categories(include_deleted=include_deleted)
                export_metadata = {
                    'total_categories': len(categories),
                    'date_filter_applied': False,
                    'include_deleted': include_deleted
                }
            
            # Prepare export data
            export_data = {
                'export_info': {
                    'exported_at': datetime.now().isoformat(),
                    'format': 'json',
                    'include_sales_data': include_sales_data,
                    **export_metadata
                },
                'categories': categories
            }
            
            # Convert to JSON
            json_content = json.dumps(export_data, indent=2, default=str)
            
            return {
                'content': json_content,
                'filename': f"categories_export_{datetime.now().strftime('%Y-%m-%d')}.json",
                'content_type': 'application/json',
                'total_records': len(categories),
                'include_deleted': include_deleted  # NEW: Include this info
            }
            
        except Exception as e:
            raise Exception(f"Error exporting categories to JSON: {str(e)}")

    def _format_export_date(self, date_value):
        """Helper method to format dates for export"""
        if not date_value:
            return 'N/A'
        
        try:
            if isinstance(date_value, str):
                # Try to parse string date
                try:
                    date_obj = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                except:
                    return date_value  # Return as-is if parsing fails
            elif isinstance(date_value, datetime):
                date_obj = date_value
            else:
                return 'Invalid Date'
            
            # Format as: "27-Jun-2025 09:00 AM"
            return date_obj.strftime('%d-%b-%Y %I:%M %p')
            
        except Exception:
            return 'Invalid Date'

    # ================================================================
    # EXPORT UTILITY METHODS (Updated)
    # ================================================================

    def get_export_stats(self, include_deleted=False):
        """
        Get statistics for export operations - Updated to support soft delete
        
        Args:
            include_deleted: Whether to include soft-deleted categories in stats
        """
        try:
            # Build base filter
            base_filter = {}
            if not include_deleted:
                base_filter['isDeleted'] = {'$ne': True}
            
            # Get category counts
            total_categories = self.category_collection.count_documents(base_filter)
            
            active_filter = {**base_filter, 'status': 'active'}
            active_categories = self.category_collection.count_documents(active_filter)
            
            inactive_filter = {**base_filter, 'status': 'inactive'}
            inactive_categories = self.category_collection.count_documents(inactive_filter)
            
            # Get soft-deleted count
            deleted_categories = self.category_collection.count_documents({'isDeleted': True})
            
            # Count total subcategories and products
            pipeline = [
                {'$match': base_filter},  # Apply delete filter
                {
                    '$project': {
                        'subcategory_count': {'$size': {'$ifNull': ['$sub_categories', []]}},
                        'product_count': {
                            '$sum': {
                                '$map': {
                                    'input': {'$ifNull': ['$sub_categories', []]},
                                    'as': 'sub',
                                    'in': {'$size': {'$ifNull': ['$sub.products', []]}}
                                }
                            }
                        }
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'total_subcategories': {'$sum': '$subcategory_count'},
                        'total_products': {'$sum': '$product_count'}
                    }
                }
            ]
            
            stats_result = list(self.category_collection.aggregate(pipeline))
            stats = stats_result[0] if stats_result else {'total_subcategories': 0, 'total_products': 0}
            
            return {
                'total_categories': total_categories,
                'active_categories': active_categories,
                'inactive_categories': inactive_categories,
                'deleted_categories': deleted_categories,  # NEW: Soft-deleted count
                'total_subcategories': stats['total_subcategories'],
                'total_products': stats['total_products'],
                'include_deleted': include_deleted,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Error getting export stats: {str(e)}")

    def validate_export_params(self, format_type, include_sales_data, date_filter, include_deleted=False):
        """
        Validate export parameters - Updated to include delete parameter
        
        Args:
            format_type: Export format ('csv' or 'json')
            include_sales_data: Whether to include sales data
            date_filter: Date filter parameters
            include_deleted: Whether to include soft-deleted categories
        """
        try:
            # Validate format
            valid_formats = ['csv', 'json']
            if format_type not in valid_formats:
                raise ValueError(f"Invalid format. Must be one of: {', '.join(valid_formats)}")
            
            # Validate include_sales_data
            if not isinstance(include_sales_data, bool):
                raise ValueError("include_sales_data must be a boolean")
            
            # Validate include_deleted
            if not isinstance(include_deleted, bool):
                raise ValueError("include_deleted must be a boolean")
            
            # Validate date_filter if provided
            if date_filter:
                if not isinstance(date_filter, dict):
                    raise ValueError("date_filter must be a dictionary")
                
                # Check date format if dates are provided
                for date_key in ['start_date', 'end_date']:
                    if date_key in date_filter and date_filter[date_key]:
                        try:
                            if isinstance(date_filter[date_key], str):
                                datetime.fromisoformat(date_filter[date_key])
                        except ValueError:
                            raise ValueError(f"Invalid {date_key} format. Use ISO format (YYYY-MM-DD)")
            
            return True
            
        except Exception as e:
            raise Exception(f"Export parameter validation failed: {str(e)}")
            
    # ================================================================
    # NEW METHODS FOR DELETE MANAGEMENT
    # ================================================================
    
    def get_deleted_categories_display(self):
        """Get only soft-deleted categories with sales data (for admin recovery)"""
        try:
            return self.get_categories_display(include_deleted=True)
        except Exception as e:
            raise Exception(f"Error getting deleted categories display: {str(e)}")
    
    def get_category_deletion_impact(self, category_id):
        """
        Get the impact analysis for deleting a category
        (shows subcategories, products, sales data that would be affected)
        """
        try:
            category_service = CategoryService()
            return category_service.get_category_delete_info(category_id)
        except Exception as e:
            raise Exception(f"Error getting category deletion impact: {str(e)}")
        
class ProductSubcategoryService:
    # Constants inside the class
    UNCATEGORIZED_CATEGORY_NAME = "Uncategorized"
    UNCATEGORIZED_SUBCATEGORY_NAME = "General"
    UNCATEGORIZED_CATEGORY_ID = '686a4de143821e2b21f725c6'
    
    def __init__(self):
        self.db = db_manager.get_database()  
        self.category_collection = self.db.category
        self.product_collection = self.db.products
        try:
            from .audit_service import AuditLogService
            self.audit_service = AuditLogService()
            print("✅ Audit service initialized for CategoryService")
        except Exception as e:
            print(f"⚠️ Could not initialize audit service: {e}")
            self.audit_service = None
    
    def update_product_subcategory(self, product_id, new_subcategory, category_id, current_user=None):
        """
        Updated method: Handle "None" as a real subcategory name
        """
        try:
            print(f"🔍 DEBUG: Starting product-centric update")
            print(f"  - product_id: {product_id}")
            print(f"  - new_subcategory: {new_subcategory}")
            print(f"  - category_id: {category_id}")
            
            # Convert IDs to ObjectId
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            if isinstance(product_id, str):
                product_obj_id = ObjectId(product_id)
            
            # 1. FIND THE PRODUCT BY ID
            product = self.product_collection.find_one({'_id': product_obj_id})
            if not product:
                raise Exception(f"Product with ID {product_id} not found in products collection")
            
            product_name = product.get('product_name')
            if not product_name:
                raise Exception(f"Product {product_id} has no product_name")
            
            print(f"✅ Found product: {product_name}")
            
            # 2. GET TARGET CATEGORY
            target_category = self.category_collection.find_one({
                '_id': category_id,
                'isDeleted': {'$ne': True}
            })
            
            if not target_category:
                raise Exception("Target category not found or is deleted")
            
            print(f"✅ Found target category: {target_category.get('category_name')}")
            
            # 3. FIND CURRENT CATEGORY (where this product currently exists)
            current_category = self.category_collection.find_one({
                'sub_categories.products': product_name,
                'isDeleted': {'$ne': True}
            })
            
            current_subcategory = None
            if current_category:
                # Find which subcategory contains the product
                for subcategory in current_category.get('sub_categories', []):
                    if product_name in subcategory.get('products', []):
                        current_subcategory = subcategory['name']
                        break
                        
                print(f"✅ Found in category: {current_category.get('category_name')} > {current_subcategory}")
            else:
                print(f"ℹ️ Product not currently in any category")
            
            # 4. UPDATED LOGIC: Handle "None" as a real subcategory
            if not new_subcategory or new_subcategory.strip() == '':
                # Only move to Uncategorized if subcategory is actually empty/null
                return self._move_to_uncategorized_category(
                    product_id, 
                    product_name, 
                    current_category, 
                    current_subcategory,
                    current_user
                )
            else:
                # Treat "None" as a real subcategory name, not a special case
                return self._move_product_to_subcategory(
                    product_id, 
                    product_name, 
                    target_category, 
                    new_subcategory,  # "None" is treated as a real subcategory
                    current_category,
                    current_subcategory,
                    current_user
                )
                
        except Exception as e:
            print(f"❌ Error in product-centric update: {str(e)}")
            raise Exception(f"Error updating product subcategory: {str(e)}")
    
    def _move_to_uncategorized_category(self, product_id, product_name, current_category=None, current_subcategory=None, current_user=None):
        """
        Move a product to the special 'Uncategorized' category
        """
        try:
            print(f"🔄 Moving {product_name} to Uncategorized category")
            
            # Ensure uncategorized category exists
            uncategorized_category = self._ensure_uncategorized_category_exists()
            
            # Remove from current category (if exists)
            if current_category and current_subcategory:
                self.category_collection.update_one(
                    {'_id': current_category['_id']},
                    {
                        '$pull': {
                            'sub_categories.$[elem].products': product_name
                        }
                    },
                    array_filters=[{'elem.name': current_subcategory}]
                )
                print(f"🗑️ Removed from {current_category.get('category_name')} > {current_subcategory}")
            
            # Add to uncategorized category
            result = self.category_collection.update_one(
                {'_id': ObjectId(uncategorized_category['_id'])},
                {
                    '$addToSet': {
                        'sub_categories.$[elem].products': product_name
                    },
                    '$set': {
                        'last_updated': datetime.utcnow()
                    }
                },
                array_filters=[{'elem.name': self.UNCATEGORIZED_SUBCATEGORY_NAME}]
            )
            
            if result.modified_count > 0:
                # Update product document
                self.product_collection.update_one(
                    {'_id': ObjectId(product_id)},
                    {
                        '$set': {
                            'category_id': uncategorized_category['_id'],
                            'subcategory': self.UNCATEGORIZED_SUBCATEGORY_NAME,
                            'updated_at': datetime.utcnow(),
                            'is_uncategorized': True
                        }
                    }
                )
                
                print(f"✅ Moved {product_name} to Uncategorized > General")
                
                return {
                    'success': True,
                    'action': 'moved_to_uncategorized',
                    'product_id': product_id,
                    'old_category': current_category.get('category_name') if current_category else None,
                    'old_subcategory': current_subcategory,
                    'new_category': self.UNCATEGORIZED_CATEGORY_NAME,
                    'new_subcategory': self.UNCATEGORIZED_SUBCATEGORY_NAME,
                    'message': f"Product moved to {self.UNCATEGORIZED_CATEGORY_NAME} category"
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to move product to uncategorized category'
                }
                
        except Exception as e:
            raise Exception(f"Error moving to uncategorized category: {str(e)}")
    
    def _move_product_to_subcategory(self, product_id, product_name, target_category, new_subcategory, current_category, current_subcategory, current_user=None):
        """Move product to a specific subcategory"""
        try:
            # Check if target subcategory exists
            target_subcategory_exists = any(
                sub['name'] == new_subcategory 
                for sub in target_category.get('sub_categories', [])
            )
            
            if not target_subcategory_exists:
                raise Exception(f"Subcategory '{new_subcategory}' does not exist in category '{target_category.get('category_name')}'")
            
            # Check if it's the same location (no change needed)
            if (current_category and 
                str(current_category['_id']) == str(target_category['_id']) and 
                current_subcategory == new_subcategory):
                return {
                    'success': True,
                    'action': 'no_change',
                    'product_id': product_id,
                    'category_name': target_category.get('category_name'),
                    'subcategory': new_subcategory,
                    'message': f"Product is already in {target_category.get('category_name')} > {new_subcategory}"
                }
            
            # Step 1: Remove from current location (if exists)
            if current_category:
                self.category_collection.update_one(
                    {'_id': current_category['_id']},
                    {
                        '$pull': {
                            'sub_categories.$[elem].products': product_name
                        }
                    },
                    array_filters=[{'elem.name': current_subcategory}]
                )
                print(f"🔄 Removed from {current_category.get('category_name')} > {current_subcategory}")
            
            # Step 2: Add to new location
            result = self.category_collection.update_one(
                {'_id': target_category['_id']},
                {
                    '$addToSet': {
                        'sub_categories.$[elem].products': product_name
                    },
                    '$set': {
                        'last_updated': datetime.utcnow()
                    }
                },
                array_filters=[{'elem.name': new_subcategory}]
            )
            
            if result.modified_count > 0:
                # Step 3: Update product document with new category reference
                self.product_collection.update_one(
                    {'_id': ObjectId(product_id)},
                    {
                        '$set': {
                            'category_id': str(target_category['_id']),
                            'subcategory': new_subcategory,
                            'updated_at': datetime.utcnow()
                        }
                    }
                )
                
                print(f"✅ Moved to {target_category.get('category_name')} > {new_subcategory}")
                
                return {
                    'success': True,
                    'action': 'moved_subcategory',
                    'product_id': product_id,
                    'old_category': current_category.get('category_name') if current_category else None,
                    'old_subcategory': current_subcategory,
                    'new_category': target_category.get('category_name'),
                    'new_subcategory': new_subcategory,
                    'message': f"Product moved to {target_category.get('category_name')} > {new_subcategory}"
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to add product to new subcategory'
                }
                
        except Exception as e:
            raise Exception(f"Error moving product to subcategory: {str(e)}")
    
    def _ensure_uncategorized_category_exists(self):
        """
        Ensure the 'Uncategorized' category exists, create if it doesn't
        """
        try:
            # Check if uncategorized category already exists
            uncategorized_category = self.category_collection.find_one({
                'category_name': self.UNCATEGORIZED_CATEGORY_NAME,
                'isDeleted': {'$ne': True}
            })
            
            if uncategorized_category:
                print(f"✅ Uncategorized category already exists: {uncategorized_category['_id']}")
                return self._convert_object_id(uncategorized_category)
            
            # Create the uncategorized category
            from ..models import Category
            
            uncategorized_data = {
                'category_name': self.UNCATEGORIZED_CATEGORY_NAME,
                'description': 'Auto-generated category for products without specific categorization',
                'status': 'active',
                'sub_categories': [
                    {
                        'name': self.UNCATEGORIZED_SUBCATEGORY_NAME,
                        'description': 'General uncategorized products',
                        'products': []
                    }
                ],
                'isDeleted': False,
                'is_system_category': True,
                'auto_created': True
            }
            
            category = Category(**uncategorized_data)
            result = self.category_collection.insert_one(category.to_dict())
            
            # Get the created category
            created_category = self.category_collection.find_one({'_id': result.inserted_id})
            
            print(f"✅ Created uncategorized category: {result.inserted_id}")
            
            return self._convert_object_id(created_category)
            
        except Exception as e:
            raise Exception(f"Error ensuring uncategorized category exists: {str(e)}")
    
    def validate_subcategory_update(self, product_id, new_subcategory, category_id):
        """Validate a subcategory update before performing it"""
        try:
            # Check if product exists
            product = self.product_collection.find_one({'_id': ObjectId(product_id)})
            if not product:
                return {
                    'is_valid': False,
                    'error': f'Product with ID {product_id} not found'
                }
            
            # Check if category exists
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            
            category = self.category_collection.find_one({
                '_id': category_id,
                'isDeleted': {'$ne': True}
            })
            
            if not category:
                return {
                    'is_valid': False,
                    'error': 'Category not found or is deleted'
                }
            
            # If new_subcategory is None/empty, it's valid (means move to uncategorized)
            if not new_subcategory or new_subcategory.strip() == '' or new_subcategory.lower() == 'none':
                return {
                    'is_valid': True,
                    'action': 'move_to_uncategorized',
                    'warning': f'Product will be moved to Uncategorized category'
                }
            
            # Check if new subcategory exists in target category
            subcategory_exists = any(
                sub['name'] == new_subcategory 
                for sub in category.get('sub_categories', [])
            )
            
            if not subcategory_exists:
                return {
                    'is_valid': False,
                    'error': f'Subcategory "{new_subcategory}" does not exist in category {category.get("category_name")}'
                }
            
            return {
                'is_valid': True,
                'action': 'move_to_subcategory',
                'target_category': category.get('category_name'),
                'target_subcategory': new_subcategory
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'error': f'Validation error: {str(e)}'
            }
    
    def _convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    def move_product_to_uncategorized_category(self, product_id, current_category_id=None):
        """
        Dedicated method to move a product to Uncategorized category
        """
        try:
            print(f"🔄 Moving product {product_id} to Uncategorized category")
            
            # Use the existing update method but force uncategorized
            result = self.update_product_subcategory(
                product_id=product_id,
                new_subcategory=None,  # null/empty triggers uncategorized move
                category_id=self.UNCATEGORIZED_CATEGORY_ID or '686a4de143821e2b21f725c6'
            )
            
            return {
                'success': True,
                'action': 'moved_to_uncategorized',
                'product_id': product_id,
                'previous_category_id': current_category_id,
                'new_category_id': self.UNCATEGORIZED_CATEGORY_ID,
                'message': 'Product moved to Uncategorized category successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'product_id': product_id
            }

    def bulk_move_products_to_uncategorized(self, product_ids, current_category_id=None):
        """
        Move multiple products to Uncategorized category
        """
        try:
            print(f"🔄 Bulk moving {len(product_ids)} products to Uncategorized")
            
            results = []
            successful = 0
            failed = 0
            
            for product_id in product_ids:
                try:
                    result = self.move_product_to_uncategorized_category(
                        product_id=product_id,
                        current_category_id=current_category_id
                    )
                    
                    if result.get('success'):
                        successful += 1
                    else:
                        failed += 1
                        
                    results.append(result)
                    
                except Exception as e:
                    failed += 1
                    results.append({
                        'success': False,
                        'error': str(e),
                        'product_id': product_id
                    })
            
            return {
                'success': successful > 0,
                'message': f'Bulk move completed: {successful} successful, {failed} failed',
                'successful': successful,
                'failed': failed,
                'results': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Bulk move to uncategorized failed'
            }
    