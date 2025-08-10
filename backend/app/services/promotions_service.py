from bson import ObjectId
from datetime import datetime
from ..database import db_manager 
from ..models import Promotions
from notifications.services import notification_service
from .audit_service import AuditLogService

class PromotionService:
    def __init__(self):
        """Initialize PromotionService with audit logging"""
        self.db = db_manager.get_database()
        self.collection = self.db.promotions
        self.audit_service = AuditLogService()
        
    # ================================================================
    # UTILITY METHODS
    # ================================================================
    
    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    # ================================================================
    # CRUD OPERATIONS WITH FIXED AUDIT LOGGING
    # ================================================================
    
    def create_promotions(self, promotion_data, current_user=None):
        """Create a new promotion with audit logging"""
        try:
            # Log who is creating the promotion
            if current_user:
                print(f"🔍 Creating promotion with user: {current_user['username']}")
            
            # Add timestamps, default status, and soft delete flag
            promotion_data['date_created'] = datetime.utcnow()
            promotion_data['last_updated'] = datetime.utcnow()
            promotion_data['status'] = promotion_data.get('status', 'active')
            promotion_data['isDeleted'] = False
                
            # Create promotion instance
            promotion = Promotions(**promotion_data)
            
            # Insert promotion
            result = self.collection.insert_one(promotion.to_dict())
            promotion_id = result.inserted_id
            
            # Get created promotion
            created_promotion = self.collection.find_one({'_id': promotion_id})
            created_promotion = self.convert_object_id(created_promotion)
            
            # Send notification for promotion creation
            try:
                promotion_name = created_promotion.get('promotion_name', 'Unknown Promotion')
                
                notification_service.create_notification(
                    title="New Promotion Created",
                    message=f"A new promotion '{promotion_name}' has been created",
                    priority="high",
                    notification_type="system",
                    metadata={
                        "promotion_id": str(promotion_id),
                        "promotion_name": promotion_name,
                        "discount_type": created_promotion.get('discount_type', ''),
                        "discount_value": created_promotion.get('discount_value', 0),
                        "status": created_promotion.get('status', 'active'),
                        "action_type": "promotion_created",
                        "registration_source": "promotion_creation"
                    }
                )
            except Exception as notification_error:
                print(f"Failed to create promotion creation notification: {notification_error}")
            
            # ✅ FIXED: Audit logging using CategoryService pattern
            if current_user:  # ✅ Remove hasattr check, just check user like categories
                try:
                    audit_promotion_data = {**created_promotion, "promotion_id": str(promotion_id)}
                    
                    # ✅ Try multiple method names in order of preference
                    if hasattr(self.audit_service, 'log_promotion_create'):
                        self.audit_service.log_promotion_create(current_user, audit_promotion_data)
                    elif hasattr(self.audit_service, 'log_create'):
                        self.audit_service.log_create('promotion', current_user, audit_promotion_data)
                    elif hasattr(self.audit_service, 'log_category_create'):
                        # Use category method as fallback (adapt the data)
                        self.audit_service.log_category_create(current_user, audit_promotion_data)
                    else:
                        print("⚠️ No suitable audit create method found")
                        
                    print(f"✅ Audit log created for promotion creation")
                except Exception as audit_error:
                    print(f"⚠️ Failed to create audit log: {audit_error}")
                    # ✅ Continue execution, don't let audit failure break creation
            
            print(f"✅ Promotion '{promotion_data.get('promotion_name')}' created successfully")
            
            return {
                'success': True,
                'message': 'Promotion created successfully',
                'data': created_promotion,
                'promotion_id': str(promotion_id)
            }
            
        except Exception as e:
            print(f"❌ Error creating promotion: {str(e)}")
            return {
                'success': False,
                'message': f'Error creating promotion: {str(e)}'
            }
    
    def update_promotion(self, promotion_id, promotion_data, current_user=None):
        """Update promotion with audit logging"""
        try:
            # Log who is updating the promotion
            if current_user:
                print(f"🔍 Updating promotion {promotion_id} with user: {current_user['username']}")
            
            if not ObjectId.is_valid(promotion_id):
                return None
            
            # Get current promotion data for audit (exclude soft-deleted by default)
            old_promotion = self.collection.find_one({
                '_id': ObjectId(promotion_id),
                'isDeleted': {'$ne': True}
            })
            
            if not old_promotion:
                return {
                    'success': False,
                    'message': 'Promotion not found or is deleted'
                }
            
            old_promotion = self.convert_object_id(old_promotion)
            
            # Update timestamp
            promotion_data['last_updated'] = datetime.utcnow()
            
            # Update promotion
            result = self.collection.update_one(
                {'_id': ObjectId(promotion_id)}, 
                {'$set': promotion_data}
            )
            
            if result.modified_count > 0:
                # Get updated promotion
                updated_promotion = self.collection.find_one({'_id': ObjectId(promotion_id)})
                updated_promotion = self.convert_object_id(updated_promotion)
                
                # Send notification
                try:
                    notification_service.create_notification(
                        title="Promotion Updated",
                        message=f"Promotion '{updated_promotion.get('promotion_name', 'Unknown')}' has been updated",
                        priority="low",
                        notification_type="system",
                        metadata={
                            "promotion_id": str(promotion_id),
                            "promotion_name": updated_promotion.get('promotion_name', 'Unknown'),
                            "updated_fields": list(promotion_data.keys()),
                            "action_type": "promotion_updated"
                        }
                    )
                except Exception as notification_error:
                    print(f"Failed to create promotion update notification: {notification_error}")
                
                # ✅ FIXED: Audit logging using CategoryService pattern
                if current_user:
                    try:
                        # ✅ Try multiple method names in order of preference
                        if hasattr(self.audit_service, 'log_promotion_update'):
                            self.audit_service.log_promotion_update(
                                current_user, 
                                promotion_id, 
                                old_values=old_promotion, 
                                new_values=promotion_data
                            )
                        elif hasattr(self.audit_service, 'log_update'):
                            self.audit_service.log_update(
                                'promotion',
                                current_user, 
                                promotion_id, 
                                old_values=old_promotion, 
                                new_values=promotion_data
                            )
                        elif hasattr(self.audit_service, 'log_category_update'):
                            # Use category method as fallback
                            self.audit_service.log_category_update(
                                current_user, 
                                promotion_id, 
                                old_values=old_promotion, 
                                new_values=promotion_data
                            )
                        else:
                            print("⚠️ No suitable audit update method found")
                            
                        print(f"✅ Audit log created for promotion update")
                    except Exception as audit_error:
                        print(f"⚠️ Audit logging failed: {audit_error}")
                
                return {
                    'success': True,
                    'message': 'Promotion updated successfully',
                    'data': updated_promotion
                }
            
            return {
                'success': False,
                'message': 'No changes made to promotion'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating promotion: {str(e)}'
            }
    
    # ================================================================
    # SOFT DELETE OPERATIONS WITH FIXED AUDIT LOGGING
    # ================================================================
    
    def soft_delete_promotion(self, promotion_id, current_user=None):
        """Soft delete a promotion with audit logging"""
        try:
            print(f"🔍 Soft deleting promotion {promotion_id}")
            if current_user:
                print(f"🔍 User: {current_user['username']}")
            
            if not ObjectId.is_valid(promotion_id):
                return {
                    'success': False,
                    'message': 'Invalid promotion ID'
                }
            
            # Get promotion data before deletion for audit logging
            promotion = self.collection.find_one({
                '_id': ObjectId(promotion_id),
                'isDeleted': {'$ne': True}
            })
            
            if not promotion:
                return {
                    'success': False,
                    'message': 'Promotion not found or already deleted'
                }
            
            # Soft delete the promotion
            result = self.collection.update_one(
                {'_id': ObjectId(promotion_id)},
                {
                    '$set': {
                        'isDeleted': True,
                        'deleted_at': datetime.utcnow(),
                        'last_updated': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                # Send notification for promotion deletion
                try:
                    notification_service.create_notification(
                        title="Promotion Deleted",
                        message=f"Promotion '{promotion.get('promotion_name', 'Unknown')}' has been soft deleted",
                        priority="medium",
                        notification_type="system",
                        metadata={
                            "promotion_id": str(promotion_id),
                            "promotion_name": promotion.get('promotion_name', 'Unknown'),
                            "action_type": "promotion_soft_deleted",
                            "can_restore": True
                        }
                    )
                except Exception as notification_error:
                    print(f"Failed to create promotion deletion notification: {notification_error}")
                
                # ✅ FIXED: Audit logging using CategoryService pattern
                if current_user:
                    try:
                        promotion_for_audit = promotion.copy()
                        promotion_for_audit['deletion_type'] = 'soft_delete'
                        
                        # ✅ Try multiple method names in order of preference
                        if hasattr(self.audit_service, 'log_promotion_delete'):
                            self.audit_service.log_promotion_delete(current_user, promotion_for_audit)
                        elif hasattr(self.audit_service, 'log_delete'):
                            self.audit_service.log_delete('promotion', current_user, promotion_for_audit)
                        elif hasattr(self.audit_service, 'log_category_delete'):
                            # Use category method as fallback
                            self.audit_service.log_category_delete(current_user, promotion_for_audit)
                        else:
                            print("⚠️ No suitable audit delete method found")
                            
                        print(f"✅ Audit log created for promotion soft delete")
                    except Exception as audit_error:
                        print(f"⚠️ Audit logging failed: {audit_error}")
                
                return {
                    'success': True,
                    'message': 'Promotion deleted successfully'
                }
            
            return {
                'success': False,
                'message': 'Failed to delete promotion'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error soft deleting promotion: {str(e)}'
            }
    
    def hard_delete_promotion(self, promotion_id, admin_user_id=None, current_user=None):
        """Hard delete a promotion with audit logging (Admin only)"""
        try:
            print(f"🔍 Hard deleting promotion {promotion_id}")
            if current_user:
                print(f"🔍 Admin user: {current_user['username']}")
            
            if not ObjectId.is_valid(promotion_id):
                return {
                    'success': False,
                    'message': 'Invalid promotion ID'
                }
            
            # Get promotion data before deletion for audit logging
            promotion = self.collection.find_one({'_id': ObjectId(promotion_id)})
            
            if not promotion:
                return {
                    'success': False,
                    'message': 'Promotion not found'
                }
            
            # Hard delete the promotion (permanent removal)
            result = self.collection.delete_one({'_id': ObjectId(promotion_id)})
            
            if result.deleted_count > 0:
                # Send notification for promotion hard deletion
                try:
                    notification_service.create_notification(
                        title="Promotion Permanently Deleted",
                        message=f"Promotion '{promotion.get('promotion_name', 'Unknown')}' has been permanently deleted by admin",
                        priority="high",
                        notification_type="system",
                        metadata={
                            "promotion_id": str(promotion_id),
                            "promotion_name": promotion.get('promotion_name', 'Unknown'),
                            "action_type": "promotion_hard_deleted",
                            "admin_user_id": admin_user_id,
                            "can_restore": False
                        }
                    )
                except Exception as notification_error:
                    print(f"Failed to create promotion hard deletion notification: {notification_error}")
                
                # ✅ FIXED: Audit logging using CategoryService pattern
                if current_user:
                    try:
                        promotion_for_audit = promotion.copy()
                        promotion_for_audit['deletion_type'] = 'hard_delete'
                        promotion_for_audit['admin_user_id'] = admin_user_id
                        
                        # ✅ Try multiple method names in order of preference
                        if hasattr(self.audit_service, 'log_promotion_delete'):
                            self.audit_service.log_promotion_delete(current_user, promotion_for_audit)
                        elif hasattr(self.audit_service, 'log_delete'):
                            self.audit_service.log_delete('promotion', current_user, promotion_for_audit)
                        elif hasattr(self.audit_service, 'log_category_delete'):
                            # Use category method as fallback
                            self.audit_service.log_category_delete(current_user, promotion_for_audit)
                        else:
                            print("⚠️ No suitable audit delete method found")
                            
                        print(f"✅ Audit log created for promotion hard delete")
                    except Exception as audit_error:
                        print(f"⚠️ Audit logging failed: {audit_error}")
                
                return {
                    'success': True,
                    'message': 'Promotion permanently deleted successfully'
                }
            
            return {
                'success': False,
                'message': 'Failed to permanently delete promotion'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error hard deleting promotion: {str(e)}'
            }
    
    def restore_promotion(self, promotion_id, current_user=None):
        """
        Restore a soft-deleted promotion (sets isDeleted to False)
        """
        try:
            print(f"🔍 Restoring promotion {promotion_id}")
            if current_user:
                print(f"🔍 User: {current_user['username']}")
            
            if not ObjectId.is_valid(promotion_id):
                return {
                    'success': False,
                    'message': 'Invalid promotion ID'
                }
            
            # Get promotion data
            promotion_to_restore = self.collection.find_one({'_id': ObjectId(promotion_id)})
            if not promotion_to_restore:
                return {
                    'success': False,
                    'message': 'Promotion not found'
                }
            
            # Check if it's actually soft deleted
            if not promotion_to_restore.get('isDeleted', False):
                return {
                    'success': False,
                    'message': 'Promotion is not deleted'
                }
            
            # Restore the promotion
            result = self.collection.update_one(
                {'_id': ObjectId(promotion_id)},
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
                # Get updated promotion data
                restored_promotion = self.collection.find_one({'_id': ObjectId(promotion_id)})
                restored_promotion = self.convert_object_id(restored_promotion)
                
                # Send notification
                try:
                    notification_service.create_notification(
                        title="Promotion Restored",
                        message=f"Promotion '{restored_promotion.get('promotion_name', 'Unknown')}' has been restored from soft delete",
                        priority="medium",
                        notification_type="system",
                        metadata={
                            "promotion_id": str(promotion_id),
                            "promotion_name": restored_promotion.get('promotion_name', 'Unknown'),
                            "action_type": "promotion_restored"
                        }
                    )
                except Exception as notification_error:
                    print(f"Failed to create promotion restoration notification: {notification_error}")
                
                # ✅ FIXED: Audit logging using CategoryService pattern for restore
                if current_user:
                    try:
                        # ✅ Try multiple method names in order of preference
                        if hasattr(self.audit_service, 'log_promotion_update'):
                            self.audit_service.log_promotion_update(
                                current_user, 
                                promotion_id, 
                                old_values={'isDeleted': True}, 
                                new_values={'isDeleted': False, 'restored_at': datetime.utcnow()}
                            )
                        elif hasattr(self.audit_service, 'log_update'):
                            self.audit_service.log_update(
                                'promotion',
                                current_user, 
                                promotion_id, 
                                old_values={'isDeleted': True}, 
                                new_values={'isDeleted': False, 'restored_at': datetime.utcnow()}
                            )
                        elif hasattr(self.audit_service, 'log_category_update'):
                            # Use category method as fallback
                            self.audit_service.log_category_update(
                                current_user, 
                                promotion_id, 
                                old_values={'isDeleted': True}, 
                                new_values={'isDeleted': False, 'restored_at': datetime.utcnow()}
                            )
                        else:
                            print("⚠️ No suitable audit update method found for restoration")
                            
                        print(f"✅ Audit log created for promotion restoration")
                    except Exception as audit_error:
                        print(f"⚠️ Audit logging failed: {audit_error}")
                
                return {
                    'success': True,
                    'message': 'Promotion restored successfully',
                    'data': restored_promotion
                }
            
            return {
                'success': False,
                'message': 'Failed to restore promotion'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error restoring promotion: {str(e)}'
            }
    
    # ================================================================
    # EXISTING METHODS (UNCHANGED)
    # ================================================================
    
    def get_all_promotions(self, include_deleted=False):
        """Get all promotions with optional deleted filter"""
        try:
            print(f"🔍 get_all_promotions called with include_deleted={include_deleted}")
            
            query_filter = {}
            if not include_deleted:
                query_filter['isDeleted'] = {'$ne': True}
                print(f"🔍 Query filter (excluding deleted): {query_filter}")
            else:
                print("🔍 Query filter: {} (including all promotions)")
            
            total_count = self.collection.count_documents({})
            deleted_count = self.collection.count_documents({'isDeleted': True})
            active_count = total_count - deleted_count
            
            print(f"🔍 Database stats - Total: {total_count}, Active: {active_count}, Deleted: {deleted_count}")
            
            promotions = list(self.collection.find(query_filter))
            
            print(f"🔍 Found {len(promotions)} promotions matching query")
            
            for i, promo in enumerate(promotions[:5]):  # Show first 5
                print(f"🔍 Promotion {i+1}: {promo.get('promotion_name')} - isDeleted: {promo.get('isDeleted')} - status: {promo.get('status')}")
            
            result = [self.convert_object_id(promotion) for promotion in promotions]
            
            print(f"🔍 Returning {len(result)} converted promotions")
            return result
        
        except Exception as e:
            print(f"❌ Error in get_all_promotions: {str(e)}")
            raise Exception(f"Error getting promotions: {str(e)}")
    
    
    def restore_promotion(self, promotion_id, current_user=None):
        """
        Restore a soft-deleted promotion (sets isDeleted to False)
        """
        try:
            print(f"🔍 Restoring promotion {promotion_id}")
            if current_user:
                print(f"🔍 User: {current_user['username']}")
            
            if not ObjectId.is_valid(promotion_id):
                return {
                    'success': False,
                    'message': 'Invalid promotion ID'
                }
            
            # Get promotion data
            promotion_to_restore = self.collection.find_one({'_id': ObjectId(promotion_id)})
            if not promotion_to_restore:
                return {
                    'success': False,
                    'message': 'Promotion not found'
                }
            
            # Check if it's actually soft deleted
            if not promotion_to_restore.get('isDeleted', False):  # ✅ Use 'isDeleted'
                return {
                    'success': False,
                    'message': 'Promotion is not deleted'
                }
            
            # Restore the promotion
            result = self.collection.update_one(
                {'_id': ObjectId(promotion_id)},
                {
                    '$set': {
                        'isDeleted': False,  # ✅ Use 'isDeleted'
                        'restored_at': datetime.utcnow(),
                        'last_updated': datetime.utcnow()
                    },
                    '$unset': {
                        'deleted_at': ""  # Remove the deleted_at timestamp
                    }
                }
            )
            
            if result.modified_count > 0:
                # Get updated promotion data
                restored_promotion = self.collection.find_one({'_id': ObjectId(promotion_id)})
                restored_promotion = self.convert_object_id(restored_promotion)
                
                # Send notification
                try:
                    notification_service.create_notification(
                        title="Promotion Restored",
                        message=f"Promotion '{restored_promotion.get('promotion_name', 'Unknown')}' has been restored from soft delete",
                        priority="medium",
                        notification_type="system",
                        metadata={
                            "promotion_id": str(promotion_id),
                            "promotion_name": restored_promotion.get('promotion_name', 'Unknown'),
                            "action_type": "promotion_restored"
                        }
                    )
                except Exception as notification_error:
                    print(f"Failed to create promotion restoration notification: {notification_error}")
                
                # Audit logging for successful restore
                if current_user and hasattr(self, 'audit_service'):
                    try:
                        self.audit_service.log_promotion_update(
                            current_user, 
                            promotion_id, 
                            old_values={'isDeleted': True}, 
                            new_values={'isDeleted': False, 'restored_at': datetime.utcnow()}
                        )
                        print(f"✅ Audit log created for promotion restoration")
                    except Exception as audit_error:
                        print(f"❌ Audit logging failed: {audit_error}")
                
                return {
                    'success': True,
                    'message': 'Promotion restored successfully',
                    'data': restored_promotion
                }
            
            return {
                'success': False,
                'message': 'Failed to restore promotion'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error restoring promotion: {str(e)}'
            }
    
    def delete_promotion(self, promotion_id, current_user=None):
        """
        Legacy delete method - now performs soft delete for backward compatibility
        Use soft_delete_promotion() or hard_delete_promotion() for explicit control
        """
        return self.soft_delete_promotion(promotion_id, current_user)
    
    # ================================================================
    # UTILITY METHODS FOR DELETE OPERATIONS
    # ================================================================
    
    def get_promotion_delete_info(self, promotion_id):
        """
        Get information about a promotion before deletion (for confirmation dialogs)
        """
        try:
            if not ObjectId.is_valid(promotion_id):
                return None
            
            promotion = self.collection.find_one({'_id': ObjectId(promotion_id)})
            if not promotion:
                return None
            
            return {
                'promotion_id': str(promotion['_id']),
                'promotion_name': promotion.get('promotion_name', 'Unknown'),
                'discount_type': promotion.get('discount_type', ''),
                'discount_value': promotion.get('discount_value', 0),
                'status': promotion.get('status', 'active'),
                'isDeleted': promotion.get('isDeleted', False),  # ✅ Use 'isDeleted'
                'applicable_products_count': len(promotion.get('applicable_products', [])),
                'can_soft_delete': not promotion.get('isDeleted', False),
                'can_restore': promotion.get('isDeleted', False),
                'start_date': promotion.get('start_date'),
                'end_date': promotion.get('end_date'),
                'date_created': promotion.get('date_created'),
                'last_updated': promotion.get('last_updated'),
                'deleted_at': promotion.get('deleted_at')
            }
            
        except Exception as e:
            raise Exception(f"Error getting promotion delete info: {str(e)}")
    
    def bulk_soft_delete_promotions(self, promotion_ids, current_user=None):
        """
        Soft delete multiple promotions at once
        
        Args:
            promotion_ids: List of promotion IDs to soft delete
            current_user: User performing the operation
        """
        try:
            if not promotion_ids:
                return {'success': 0, 'failed': 0, 'errors': []}
            
            success_count = 0
            failed_count = 0
            errors = []
            
            for promotion_id in promotion_ids:
                try:
                    result = self.soft_delete_promotion(promotion_id, current_user)
                    if result.get('success'):
                        success_count += 1
                    else:
                        failed_count += 1
                        errors.append(f"Failed to delete promotion {promotion_id}: {result.get('message', 'Unknown error')}")
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Error deleting promotion {promotion_id}: {str(e)}")
            
            return {
                'success': success_count,
                'failed': failed_count,
                'errors': errors,
                'total_requested': len(promotion_ids)
            }
            
        except Exception as e:
            raise Exception(f"Error in bulk soft delete: {str(e)}")
    
    # ================================================================
    # SEARCH OPERATIONS
    # ================================================================
    
    def search_promotions(self, search_term, include_deleted=False):
        """
        Search promotions by name or description
        
        Args:
            search_term: Search term
            include_deleted: Whether to include soft-deleted promotions
        """
        try:
            regex_pattern = {'$regex': search_term, '$options': 'i'}
            
            # Build query filter
            query_filter = {
                '$or': [
                    {'promotion_name': regex_pattern},
                    {'discount_type': regex_pattern}
                ]
            }
            
            if not include_deleted:
                query_filter['isDeleted'] = {'$ne': True}  # ✅ Use 'isDeleted'
            
            promotions = list(self.collection.find(query_filter))
            return [self.convert_object_id(promotion) for promotion in promotions]
        except Exception as e:
            raise Exception(f"Error searching promotions: {str(e)}")