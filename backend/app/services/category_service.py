from datetime import datetime
from ..database import db_manager
from ..models import Category
import logging
import re
from .audit_service import AuditLogService
from notifications.services import notification_service

logger = logging.getLogger(__name__)

class CategoryService:
    def __init__(self):
        """Initialize CategoryService with string-based architecture"""
        self.db = db_manager.get_database()
        self.collection = self.db.category
        self.product_collection = self.db.products  
        self.audit_service = AuditLogService()
        self._ensure_indexes()

    # ================================================================
    # UTILITY METHODS
    # ================================================================

    def ensure_uncategorized_category_exists(self):
        """Ensure an 'Uncategorized' category exists, create if not"""
        try:
            # Check if uncategorized category already exists
            uncategorized = self.collection.find_one({
                '_id': 'UNCTGRY-001',
                'isDeleted': {'$ne': True}
            })
            
            if uncategorized:
                logger.info("Uncategorized category already exists")
                return uncategorized
            
            # Create default uncategorized category
            now = datetime.utcnow()
            uncategorized_data = {
                '_id': 'UNCTGRY-001',
                'category_name': 'Uncategorized',
                'description': 'Default category for products without specific categorization',
                'status': 'active',
                'sub_categories': [{
                    'subcategory_id': 'SUBCAT-00001',
                    'name': 'General',
                    'description': 'General uncategorized products',
                    'products': [],
                    'created_at': now.isoformat(),
                    'status': 'active'
                }],
                'isDeleted': False,
                'date_created': now.isoformat(),
                'last_updated': now.isoformat()
            }
            
            # Insert the category
            result = self.collection.insert_one(uncategorized_data)
            
            logger.info("Created default 'Uncategorized' category with ID: UNCTGRY-001")
            
            # Send notification about system initialization
            self._send_category_notification('created', 'Uncategorized', 'UNCTGRY-001', {
                'system_generated': True,
                'action_type': 'system_initialization'
            })
            
            return uncategorized_data
            
        except Exception as e:
            logger.error(f"Error ensuring uncategorized category exists: {e}")
            raise Exception(f"Error creating uncategorized category: {str(e)}")

    def generate_category_id(self):
        """Generate sequential CTGY-### ID"""
        try:
            # Use aggregation to find highest existing number
            pipeline = [
                {
                    '$match': {
                        'category_id': {'$regex': '^CTGY-\\d{3}$'}
                    }
                },
                {
                    '$addFields': {
                        'numeric_part': {
                            '$toInt': {'$substr': ['$category_id', 5, 3]}
                        }
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'max_number': {'$max': '$numeric_part'}
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            if result and result[0]['max_number'] is not None:
                next_number = result[0]['max_number'] + 1
            else:
                # Fallback to count-based approach
                next_number = self.collection.count_documents({}) + 1
            
            return f"CTGY-{next_number:03d}"
            
        except Exception as e:
            logger.error(f"Error generating category ID: {e}")
            # Emergency fallback
            import time
            fallback_number = int(time.time()) % 1000
            return f"CTGY-{fallback_number:03d}"

    def generate_subcategory_id(self):
        """Generate sequential SUBCAT-##### ID"""
        try:
            # Use aggregation to find highest existing number across all categories
            pipeline = [
                {"$unwind": "$sub_categories"},
                {
                    '$match': {
                        'sub_categories.subcategory_id': {'$regex': '^SUBCAT-\\d{5}$'}
                    }
                },
                {
                    '$addFields': {
                        'numeric_part': {
                            '$toInt': {'$substr': ['$sub_categories.subcategory_id', 7, 5]}
                        }
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'max_number': {'$max': '$numeric_part'}
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            if result and result[0]['max_number'] is not None:
                next_number = result[0]['max_number'] + 1
            else:
                next_number = 1
            
            return f"SUBCAT-{next_number:05d}"
            
        except Exception as e:
            logger.error(f"Error generating subcategory ID: {e}")
            # Emergency fallback
            import time
            fallback_number = int(time.time()) % 100000
            return f"SUBCAT-{fallback_number:05d}"

    def _ensure_indexes(self):
        """Create indexes for string-based operations"""
        try:
            indexes = [
                [("category_id", 1), ("isDeleted", 1)],
                [("category_name", 1), ("isDeleted", 1)],
                [("status", 1), ("isDeleted", 1)],
                [("sub_categories.products.product_id", 1)],
                [("sub_categories.name", 1)]
            ]
            
            for index_fields in indexes:
                self.collection.create_index(index_fields, background=True)
                
            logger.info("String-based indexes created successfully")
        except Exception as e:
            logger.warning(f"Could not create indexes: {e}")

    def _validate_category_data(self, category_data):
        """Validate category data before processing"""
        if not category_data:
            raise ValueError("Category data is required")
        
        category_name = category_data.get("category_name", "").strip()
        if not category_name:
            raise ValueError("Category name is required")
        
        # Check for duplicates using string operations
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
        """Prepare subcategories with string IDs"""
        subcategories_list = existing_sub_categories or []
        
        # Check if "None" subcategory already exists
        none_exists = any(
            sub.get('name', '').lower() == 'none' 
            for sub in subcategories_list
        )
        
        if not none_exists:
            default_none = {
                'subcategory_id': self.generate_subcategory_id(),  # String ID
                'name': "None",
                'description': "Default holding subcategory for products without specific subcategorization",
                'products': [],
                'created_at': datetime.utcnow(),
                'status': 'active'
            }
            subcategories_list.insert(0, default_none)
            logger.debug("Auto-added 'None' subcategory with string ID")
        
        # Process existing subcategories and ensure they have string IDs
        processed_subcategories = []
        for sub in subcategories_list:
            # If subcategory doesn't have an ID, generate one
            if not sub.get('subcategory_id'):
                sub['subcategory_id'] = self.generate_subcategory_id()
            
            clean_sub = {
                'subcategory_id': sub['subcategory_id'],  # String ID
                'name': sub.get('name', ''),
                'description': sub.get('description', ''),
                'products': sub.get('products', []),
                'created_at': sub.get('created_at', datetime.utcnow()),
                'status': sub.get('status', 'active')
            }
            processed_subcategories.append(clean_sub)
        
        return processed_subcategories
    
    def _send_category_notification(self, action_type, category_name, category_id=None, additional_metadata=None):
        """Centralized notification helper for category actions"""
        try:
            # Define notification templates - UPDATED with missing ones
            templates = {
                'created': {
                    'title': "Category Created",
                    'message': f"Category '{category_name}' has been created",
                    'priority': "medium"
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
                    'message': f"Category '{category_name}' has been permanently deleted",
                    'priority': "high"
                },
                'restored': {
                    'title': "Category Restored",
                    'message': f"Category '{category_name}' has been restored",
                    'priority': "medium"
                },
                'bulk_created': {
                    'title': "Categories Bulk Created",
                    'message': f"Multiple categories created including '{category_name}'",
                    'priority': "low"
                },
                'bulk_updated': {
                    'title': "Categories Bulk Updated",
                    'message': f"Multiple categories updated including '{category_name}'",
                    'priority': "low"
                },
                # MISSING TEMPLATES - ADDED:
                'subcategory_added': {
                    'title': "Subcategory Added",
                    'message': f"Subcategory added to category '{category_name}'",
                    'priority': "low"
                },
                'subcategory_removed': {
                    'title': "Subcategory Removed", 
                    'message': f"Subcategory removed from category '{category_name}'",
                    'priority': "low"
                }
            }
            
            template = templates.get(action_type)
            if not template:
                logger.warning(f"Unknown notification action type: {action_type}")
                return
            
            # Prepare metadata
            metadata = {
                "category_id": str(category_id) if category_id else "",
                "category_name": category_name,
                "action_type": f"category_{action_type}"
            }
            
            # Add additional metadata if provided
            if additional_metadata and isinstance(additional_metadata, dict):
                metadata.update(additional_metadata)
            
            # Send notification
            notification_service.create_notification(
                title=template['title'],
                message=template['message'],
                priority=template['priority'],
                notification_type="system",
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to send category notification: {e}")
    
    def create_category(self, category_data, current_user=None):
        try:
            category_name = self._validate_category_data(category_data)
            logger.info(f"Creating category: {category_name}")
            
            # Generate string ID
            category_id = self.generate_category_id()
            
            # Prepare subcategories
            existing_sub_categories = category_data.get("sub_categories", [])
            sub_categories = self._prepare_subcategories(existing_sub_categories)
            
            # Add timestamps and default values
            now = datetime.utcnow()
            category_kwargs = {
                '_id': category_id,
                'category_name': category_name,
                'description': category_data.get("description", ''),
                'status': category_data.get("status", 'active'),
                'sub_categories': sub_categories,
                'isDeleted': False,
                'date_created': now.isoformat(),
                'last_updated': now.isoformat()
            }
            
            # Add image fields if present
            image_fields = ['image_url', 'image_filename', 'image_size', 'image_type', 'image_uploaded_at']
            for field in image_fields:
                if field in category_data and category_data[field] is not None:
                    category_kwargs[field] = category_data[field]
            
            # Create and insert category
            category = Category(**category_kwargs)
            self.collection.insert_one(category.to_dict())
            
            # Send notification
            self._send_category_notification('created', category_name, category_id)
            
            # Audit logging - use the clean data we already have
            if current_user and self.audit_service:
                try:
                    audit_data = {**category_kwargs, "category_id": category_id}
                    self.audit_service.log_category_create(current_user, audit_data)
                    logger.debug("Audit log created for category creation")
                except Exception as audit_error:
                    logger.error(f"Audit logging failed: {audit_error}")
            
            logger.info(f"Category '{category_name}' created successfully with ID {category_id}")
            
            # Return the clean data instead of querying back
            return category_kwargs

        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
            raise Exception(f"Validation error: {str(ve)}")
        except Exception as e:
            logger.error(f"Error creating category: {e}", exc_info=True)
            raise Exception(f"Error creating category: {str(e)}")
    
    def get_all_categories(self, include_deleted=False, limit=None, skip=None):
        """Get all categories with string ID operations"""
        try:
            # Ensure uncategorized category exists first
            self.ensure_uncategorized_category_exists()
            
            query = {}
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
            
            cursor = self.collection.find(query)
            
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            
            categories = list(cursor)
            return categories
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            raise Exception(f"Error getting categories: {str(e)}")
    
    def get_category_by_id(self, category_id, include_deleted=False):
        """Get category by string ID"""
        try:
            if not category_id or not category_id.startswith('CTGY-'):
                return None
            
            query = {'_id': category_id}  # Use _id instead of category_id
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}

            category = self.collection.find_one(query)
            return category
        except Exception as e:
            logger.error(f"Error getting category by ID {category_id}: {e}")
            raise Exception(f"Error getting category: {str(e)}")
        
    def update_category(self, category_id, category_data, current_user=None):
        """Update category with string ID operations"""
        try:
            logger.info(f"Updating category {category_id}")
            if current_user:
                logger.info(f"Updated by: {current_user['username']}")
            
            if not category_id or not category_id.startswith('CTGY-'):
                return None
            
            # Get current category data for audit
            old_category = self.collection.find_one({
                '_id': category_id,
                'isDeleted': {'$ne': True}
            })
            
            if not old_category:
                return None
            
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
                        '_id': {'$ne': category_id}
                    })
                    if existing:
                        raise ValueError(f"Category name '{new_name}' already exists")

            result = self.collection.update_one(
                {
                    '_id': category_id,
                    'isDeleted': {'$ne': True}
                },
                {'$set': update_data}
            )
            
            if result.modified_count == 0:
                return None

            updated_category = self.collection.find_one({'_id': category_id})
            
            # Send notification
            self._send_category_notification('updated', updated_category['category_name'], category_id)
            
            # Audit logging
            if current_user and self.audit_service:
                try:
                    self.audit_service.log_action(
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
        """Soft delete category with string ID operations"""
        try:
            logger.info(f"Soft deleting category {category_id}")
            if current_user:
                logger.info(f"Deleted by: {current_user['username']}")
            
            if not category_id or not category_id.startswith('CTGY-'):
                return False
            
            # Get category data before deletion (only active categories)
            category_to_delete = self.collection.find_one({
                'category_id': category_id,
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
            
            # Update category using string ID
            result = self.collection.update_one(
                {'category_id': category_id},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                # Send notification
                self._send_category_notification('soft_deleted', category_to_delete['category_name'], category_id)
                
                # Audit logging
                if current_user and self.audit_service:
                    try:
                        category_for_audit = category_to_delete.copy()
                        category_for_audit['deletion_type'] = 'soft_delete'
                        
                        self.audit_service.log_action(current_user, category_for_audit)
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
            
            if not category_id or not category_id.startswith('CTGY-'):
                return False
            
            # Find deleted category using string ID
            deleted_category = self.collection.find_one({
                'category_id': category_id,
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
            
            # Restore category using string ID
            result = self.collection.update_one(
                {'category_id': category_id},
                {'$set': restore_data, '$unset': unset_data}
            )
            
            if result.modified_count > 0:
                restored_category = self.collection.find_one({'category_id': category_id})
                
                # Send notification
                self._send_category_notification('restored', restored_category['category_name'], category_id)
                
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
            
            if not category_id or not category_id.startswith('CTGY-'):
                return False
            
            # Get category data before permanent deletion
            category_to_delete = self.collection.find_one({'category_id': category_id})
            if not category_to_delete:
                return False
            
            category_name = category_to_delete.get('category_name', 'Unknown Category')
            
            # Permanently delete from collection using string ID
            result = self.collection.delete_one({'category_id': category_id})
            
            if result.deleted_count > 0:
                # Send critical notification with enhanced metadata
                self._send_category_notification('hard_deleted', category_name, category_id, {
                    "warning": "PERMANENT_DELETION",
                    "deleted_by": current_user.get('username') if current_user else 'system'
                })
                
                # Audit logging
                if current_user and self.audit_service:
                    try:
                        category_for_audit = category_to_delete.copy()
                        category_for_audit['deletion_type'] = 'hard_delete'
                        
                        self.audit_service.log_action(current_user, category_for_audit)
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
            return categories
        except Exception as e:
            logger.error(f"Error getting deleted categories: {e}")
            raise Exception(f"Error getting deleted categories: {str(e)}")
    
   
    def _resolve_product(self, product_identifier):
        """
        Resolve product identifier to get both string ID and name
        Updated to work with PROD-##### string IDs
        """
        try:
            product = None
            
            # Case 1: PROD-##### string ID
            if isinstance(product_identifier, str):
                if product_identifier.startswith('PROD-'):
                    # Direct lookup by string ID
                    product = self.product_collection.find_one({'product_id': product_identifier})
                else:
                    # Try as product name (case-insensitive)
                    product = self.product_collection.find_one({
                        'product_name': {'$regex': f'^{re.escape(product_identifier.strip())}$', '$options': 'i'}
                    })
            
            # Case 2: Dictionary with product data (from imports)
            elif isinstance(product_identifier, dict):
                if 'product_id' in product_identifier:
                    product_id = product_identifier['product_id']
                    product = self.product_collection.find_one({'product_id': product_id})
                elif 'product_name' in product_identifier:
                    product = self.product_collection.find_one({
                        'product_name': product_identifier['product_name']
                    })
            
            if not product:
                raise ValueError(f"Product not found: {product_identifier}")
            
            return {
                'id': product['product_id'],  # Now returns string ID
                'name': product['product_name']
            }
            
        except Exception as e:
            raise ValueError(f"Failed to resolve product: {str(e)}")
        
    def add_product_to_subcategory(self, category_id, subcategory_name, product_identifier, current_user=None):
        """Add product to subcategory using string IDs"""
        try:
            logger.info(f"Adding product '{product_identifier}' to subcategory '{subcategory_name}' in category {category_id}")
            
            if not category_id or not category_id.startswith('CTGY-'):
                raise ValueError("Invalid category ID")
            
            if not subcategory_name or not subcategory_name.strip():
                raise ValueError("Subcategory name is required")
            
            # Get and validate category using string ID
            category = self.collection.find_one({
                'category_id': category_id,
                'isDeleted': {'$ne': True}
            })
            
            if not category:
                raise ValueError("Category not found or deleted")
            
            # Check if subcategory exists
            subcategory_exists = any(
                sub['name'] == subcategory_name 
                for sub in category.get('sub_categories', [])
            )
            
            if not subcategory_exists:
                raise ValueError(f"Subcategory '{subcategory_name}' not found in category")
            
            # Resolve product - get both string ID and name
            product_data = self._resolve_product(product_identifier)
            product_id = product_data['id']  # This should be PROD-##### 
            product_name = product_data['name']
            
            # Check if product already exists in this subcategory
            for subcategory in category.get('sub_categories', []):
                if subcategory['name'] == subcategory_name:
                    products = subcategory.get('products', [])
                    if products and isinstance(products[0], dict):
                        existing_product_ids = [p['product_id'] for p in products]
                        if product_id in existing_product_ids:
                            return {
                                'success': True,
                                'action': 'no_change',
                                'message': f"Product '{product_name}' already exists in subcategory '{subcategory_name}'"
                            }
                                    
            # Remove product from any other subcategory first
            self._remove_product_from_all_subcategories(product_id)
            
            # Add to subcategory with combined format using string IDs
            result = self.collection.update_one(
                {'_id': category_id},
                {
                    '$addToSet': {
                        'sub_categories.$[elem].products': {
                            'product_id': product_id,        # String: PROD-#####
                            'product_name': product_name,    # String: Product Name
                            'added_at': datetime.utcnow()    # Datetime (serializable)
                        }
                    },
                    '$set': {
                        'sub_categories.$[elem].updated_at': datetime.utcnow(),
                        'last_updated': datetime.utcnow()
                    }
                },
                array_filters=[{'elem.name': subcategory_name}]
            )
            
            if result.modified_count > 0:
                # Update product document with category reference using string IDs
                self.product_collection.update_one(
                    {'product_id': product_id},
                    {
                        '$set': {
                            'category_id': category_id,  # String category ID
                            'subcategory_name': subcategory_name,
                            'updated_at': datetime.utcnow()
                        }
                    }
                )
                
                logger.info(f"Successfully added product '{product_name}' to subcategory '{subcategory_name}'")
                
                return {
                    'success': True,
                    'action': 'added',
                    'product_id': product_id,
                    'product_name': product_name,
                    'category_id': category_id,
                    'subcategory_name': subcategory_name,
                    'message': f"Product '{product_name}' added to subcategory '{subcategory_name}'"
                }
            
            return {'success': False, 'message': 'Failed to add product to subcategory'}
            
        except Exception as e:
            logger.error(f"Error adding product to subcategory: {e}")
            raise Exception(f"Error adding product to subcategory: {str(e)}")

    def _remove_product_from_all_subcategories(self, product_id):
        """Remove product from all subcategories using string ID"""
        try:
            categories_with_product = self.collection.find({
                'sub_categories.products.product_id': product_id,
                'isDeleted': {'$ne': True}
            })
            
            for category in categories_with_product:
                self.collection.update_one(
                    {'category_id': category['category_id']},  # Use string ID
                    {
                        '$pull': {
                            'sub_categories.$[].products': {'product_id': product_id}
                        },
                        '$set': {'last_updated': datetime.utcnow()}
                    }
                )
            
            logger.info(f"Removed product {product_id} from all subcategories")
            
        except Exception as e:
            logger.error(f"Error removing product from all subcategories: {e}")

    def remove_product_from_subcategory(self, category_id, subcategory_name, product_identifier, current_user=None):
        """Remove product from subcategory using string IDs"""
        try:
            logger.info(f"Removing product '{product_identifier}' from subcategory '{subcategory_name}' in category {category_id}")
            
            if not category_id or not category_id.startswith('CTGY-'):
                raise ValueError("Invalid category ID")
            
            if not subcategory_name or not subcategory_name.strip():
                raise ValueError("Subcategory name is required")
            
            # Get and validate category using string ID
            category = self.collection.find_one({
                'category_id': category_id,
                'isDeleted': {'$ne': True}
            })
            
            if not category:
                raise ValueError("Category not found or deleted")
            
            # Resolve product
            product_data = self._resolve_product(product_identifier)
            product_id = product_data['id']
            product_name = product_data['name']
            
            # Remove from subcategory using string IDs
            result = self.collection.update_one(
                {'category_id': category_id},
                {
                    '$pull': {
                        'sub_categories.$[elem].products': {'product_id': product_id}
                    },
                    '$set': {
                        'sub_categories.$[elem].updated_at': datetime.utcnow(),
                        'last_updated': datetime.utcnow()
                    }
                },
                array_filters=[{'elem.name': subcategory_name}]
            )
            
            if result.modified_count > 0:
                # Update product document to remove category reference
                self.product_collection.update_one(
                    {'product_id': product_id},
                    {
                        '$unset': {
                            'category_id': "",
                            'subcategory_name': ""
                        },
                        '$set': {
                            'updated_at': datetime.utcnow()
                        }
                    }
                )
                
                logger.info(f"Successfully removed product '{product_name}' from subcategory '{subcategory_name}'")
                
                return {
                    'success': True,
                    'action': 'removed',
                    'product_id': product_id,
                    'product_name': product_name,
                    'category_id': category_id,
                    'subcategory_name': subcategory_name,
                    'message': f"Product '{product_name}' removed from subcategory '{subcategory_name}'"
                }
            
            return {'success': False, 'message': 'Product not found in subcategory or no changes made'}
            
        except Exception as e:
            logger.error(f"Error removing product from subcategory: {e}")
            raise Exception(f"Error removing product from subcategory: {str(e)}")
    
    def get_active_categories(self, include_deleted=False):
        """Get only active categories"""
        try:
            query = {'status': 'active'}
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
            
            categories = list(self.collection.find(query))
            return categories
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
            return categories
        except Exception as e:
            logger.error(f"Error searching categories: {e}")
            raise Exception(f"Error searching categories: {str(e)}")
    
    def add_subcategory(self, category_id, subcategory_data, current_user=None):
        """Add a subcategory to a category"""
        try:
            logger.info(f"Adding subcategory to category {category_id}")
            if current_user:
                logger.info(f"Added by: {current_user['username']}")
            
            if not category_id or not category_id.startswith('CTGY-'):
                return False
            
            # Validate subcategory data
            if not subcategory_data or not subcategory_data.get('name', '').strip():
                raise ValueError("Subcategory name is required")
            
            # Check if category exists and is not deleted
            category = self.collection.find_one({
                'category_id': category_id,
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
                {'category_id': category_id},
                {
                    '$addToSet': {'sub_categories': subcategory_data},
                    '$set': {'last_updated': datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                # Send notification
                self._send_category_notification('subcategory_added', category.get('category_name', 'Unknown'), category_id, {
                    "subcategory_name": subcategory_data.get('name', 'Unknown'),
                    "action_type": "subcategory_added"
                })
                
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
            
            if not category_id or not category_id.startswith('CTGY-'):
                return False
            
            # Check if category exists and is not deleted
            category = self.collection.find_one({
                'category_id': category_id,
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
                {'category_id': category_id},
                {
                    '$pull': {'sub_categories': {'name': subcategory_name}},
                    '$set': {'last_updated': datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                self._send_category_notification('subcategory_removed', category.get('category_name', 'Unknown'), category_id, {
                    "subcategory_name": subcategory_name,
                    "action_type": "subcategory_removed"
                })
                
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
            if not category_id or not category_id.startswith('CTGY-'):
                return []
            
            category = self.collection.find_one(
                {
                    'category_id': category_id,
                    'isDeleted': {'$ne': True}
                },
                {'sub_categories': 1}
            )
            
            return category.get('sub_categories', []) if category else []
            
        except Exception as e:
            logger.error(f"Error getting subcategories: {e}")
            raise Exception(f"Error getting subcategories: {str(e)}")

    def get_subcategory_products_with_details(self, category_id, subcategory_name):
        """Get products in subcategory with full product details (ID + Name format)"""
        try:
            if not category_id or not category_id.startswith('CTGY-'):
                return []
                
            category = self.collection.find_one({'category_id': category_id})
            if not category:
                return []
            
            for subcategory in category.get('sub_categories', []):
                if subcategory['name'] == subcategory_name:
                    products = subcategory.get('products', [])
                    
                    # Return combined format with both ID and Name
                    if products and isinstance(products[0], dict):
                        return [
                            {
                                'product_id': p['product_id'],    # String ID: PROD-#####
                                'product_name': p['product_name'] # Product name
                            } 
                            for p in products
                        ]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting subcategory products: {e}")
            raise Exception(f"Error getting subcategory products: {str(e)}")
    
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
                                        'in': {'$size': {'$ifNull': ['$$sub.products', []]}}
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
        """Get information about a category before deletion"""
        try:
            if not category_id or not category_id.startswith('CTGY-'):
                return None
            
            category = self.collection.find_one({'category_id': category_id})
            if not category:
                return None
            
            # Count subcategories and products
            subcategories_count = len(category.get('sub_categories', []))
            products_count = 0
            
            for subcategory in category.get('sub_categories', []):
                products_count += len(subcategory.get('products', []))
            
            return {
                'category_id': category['category_id'],
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
            
            success_count = 0
            failed_count = 0
            errors = []
            
            for category_id in category_ids:
                try:
                    if not category_id.startswith('CTGY-'):
                        failed_count += 1
                        errors.append(f"Invalid category ID: {category_id}")
                        continue
                        
                    result = self.soft_delete_category(category_id, current_user)
                    if result:
                        success_count += 1
                    else:
                        failed_count += 1
                        errors.append(f"Failed to soft delete {category_id}")
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Error deleting {category_id}: {str(e)}")
            
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
            
            # Filter valid category IDs
            valid_ids = [cid for cid in category_ids if cid.startswith('CTGY-')]
            
            result = self.collection.update_many(
                {
                    'category_id': {'$in': valid_ids},
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
                self._send_category_notification('bulk_updated', f"{result.modified_count} categories", None, {
                    "updated_count": result.modified_count,
                    "new_status": new_status,
                    "action_type": "categories_bulk_status_update",
                    "updated_by": current_user.get('username') if current_user else 'system'
                })
            
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
    
    def _get_subcategory_product_ids(self, category_id, subcategory_name):
        """Get all product IDs in a specific subcategory (string format only)"""
        try:
            if not category_id or not category_id.startswith('CTGY-'):
                return []
                
            category = self.collection.find_one({'category_id': category_id})
            if not category:
                return []
            
            for subcategory in category.get('sub_categories', []):
                if subcategory['name'] == subcategory_name:
                    products = subcategory.get('products', [])
                    # Handle combined format only (ID + Name)
                    if products and isinstance(products[0], dict):
                        return [p['product_id'] for p in products]
                    return []
            
            return []
        except Exception as e:
            logger.error(f"Error getting subcategory products: {e}")
            return []

    def move_product_to_none_subcategory(self, product_id, category_id, current_user=None):
        """Move product to the 'None' subcategory within the same category"""
        try:
            logger.info(f"Moving product {product_id} to 'None' subcategory in category {category_id}")
            
            if not product_id.startswith('PROD-') or not category_id.startswith('CTGY-'):
                raise ValueError("Invalid product or category ID format")
            
            # Get product details
            product = self.product_collection.find_one({'product_id': product_id})
            if not product:
                raise ValueError(f"Product {product_id} not found")
            
            product_name = product.get('product_name')
            
            # Remove from current subcategory
            self._remove_product_from_all_subcategories(product_id)
            
            # Add to "None" subcategory
            result = self.collection.update_one(
                {'category_id': category_id},
                {
                    '$addToSet': {
                        'sub_categories.$[elem].products': {
                            'product_id': product_id,
                            'product_name': product_name
                        }
                    },
                    '$set': {'last_updated': datetime.utcnow()}
                },
                array_filters=[{'elem.name': 'None'}]
            )
            
            if result.modified_count > 0:
                # Update product document
                self.product_collection.update_one(
                    {'product_id': product_id},
                    {
                        '$set': {
                            'category_id': category_id,
                            'subcategory_name': 'None',
                            'updated_at': datetime.utcnow()
                        }
                    }
                )
                
                logger.info(f"Product moved to 'None' subcategory successfully")
                return {
                    'success': True,
                    'action': 'moved_to_none',
                    'message': f"Product '{product_name}' moved to 'None' subcategory"
                }
            
            return {'success': False, 'message': 'Failed to move product to None subcategory'}
            
        except Exception as e:
            logger.error(f"Error moving product to None subcategory: {e}")
            raise Exception(f"Error moving product to None subcategory: {str(e)}")
    
    