from bson import ObjectId
from datetime import datetime
from ..database import db_manager
from ..models import Category
import logging
from .audit_service import AuditLogService
from notifications.services import notification_service

logger = logging.getLogger(__name__)

class CategoryService:
    def __init__(self):
        """Initialize CategoryService with audit logging and indexes"""
        self.db = db_manager.get_database()
        self.collection = self.db.category
        self.audit_service = AuditLogService()
        self._ensure_indexes()

    # ================================================================
    # UTILITY METHODS
    # ================================================================
    
    def _ensure_indexes(self):
        """Add essential database indexes for performance"""
        try:
            indexes = [
                [("category_name", 1), ("isDeleted", 1)],
                [("status", 1), ("isDeleted", 1)],
                [("sub_categories.products", 1)]
            ]
            
            for index_fields in indexes:
                self.collection.create_index(index_fields, background=True)
                
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Could not create indexes: {e}")

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

    def _validate_category_data(self, category_data):
        """Validate category data before processing"""
        if not category_data:
            raise ValueError("Category data is required")
        
        category_name = category_data.get("category_name", "").strip()
        if not category_name:
            raise ValueError("Category name is required")
        
        # Check for duplicates
        existing = self.collection.find_one({
            'category_name': category_name,
            'isDeleted': {'$ne': True}
        })

        if existing:
            raise ValueError(f"Category '{category_name}' already exists")
        
        # Validate status if provided
        status = category_data.get("status", "active")
        if status not in ['active', 'inactive']:
            raise ValueError("Status must be 'active' or 'inactive'")
        
        return category_name

    def _prepare_subcategories(self, existing_sub_categories):
        """Prepare subcategories with auto-generated 'None' if needed"""
        subcategories_list = existing_sub_categories or []
        
        # Check if "None" subcategory already exists
        none_exists = any(
            sub.get('name', '').lower() == 'none' 
            for sub in subcategories_list
        )
        
        if not none_exists:
            default_none = {
                "name": "None",
                "description": "Products in this category without specific subcategorization",
                "products": [],
                "is_default": True,
                "created_automatically": True,
                "created_at": datetime.utcnow()
            }
            subcategories_list.insert(0, default_none)
            logger.debug("Auto-added 'None' subcategory")
        
        return subcategories_list

    # ================================================================
    # NOTIFICATION METHODS
    # ================================================================
    
    def _send_category_notification(self, action_type, category_data, category_id=None, old_category_data=None):
        """Send notification for category-related actions"""
        try:
            category_name = category_data.get('category_name', 'Unknown Category')
            
            # Notification configurations
            configs = {
                'created': {
                    'title': "New Category Created",
                    'message': f"A new category '{category_name}' has been added to the system",
                    'priority': "high"
                },
                'updated': {
                    'title': "Category Updated", 
                    'message': f"Category '{category_name}' has been updated",
                    'priority': "medium"
                },
                'soft_deleted': {
                    'title': "Category Deleted",
                    'message': f"Category '{category_name}' has been deleted",
                    'priority': "medium"
                },
                'hard_deleted': {
                    'title': "Category Permanently Deleted",
                    'message': f"Category '{category_name}' has been permanently deleted by admin",
                    'priority': "high"
                },
                'restored': {
                    'title': "Category Restored",
                    'message': f"Category '{category_name}' has been restored to the system",
                    'priority': "medium"
                }
            }

            if action_type not in configs:
                return
            config = configs[action_type]

            # Add change details for updates
            if action_type == 'updated' and old_category_data:
                changes = []
                for field in ['category_name', 'description', 'status']:
                    old_val = old_category_data.get(field)
                    new_val = category_data.get(field)
                    if old_val != new_val:
                        changes.append(f"{field}: '{old_val}' → '{new_val}'")
                
                if changes:
                    config['message'] += f" - Changes: {', '.join(changes)}"

            # Create metadata
            metadata = {
                "category_id": str(category_id or category_data.get('_id', '')),
                "category_name": category_name,
                "description": category_data.get('description', ''),
                "status": category_data.get('status', 'active'),
                "action_type": f"category_{action_type}",
                "source": "category_management"
            }
            
            if action_type == 'updated' and 'changes' in locals():
                metadata["changes"] = changes

            # Send notification
            notification_service.create_notification(
                title=config['title'],
                message=config['message'],
                priority=config['priority'],
                notification_type="system",
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to create {action_type} notification for category: {e}")

    # ================================================================
    # CRUD OPERATIONS
    # ================================================================
    
    def create_category(self, category_data, current_user=None):
        """Create a new category with automatic 'None' subcategory"""
        try:
            # Validate input data
            category_name = self._validate_category_data(category_data)
            logger.info(f"Creating category: {category_name}")
            
            # Prepare subcategories
            existing_sub_categories = category_data.get("sub_categories", [])
            sub_categories = self._prepare_subcategories(existing_sub_categories)
            
            # Add timestamps and default values
            now = datetime.utcnow()
            category_kwargs = {
                'category_name': category_name,
                'description': category_data.get("description", ''),
                'status': category_data.get("status", 'active'),
                'sub_categories': sub_categories,
                'isDeleted': False,
                'date_created': now,
                'last_updated': now
            }
            
            # Add image fields if present
            image_fields = ['image_url', 'image_filename', 'image_size', 'image_type', 'image_uploaded_at']
            for field in image_fields:
                if field in category_data and category_data[field] is not None:
                    category_kwargs[field] = category_data[field]
            
            # Create and insert category
            category = Category(**category_kwargs)
            result = self.collection.insert_one(category.to_dict())
            
            # Get created category
            created_category = self.collection.find_one({'_id': result.inserted_id})
            created_category = self.convert_object_id(created_category)
            
            # Send notification
            self._send_category_notification('created', created_category)
            
            # Audit logging
            if current_user and self.audit_service:
                try:
                    audit_data = {**created_category, "category_id": created_category['_id']}
                    self.audit_service.log_category_create(current_user, audit_data)
                    logger.debug("Audit log created for category creation")
                except Exception as audit_error:
                    logger.error(f"Audit logging failed: {audit_error}")
            
            logger.info(f"Category '{category_name}' created successfully with {len(sub_categories)} subcategories")
            return created_category

        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
            raise Exception(f"Validation error: {str(ve)}")
        except Exception as e:
            logger.error(f"Error creating category: {e}", exc_info=True)
            raise Exception(f"Error creating category: {str(e)}")

    def get_all_categories(self, include_deleted=False, limit=None, skip=None):
        """Get all categories with optional pagination"""
        try:
            query = {}
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
            
            cursor = self.collection.find(query)
            
            # Add pagination if specified
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            
            categories = list(cursor)
            return [self.convert_object_id(category) for category in categories]
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            raise Exception(f"Error getting categories: {str(e)}")

    def get_category_by_id(self, category_id, include_deleted=False):
        """Get category by ID"""
        try:
            if not category_id or not ObjectId.is_valid(category_id):
                return None
            
            query = {'_id': ObjectId(category_id)}
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}

            category = self.collection.find_one(query)
            return self.convert_object_id(category) if category else None
        except Exception as e:
            logger.error(f"Error getting category by ID {category_id}: {e}")
            raise Exception(f"Error getting category: {str(e)}")

    def get_active_categories(self, include_deleted=False):
        """Get only active categories"""
        try:
            query = {'status': 'active'}
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
            
            categories = list(self.collection.find(query))
            return [self.convert_object_id(category) for category in categories]
        except Exception as e:
            logger.error(f"Error getting active categories: {e}")
            raise Exception(f"Error getting active categories: {str(e)}")

    def search_categories(self, search_term, include_deleted=False, limit=20):
        """Search categories by name or description"""
        try:
            if not search_term or not search_term.strip():
                return []
            
            search_term = search_term.strip()
            regex_pattern = {'$regex': search_term, '$options': 'i'}
            
            query = {
                '$or': [
                    {'category_name': regex_pattern},
                    {'description': regex_pattern}
                ]
            }
            
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
            
            categories = list(self.collection.find(query).limit(limit))
            return [self.convert_object_id(category) for category in categories]
        except Exception as e:
            logger.error(f"Error searching categories: {e}")
            raise Exception(f"Error searching categories: {str(e)}")

    def update_category(self, category_id, category_data, current_user=None):
        """Update category with audit logging"""
        try:
            logger.info(f"Updating category {category_id}")
            if current_user:
                logger.info(f"Updated by: {current_user['username']}")
            
            if not category_id or not ObjectId.is_valid(category_id):
                return None
            
            # Get current category data for audit and notification comparison
            old_category = self.collection.find_one({
                '_id': ObjectId(category_id),
                'isDeleted': {'$ne': True}
            })
            
            if not old_category:
                return None
            
            old_category = self.convert_object_id(old_category)
            
            # Prepare update data
            update_data = category_data.copy()
            update_data['last_updated'] = datetime.utcnow()
            
            # Validate category name if being updated
            if 'category_name' in update_data:
                new_name = update_data['category_name'].strip()
                if new_name != old_category.get('category_name'):
                    existing = self.collection.find_one({
                        'category_name': new_name,
                        'isDeleted': {'$ne': True},
                        '_id': {'$ne': ObjectId(category_id)}
                    })
                    if existing:
                        raise ValueError(f"Category name '{new_name}' already exists")

            result = self.collection.update_one(
                {
                    '_id': ObjectId(category_id),
                    'isDeleted': {'$ne': True}
                },
                {'$set': update_data}
            )
            
            if result.modified_count == 0:
                return None

            updated_category = self.collection.find_one({'_id': ObjectId(category_id)})
            updated_category = self.convert_object_id(updated_category)
            
            # Send notification
            self._send_category_notification('updated', updated_category, category_id, old_category)
            
            # Audit logging
            if current_user and self.audit_service:
                try:
                    self.audit_service.log_category_update(
                        current_user, 
                        category_id, 
                        old_values=old_category, 
                        new_values=update_data
                    )
                    logger.debug("Audit log created for category update")
                except Exception as audit_error:
                    logger.error(f"Audit logging failed: {audit_error}")
            
            logger.info(f"Category updated successfully")
            return updated_category

        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
            raise Exception(f"Validation error: {str(ve)}")
        except Exception as e:
            logger.error(f"Error updating category: {e}", exc_info=True)
            raise Exception(f"Error updating category: {str(e)}")

    def soft_delete_category(self, category_id, current_user=None, deletion_context=None):
        """Soft delete category with audit logging"""
        try:
            logger.info(f"Soft deleting category {category_id}")
            if current_user:
                logger.info(f"Deleted by: {current_user['username']}")
            
            if not category_id or not ObjectId.is_valid(category_id):
                return False
            
            object_id = ObjectId(category_id)
            
            # Get category data before deletion (only active categories)
            category_to_delete = self.collection.find_one({
                '_id': object_id,
                'isDeleted': {'$ne': True}
            })
            
            if not category_to_delete:
                return False
            
            now = datetime.utcnow()
            
            # Soft delete data
            update_data = {
                'isDeleted': True,
                'deleted_at': now,
                'deletedBy': current_user.get('username') if current_user else 'system',
                'last_updated': now,
                'deletionContext': deletion_context or "category_deletion"
            }
            
            # Update category
            result = self.collection.update_one(
                {'_id': object_id},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                category_to_delete = self.convert_object_id(category_to_delete)
                
                # Send notification
                self._send_category_notification('soft_deleted', category_to_delete, category_id)
                
                # Audit logging
                if current_user and self.audit_service:
                    try:
                        category_for_audit = category_to_delete.copy()
                        category_for_audit['deletion_type'] = 'soft_delete'
                        
                        self.audit_service.log_category_delete(current_user, category_for_audit)
                        logger.info("Audit log created for category soft deletion")
                    except Exception as audit_error:
                        logger.error(f"Audit logging failed: {audit_error}")
                
                logger.info("Category soft deleted successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error soft deleting category {category_id}: {str(e)}")
            raise Exception(f"Error soft deleting category: {str(e)}")

    def restore_category(self, category_id, current_user=None):
        """Restore a soft-deleted category"""
        try:
            logger.info(f"Restoring category {category_id}")
            if current_user:
                logger.info(f"Restored by: {current_user['username']}")
            
            if not category_id or not ObjectId.is_valid(category_id):
                return False
            
            object_id = ObjectId(category_id)
            
            # Find deleted category
            deleted_category = self.collection.find_one({
                '_id': object_id,
                'isDeleted': True
            })
            
            if not deleted_category:
                return False
            
            now = datetime.utcnow()
            
            # Restore data
            restore_data = {
                'isDeleted': False,
                'restoredAt': now,
                'restoredBy': current_user.get('username') if current_user else 'system',
                'last_updated': now,
                'status': 'active'  # Reactivate
            }
            
            # Remove deletion metadata
            unset_data = {
                'deleted_at': "",
                'deletedBy': "",
                'deletionContext': ""
            }
            
            # Restore category
            result = self.collection.update_one(
                {'_id': object_id},
                {'$set': restore_data, '$unset': unset_data}
            )
            
            if result.modified_count > 0:
                restored_category = self.collection.find_one({'_id': object_id})
                restored_category = self.convert_object_id(restored_category)
                
                # Send notification
                self._send_category_notification('restored', restored_category, category_id)
                
                # Audit logging
                if current_user and self.audit_service:
                    try:
                        self.audit_service.log_category_restore(current_user, restored_category)
                        logger.info("Audit log created for category restoration")
                    except Exception as audit_error:
                        logger.error(f"Audit logging failed: {audit_error}")
                
                logger.info("Category restored successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error restoring category {category_id}: {str(e)}")
            raise Exception(f"Error restoring category: {str(e)}")

    def hard_delete_category(self, category_id, current_user=None):
        """Permanently delete category (use with extreme caution)"""
        try:
            logger.warning(f"HARD DELETING category {category_id} - THIS IS PERMANENT!")
            if current_user:
                logger.info(f"Deleted by: {current_user['username']}")
            
            if not category_id or not ObjectId.is_valid(category_id):
                return False
            
            object_id = ObjectId(category_id)
            
            # Get category data before permanent deletion
            category_to_delete = self.collection.find_one({'_id': object_id})
            if not category_to_delete:
                return False
            
            category_name = category_to_delete.get('category_name', 'Unknown Category')
            
            # Permanently delete from collection
            result = self.collection.delete_one({'_id': object_id})
            
            if result.deleted_count > 0:
                # Send critical notification for permanent deletion
                try:
                    notification_service.create_notification(
                        title="⚠️ CATEGORY PERMANENTLY DELETED",
                        message=f"Category '{category_name}' has been PERMANENTLY deleted from the system",
                        priority="urgent",
                        notification_type="system",
                        metadata={
                            "category_id": str(category_id),
                            "category_name": category_name,
                            "action_type": "category_hard_deleted",
                            "warning": "PERMANENT_DELETION"
                        }
                    )
                except Exception as e:
                    logger.error(f"Failed to send hard deletion notification: {e}")
                
                # Audit logging
                if current_user and self.audit_service:
                    try:
                        category_for_audit = self.convert_object_id(category_to_delete)
                        category_for_audit['deletion_type'] = 'hard_delete'
                        
                        self.audit_service.log_category_delete(current_user, category_for_audit)
                        logger.info("Audit log created for PERMANENT category deletion")
                    except Exception as audit_error:
                        logger.error(f"Audit logging failed: {audit_error}")
                
                logger.warning("Category PERMANENTLY deleted")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error permanently deleting category {category_id}: {str(e)}")
            raise Exception(f"Error permanently deleting category: {str(e)}")

    def get_deleted_categories(self):
        """Get all soft-deleted categories"""
        try:
            categories = list(self.collection.find({'isDeleted': True}))
            return [self.convert_object_id(category) for category in categories]
        except Exception as e:
            logger.error(f"Error getting deleted categories: {e}")
            raise Exception(f"Error getting deleted categories: {str(e)}")

    # ================================================================
    # SUBCATEGORY OPERATIONS
    # ================================================================
    
    def add_subcategory(self, category_id, subcategory_data, current_user=None):
        """Add a subcategory to a category"""
        try:
            logger.info(f"Adding subcategory to category {category_id}")
            if current_user:
                logger.info(f"Added by: {current_user['username']}")
            
            if not category_id or not ObjectId.is_valid(category_id):
                return False
            
            # Validate subcategory data
            if not subcategory_data or not subcategory_data.get('name', '').strip():
                raise ValueError("Subcategory name is required")
            
            object_id = ObjectId(category_id)
            
            # Check if category exists and is not deleted
            category = self.collection.find_one({
                '_id': object_id,
                'isDeleted': {'$ne': True}
            })
            
            if not category:
                raise ValueError("Category not found or is deleted")
            
            # Check for duplicate subcategory name
            existing_names = [sub.get('name', '').lower() for sub in category.get('sub_categories', [])]
            new_name = subcategory_data.get('name', '').strip().lower()
            
            if new_name in existing_names:
                raise ValueError(f"Subcategory '{subcategory_data.get('name')}' already exists")
            
            # Ensure required fields
            if 'products' not in subcategory_data:
                subcategory_data['products'] = []
            if 'created_at' not in subcategory_data:
                subcategory_data['created_at'] = datetime.utcnow()
            
            # Add subcategory
            result = self.collection.update_one(
                {'_id': object_id},
                {
                    '$addToSet': {'sub_categories': subcategory_data},
                    '$set': {'last_updated': datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                # Send notification
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
                    logger.error(f"Failed to send subcategory notification: {notification_error}")
                
                # Audit logging
                if current_user and self.audit_service:
                    try:
                        self.audit_service.log_category_update(
                            current_user, 
                            category_id, 
                            old_values={}, 
                            new_values={"subcategory_added": subcategory_data}
                        )
                        logger.debug("Audit log created for subcategory addition")
                    except Exception as audit_error:
                        logger.error(f"Audit logging failed: {audit_error}")
                
                logger.info(f"Subcategory '{subcategory_data.get('name')}' added successfully")
                return True
            
            return False
            
        except ValueError as ve:
            logger.error(f"Validation error adding subcategory: {ve}")
            raise Exception(f"Validation error: {str(ve)}")
        except Exception as e:
            logger.error(f"Error adding subcategory: {e}", exc_info=True)
            raise Exception(f"Error adding subcategory: {str(e)}")

    def remove_subcategory(self, category_id, subcategory_name, current_user=None):
        """Remove a subcategory from a category"""
        try:
            logger.info(f"Removing subcategory '{subcategory_name}' from category {category_id}")
            if current_user:
                logger.info(f"Removed by: {current_user['username']}")
            
            if not category_id or not ObjectId.is_valid(category_id):
                return False
            
            object_id = ObjectId(category_id)
            
            # Check if category exists and is not deleted
            category = self.collection.find_one({
                '_id': object_id,
                'isDeleted': {'$ne': True}
            })
            
            if not category:
                raise ValueError("Category not found or is deleted")
            
            # Find subcategory and check if it has products
            subcategory_to_remove = None
            for sub in category.get('sub_categories', []):
                if sub.get('name') == subcategory_name:
                    subcategory_to_remove = sub
                    break
            
            if not subcategory_to_remove:
                raise ValueError(f"Subcategory '{subcategory_name}' not found")
            
            # Check if subcategory has products
            if subcategory_to_remove.get('products', []):
                raise ValueError(f"Cannot remove subcategory '{subcategory_name}' - it contains products")
            
            # Remove subcategory
            result = self.collection.update_one(
                {'_id': object_id},
                {
                    '$pull': {'sub_categories': {'name': subcategory_name}},
                    '$set': {'last_updated': datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                # Send notification
                try:
                    notification_service.create_notification(
                        title="Subcategory Removed",
                        message=f"Subcategory '{subcategory_name}' removed from category '{category.get('category_name', 'Unknown')}'",
                        priority="low",
                        notification_type="system",
                        metadata={
                            "category_id": str(category_id),
                            "category_name": category.get('category_name', 'Unknown'),
                            "subcategory_name": subcategory_name,
                            "action_type": "subcategory_removed"
                        }
                    )
                except Exception as notification_error:
                    logger.error(f"Failed to send subcategory notification: {notification_error}")
                
                # Audit logging
                if current_user and self.audit_service:
                    try:
                        self.audit_service.log_category_update(
                            current_user, 
                            category_id, 
                            old_values={"subcategory_removed": subcategory_to_remove}, 
                            new_values={}
                        )
                        logger.debug("Audit log created for subcategory removal")
                    except Exception as audit_error:
                        logger.error(f"Audit logging failed: {audit_error}")
                
                logger.info(f"Subcategory '{subcategory_name}' removed successfully")
                return True
            
            return False
            
        except ValueError as ve:
            logger.error(f"Validation error removing subcategory: {ve}")
            raise Exception(f"Validation error: {str(ve)}")
        except Exception as e:
            logger.error(f"Error removing subcategory: {e}", exc_info=True)
            raise Exception(f"Error removing subcategory: {str(e)}")

    def get_subcategories(self, category_id):
        """Get all subcategories for a specific category"""
        try:
            if not category_id or not ObjectId.is_valid(category_id):
                return []
            
            category = self.collection.find_one(
                {
                    '_id': ObjectId(category_id),
                    'isDeleted': {'$ne': True}
                },
                {'sub_categories': 1}
            )
            
            return category.get('sub_categories', []) if category else []
            
        except Exception as e:
            logger.error(f"Error getting subcategories: {e}")
            raise Exception(f"Error getting subcategories: {str(e)}")

    # ================================================================
    # UTILITY METHODS
    # ================================================================
    
    def get_category_stats(self):
        """Get comprehensive category statistics"""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': None,
                        'total_categories': {'$sum': 1},
                        'active_categories': {
                            '$sum': {
                                '$cond': [
                                    {'$and': [
                                        {'$eq': ['$status', 'active']},
                                        {'$ne': ['$isDeleted', True]}
                                    ]},
                                    1, 0
                                ]
                            }
                        },
                        'deleted_categories': {
                            '$sum': {'$cond': [{'$eq': ['$isDeleted', True]}, 1, 0]}
                        },
                        'total_subcategories': {
                            '$sum': {'$size': {'$ifNull': ['$sub_categories', []]}}
                        },
                        'total_products': {
                            '$sum': {
                                '$sum': {
                                    '$map': {
                                        'input': {'$ifNull': ['$sub_categories', []]},
                                        'as': 'sub',
                                        'in': {'$size': {'$ifNull': ['$sub.products', []]}}
                                    }
                                }
                            }
                        }
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            return result[0] if result else {
                'total_categories': 0,
                'active_categories': 0,
                'deleted_categories': 0,
                'total_subcategories': 0,
                'total_products': 0
            }
            
        except Exception as e:
            logger.error(f"Error getting category stats: {e}")
            return {
                'total_categories': 0,
                'active_categories': 0,
                'deleted_categories': 0,
                'total_subcategories': 0,
                'total_products': 0
            }

    def get_category_delete_info(self, category_id):
        """Get information about a category before deletion (for confirmation dialogs)"""
        try:
            if not category_id or not ObjectId.is_valid(category_id):
                return None
            
            category = self.collection.find_one({'_id': ObjectId(category_id)})
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
            logger.error(f"Error getting category delete info: {e}")
            raise Exception(f"Error getting category delete info: {str(e)}")

    def bulk_soft_delete_categories(self, category_ids, current_user=None):
        """Soft delete multiple categories at once"""
        try:
            if not category_ids:
                return {'success': 0, 'failed': 0, 'errors': []}
            
            logger.info(f"Bulk soft deleting {len(category_ids)} categories")
            if current_user:
                logger.info(f"Initiated by: {current_user['username']}")
            
            # Convert string IDs to ObjectId
            object_ids = []
            for cat_id in category_ids:
                if ObjectId.is_valid(cat_id):
                    object_ids.append(ObjectId(cat_id))
            
            # Get categories that can be soft deleted
            categories_to_delete = list(self.collection.find({
                '_id': {'$in': object_ids},
                'isDeleted': {'$ne': True}
            }))
            
            success_count = 0
            failed_count = 0
            errors = []
            
            for category in categories_to_delete:
                try:
                    result = self.soft_delete_category(str(category['_id']), current_user)
                    if result:
                        success_count += 1
                    else:
                        failed_count += 1
                        errors.append(f"Failed to soft delete {category.get('category_name', 'Unknown')}")
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Error deleting {category.get('category_name', 'Unknown')}: {str(e)}")
            
            logger.info(f"Bulk delete completed: {success_count} successful, {failed_count} failed")
            
            return {
                'success': success_count,
                'failed': failed_count,
                'errors': errors,
                'total_requested': len(category_ids)
            }
            
        except Exception as e:
            logger.error(f"Error in bulk soft delete: {e}")
            raise Exception(f"Error in bulk soft delete: {str(e)}")

    def bulk_update_categories_status(self, category_ids, new_status, current_user=None):
        """Efficiently update multiple categories status"""
        try:
            if new_status not in ['active', 'inactive']:
                raise ValueError("Status must be 'active' or 'inactive'")
            
            logger.info(f"Bulk updating {len(category_ids)} categories to status: {new_status}")
            if current_user:
                logger.info(f"Updated by: {current_user['username']}")
            
            object_ids = [ObjectId(cat_id) for cat_id in category_ids if ObjectId.is_valid(cat_id)]
            
            result = self.collection.update_many(
                {
                    '_id': {'$in': object_ids},
                    'isDeleted': {'$ne': True}
                },
                {
                    '$set': {
                        'status': new_status,
                        'last_updated': datetime.utcnow()
                    }
                }
            )
            
            # Send bulk notification
            if result.modified_count > 0:
                try:
                    notification_service.create_notification(
                        title="Categories Status Updated",
                        message=f"{result.modified_count} categories updated to {new_status} status",
                        priority="low",
                        notification_type="system",
                        metadata={
                            "updated_count": result.modified_count,
                            "new_status": new_status,
                            "action_type": "categories_bulk_status_update",
                            "updated_by": current_user.get('username') if current_user else 'system'
                        }
                    )
                except Exception as notification_error:
                    logger.error(f"Failed to send bulk update notification: {notification_error}")
            
            logger.info(f"Updated {result.modified_count} categories to {new_status}")
            return {
                'success': result.modified_count,
                'total_requested': len(category_ids)
            }
            
        except ValueError as ve:
            logger.error(f"Validation error in bulk update: {ve}")
            raise Exception(f"Validation error: {str(ve)}")
        except Exception as e:
            logger.error(f"Bulk update failed: {e}")
            raise Exception(f"Bulk update failed: {str(e)}")


# ================================================================
# CATEGORY DISPLAY SERVICE - Optimized for Performance
# ================================================================

class CategoryDisplayService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.category_collection = self.db.category
        self.sales_collection = self.db.sales_log
        self._ensure_sales_indexes()

    def _ensure_sales_indexes(self):
        """Add indexes for sales collection performance"""
        try:
            # Critical for sales performance
            self.sales_collection.create_index([
                ("item_list.item_name", 1),
                ("transaction_date", 1)
            ], background=True)
            
            logger.info("Sales indexes created")
        except Exception as e:
            logger.warning(f"Could not create sales indexes: {e}")

    def get_categories_display_optimized(self, include_deleted=False, limit=50):
        """OPTIMIZED: Use aggregation pipeline for better performance"""
        try:
            # Build category filter
            category_match = {}
            if not include_deleted:
                category_match['isDeleted'] = {'$ne': True}
            
            # Use aggregation pipeline for efficient data retrieval
            pipeline = [
                {"$match": category_match},
                {"$limit": limit},
                
                # Lookup sales data efficiently
                {"$lookup": {
                    "from": "sales_log",
                    "let": {"category_products": "$sub_categories.products"},
                    "pipeline": [
                        {"$unwind": "$item_list"},
                        {"$match": {
                            "$expr": {
                                "$in": ["$item_list.item_name", {"$reduce": {
                                    "input": "$category_products", 
                                    "initialValue": [], 
                                    "in": {"$concatArrays": ["$value", "$this"]}
                                }}]
                            }
                        }},
                        {"$group": {
                            "_id": "$item_list.item_name",
                            "total_quantity": {"$sum": "$item_list.quantity"},
                            "total_sales": {"$sum": {"$multiply": ["$item_list.quantity", "$item_list.unit_price"]}}
                        }}
                    ],
                    "as": "sales_data"
                }},
                
                # Calculate totals and convert ObjectId
                {"$addFields": {
                    "total_sales": {"$sum": "$sales_data.total_sales"},
                    "total_quantity": {"$sum": "$sales_data.total_quantity"},
                    "_id": {"$toString": "$_id"}
                }}
            ]
            
            results = list(self.category_collection.aggregate(pipeline))
            
            # Process subcategories with sales data
            for category in results:
                subcategories_data = []
                sales_lookup = {item["_id"]: item for item in category.get("sales_data", [])}
                
                for subcategory in category.get('sub_categories', []):
                    subcategory_sales = 0
                    subcategory_quantity = 0
                    
                    for product_name in subcategory.get('products', []):
                        if product_name in sales_lookup:
                            product_data = sales_lookup[product_name]
                            subcategory_quantity += product_data['total_quantity']
                            subcategory_sales += product_data['total_sales']
                    
                    subcategories_data.append({
                        'name': subcategory['name'],
                        'quantity_sold': subcategory_quantity,
                        'total_sales': round(subcategory_sales, 2),
                        'product_count': len(subcategory.get('products', []))
                    })
                
                category['subcategories'] = subcategories_data
                category['subcategory_count'] = len(subcategories_data)
                
                # Clean up raw sales_data
                if 'sales_data' in category:
                    del category['sales_data']
            
            logger.info(f"Processed {len(results)} categories with optimized pipeline")
            return results
            
        except Exception as e:
            logger.error(f"Error in optimized categories display: {e}", exc_info=True)
            raise Exception(f"Error getting categories: {str(e)}")

    def get_categories_display(self, include_deleted=False):
        """Main display method with fallback to original implementation"""
        try:
            # Try optimized version first
            return self.get_categories_display_optimized(include_deleted, limit=100)
        except Exception as e:
            logger.warning(f"Optimized method failed, using fallback: {e}")
            return self._get_categories_display_fallback(include_deleted)

    def _get_categories_display_fallback(self, include_deleted=False):
        """Fallback method with performance limits"""
        try:
            # Fallback with reasonable limits to prevent memory issues
            projection = {
                "_id": 1, "item_list.item_name": 1, "item_list.quantity": 1,
                "item_list.unit_price": 1, "transaction_date": 1
            }
            
            # CRITICAL: Add limit to prevent memory issues
            invoices = list(self.sales_collection.find({}, projection).limit(10000))
            logger.info(f"Processing {len(invoices)} invoices (limited for performance)")
            
            # Build sales lookup
            item_sales_lookup = {}
            for invoice in invoices:
                for item in invoice.get('item_list', []):
                    item_name = item['item_name']
                    if item_name not in item_sales_lookup:
                        item_sales_lookup[item_name] = {'quantity': 0, 'total_sales': 0}
                    
                    item_total = round(item['quantity'] * item['unit_price'], 2)
                    item_sales_lookup[item_name]['quantity'] += item['quantity']
                    item_sales_lookup[item_name]['total_sales'] += item_total

            # Process categories
            category_filter = {}
            if not include_deleted:
                category_filter['isDeleted'] = {'$ne': True}
                
            categories = list(self.category_collection.find(category_filter).limit(100))
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
                    'isDeleted': category.get('isDeleted', False),
                    'deleted_at': category.get('deleted_at'),
                    'date_created': category.get('date_created'),
                    'last_updated': category.get('last_updated'),
                    'total_quantity_sold': category_total_quantity,
                    'total_sales': category_total_sales,
                    'subcategories': subcategories_data,
                    'subcategory_count': len(subcategories_data)
                })

            logger.info(f"Returning {len(categories_with_sales)} categories with sales data (fallback)")
            return categories_with_sales
            
        except Exception as e:
            logger.error(f"ERROR in fallback categories display: {e}", exc_info=True)
            raise Exception(f"Error getting categories: {str(e)}")


# ================================================================
# PRODUCT SUBCATEGORY SERVICE - Simplified and Aligned
# ================================================================

class ProductSubcategoryService:
    UNCATEGORIZED_CATEGORY_NAME = "Uncategorized"
    UNCATEGORIZED_SUBCATEGORY_NAME = "General"
    
    def __init__(self):
        self.db = db_manager.get_database()
        self.category_collection = self.db.category
        self.product_collection = self.db.products
        
        try:
            self.audit_service = AuditLogService()
            logger.info("Audit service initialized for ProductSubcategoryService")
        except Exception as e:
            logger.warning(f"Could not initialize audit service: {e}")
            self.audit_service = None

    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document

    def update_product_subcategory(self, product_id, new_subcategory, category_id, current_user=None):
        """Update product subcategory with validation and audit logging"""
        try:
            logger.info(f"Updating product {product_id} subcategory to '{new_subcategory}' in category {category_id}")
            if current_user:
                logger.info(f"Updated by: {current_user['username']}")
            
            # Validate inputs
            if not product_id or not ObjectId.is_valid(product_id):
                raise ValueError("Invalid product ID")
            
            if not category_id or not ObjectId.is_valid(category_id):
                raise ValueError("Invalid category ID")
            
            # Convert to ObjectIds
            product_obj_id = ObjectId(product_id)
            category_obj_id = ObjectId(category_id)
            
            # Get product
            product = self.product_collection.find_one({'_id': product_obj_id})
            if not product:
                raise ValueError(f"Product with ID {product_id} not found")
            
            product_name = product.get('product_name')
            if not product_name:
                raise ValueError(f"Product {product_id} has no product_name")
            
            # Get target category
            target_category = self.category_collection.find_one({
                '_id': category_obj_id,
                'isDeleted': {'$ne': True}
            })
            
            if not target_category:
                raise ValueError("Target category not found or is deleted")
            
            # Find current category
            current_category = self.category_collection.find_one({
                'sub_categories.products': product_name,
                'isDeleted': {'$ne': True}
            })
            
            current_subcategory = None
            if current_category:
                for subcategory in current_category.get('sub_categories', []):
                    if product_name in subcategory.get('products', []):
                        current_subcategory = subcategory['name']
                        break
            
            # Handle empty/null subcategory (move to uncategorized)
            if not new_subcategory or new_subcategory.strip() == '':
                return self._move_to_uncategorized_category(
                    product_id, product_name, current_category, current_subcategory
                )
            
            # Move to specified subcategory
            return self._move_product_to_subcategory(
                product_id, product_name, target_category, new_subcategory,
                current_category, current_subcategory, current_user
            )
                
        except ValueError as ve:
            logger.error(f"Validation error updating product subcategory: {ve}")
            raise Exception(f"Validation error: {str(ve)}")
        except Exception as e:
            logger.error(f"Error updating product subcategory: {e}", exc_info=True)
            raise Exception(f"Error updating product subcategory: {str(e)}")

    def _move_product_to_subcategory(self, product_id, product_name, target_category, new_subcategory, current_category, current_subcategory, current_user=None):
        """Move product to a specific subcategory with validation"""
        try:
            # Check if target subcategory exists
            target_subcategory_exists = any(
                sub['name'] == new_subcategory 
                for sub in target_category.get('sub_categories', [])
            )
            
            if not target_subcategory_exists:
                raise ValueError(f"Subcategory '{new_subcategory}' does not exist in category '{target_category.get('category_name')}'")
            
            # Check if already in the right place
            if (current_category and 
                str(current_category['_id']) == str(target_category['_id']) and 
                current_subcategory == new_subcategory):
                return {
                    'success': True,
                    'action': 'no_change',
                    'message': f"Product is already in {target_category.get('category_name')} > {new_subcategory}"
                }
            
            # Remove from current location
            if current_category and current_subcategory:
                self.category_collection.update_one(
                    {'_id': current_category['_id']},
                    {'$pull': {'sub_categories.$[elem].products': product_name}},
                    array_filters=[{'elem.name': current_subcategory}]
                )
            
            # Add to new location
            result = self.category_collection.update_one(
                {'_id': target_category['_id']},
                {
                    '$addToSet': {'sub_categories.$[elem].products': product_name},
                    '$set': {'last_updated': datetime.utcnow()}
                },
                array_filters=[{'elem.name': new_subcategory}]
            )
            
            if result.modified_count > 0:
                # Update product document
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
                
                logger.info(f"Moved product to {target_category.get('category_name')} > {new_subcategory}")
                
                return {
                    'success': True,
                    'action': 'moved_subcategory',
                    'old_category': current_category.get('category_name') if current_category else None,
                    'old_subcategory': current_subcategory,
                    'new_category': target_category.get('category_name'),
                    'new_subcategory': new_subcategory,
                    'message': f"Product moved to {target_category.get('category_name')} > {new_subcategory}"
                }
            
            return {'success': False, 'message': 'Failed to add product to new subcategory'}
                
        except Exception as e:
            raise Exception(f"Error moving product to subcategory: {str(e)}")

    def _move_to_uncategorized_category(self, product_id, product_name, current_category=None, current_subcategory=None):
        """Move product to uncategorized category"""
        try:
            logger.info(f"Moving {product_name} to Uncategorized category")
            
            # Ensure uncategorized category exists
            uncategorized_category = self._ensure_uncategorized_category_exists()
            
            # Remove from current category
            if current_category and current_subcategory:
                self.category_collection.update_one(
                    {'_id': current_category['_id']},
                    {'$pull': {'sub_categories.$[elem].products': product_name}},
                    array_filters=[{'elem.name': current_subcategory}]
                )
            
            # Add to uncategorized
            result = self.category_collection.update_one(
                {'_id': ObjectId(uncategorized_category['_id'])},
                {
                    '$addToSet': {'sub_categories.$[elem].products': product_name},
                    '$set': {'last_updated': datetime.utcnow()}
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
                
                return {
                    'success': True,
                    'action': 'moved_to_uncategorized',
                    'message': f"Product moved to {self.UNCATEGORIZED_CATEGORY_NAME} category"
                }
            
            return {'success': False, 'message': 'Failed to move product to uncategorized category'}
                
        except Exception as e:
            raise Exception(f"Error moving to uncategorized category: {str(e)}")

    def _ensure_uncategorized_category_exists(self):
        """Ensure uncategorized category exists"""
        try:
            # Check if exists
            uncategorized_category = self.category_collection.find_one({
                'category_name': self.UNCATEGORIZED_CATEGORY_NAME,
                'isDeleted': {'$ne': True}
            })
            
            if uncategorized_category:
                return self.convert_object_id(uncategorized_category)
            
            # Create if doesn't exist
            from ..models import Category
            
            uncategorized_data = {
                'category_name': self.UNCATEGORIZED_CATEGORY_NAME,
                'description': 'Auto-generated category for products without specific categorization',
                'status': 'active',
                'sub_categories': [{
                    'name': self.UNCATEGORIZED_SUBCATEGORY_NAME,
                    'description': 'General uncategorized products',
                    'products': []
                }],
                'isDeleted': False,
                'is_system_category': True,
                'auto_created': True,
                'date_created': datetime.utcnow(),
                'last_updated': datetime.utcnow()
            }
            
            category = Category(**uncategorized_data)
            result = self.category_collection.insert_one(category.to_dict())
            
            created_category = self.category_collection.find_one({'_id': result.inserted_id})
            logger.info(f"Created uncategorized category: {result.inserted_id}")
            
            return self.convert_object_id(created_category)
            
        except Exception as e:
            raise Exception(f"Error ensuring uncategorized category exists: {str(e)}")

    def validate_subcategory_update(self, product_id, new_subcategory, category_id):
        """Validate subcategory update before performing it"""
        try:
            # Check product exists
            if not ObjectId.is_valid(product_id):
                return {'is_valid': False, 'error': 'Invalid product ID'}
            
            product = self.product_collection.find_one({'_id': ObjectId(product_id)})
            if not product:
                return {'is_valid': False, 'error': f'Product with ID {product_id} not found'}
            
            # Check category exists
            if not ObjectId.is_valid(category_id):
                return {'is_valid': False, 'error': 'Invalid category ID'}
            
            category = self.category_collection.find_one({
                '_id': ObjectId(category_id),
                'isDeleted': {'$ne': True}
            })
            
            if not category:
                return {'is_valid': False, 'error': 'Category not found or is deleted'}
            
            # If empty subcategory, valid (move to uncategorized)
            if not new_subcategory or new_subcategory.strip() == '':
                return {
                    'is_valid': True,
                    'action': 'move_to_uncategorized',
                    'warning': 'Product will be moved to Uncategorized category'
                }
            
            # Check if subcategory exists
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
            return {'is_valid': False, 'error': f'Validation error: {str(e)}'}

