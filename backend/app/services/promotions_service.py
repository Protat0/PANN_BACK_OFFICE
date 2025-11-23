from bson import ObjectId
from datetime import datetime, timedelta, timezone 
from ..database import db_manager 
from ..models import Promotions
from notifications.services import NotificationService
from .audit_service import AuditLogService
from ..services.product_service import ProductService
from ..services.category_service import CategoryService
import logging

logger = logging.getLogger(__name__)

class PromotionService:
    def __init__(self):
        """Initialize PromotionService with audit logging"""
        self.db = db_manager.get_database()
        self.collection = self.db.promotions
        self.audit_service = AuditLogService()
        self.notification_service = NotificationService()
        self.product_service = ProductService()
        self.category_service = CategoryService()
        
    def generate_promotion_id(self):
        """Generate sequential PROM-#### ID"""
        try:
            pipeline = [
                {"$match": {"_id": {"$regex": "^PROM-\\d{4}$"}}},  # Changed to use _id
                {"$project": {
                    "numeric_part": {
                        "$toInt": {"$substr": ["$_id", 5, -1]}  # Changed to use _id
                    }
                }},
                {"$sort": {"numeric_part": -1}},
                {"$limit": 1}
            ]
            
            result = list(self.collection.aggregate(pipeline))
            if result:
                next_number = result[0]["numeric_part"] + 1
            else:
                next_number = 1
                
            return f"PROM-{next_number:04d}"  # This returns a string
            
        except Exception as e:
            logger.error(f"Error generating promotion ID: {e}")
            count = self.collection.count_documents({}) + 1
            return f"PROM-{count:04d}"
        
    def create_promotion(self, promotion_data):
        """Create new promotion with PROM-#### ID and audit logging"""
        try:
            # Generate promotion ID
            promotion_id = self.generate_promotion_id()
            
            # Validate promotion data
            validation_result = self._validate_promotion_data(promotion_data)
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'message': validation_result['message'],
                    'errors': validation_result['errors']
                }
                
            # Build promotion document - REMOVED is_active
            promotion = {
                '_id': promotion_id,
                'promotion_id': promotion_id,
                'name': promotion_data['name'],
                'description': promotion_data.get('description', ''),
                'type': promotion_data['type'],
                'discount_value': promotion_data['discount_value'],
                'discount_config': promotion_data.get('discount_config', {}),
                'target_type': promotion_data['target_type'],
                'target_ids': promotion_data.get('target_ids', []),
                'start_date': promotion_data['start_date'],
                'end_date': promotion_data['end_date'],
                'isDeleted': False,
                'usage_limit': promotion_data.get('usage_limit'),
                'current_usage': 0,
                'total_revenue_impact': 0.0,
                'usage_history': [],
                'created_by': promotion_data.get('created_by'),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'status': promotion_data.get('status', 'scheduled'),
            }
            
            # Insert promotion - now _id will be the string promotion_id
            self.collection.insert_one(promotion)
            
            # Log successful creation
            try:
                self.audit_service.log_promotion_create(
                    user_data={'user_id': promotion_data.get('created_by')},
                    promotion_data={
                        'promotion_id': promotion_id,
                        'name': promotion_data['name'],
                        'type': promotion_data['type'],
                        'discount_value': promotion_data['discount_value'],
                        'target_type': promotion_data['target_type'],
                        'target_ids': promotion_data.get('target_ids', []),
                        'start_date': promotion_data['start_date'],
                        'end_date': promotion_data['end_date'],
                        'usage_limit': promotion_data.get('usage_limit')
                    }
                )
            except Exception as audit_error:
                logger.warning(f"Audit logging failed: {audit_error}")
            
            # Send creation notification
            try:
                self._send_promotion_notification('created', promotion)
            except Exception as notification_error:
                logger.warning(f"Notification failed: {notification_error}")
            
            # Schedule activation/deactivation if needed
            try:
                self._schedule_promotion_lifecycle(promotion)
            except Exception as schedule_error:
                logger.warning(f"Scheduling failed: {schedule_error}")
            
            return {
                'success': True,
                'message': f'Promotion {promotion_id} created successfully',
                'promotion_id': promotion_id,
                'promotion': promotion
            }
            
        except Exception as e:
            logger.error(f"Error creating promotion: {e}")
            return {
                'success': False,
                'message': f'Error creating promotion: {str(e)}'
            }

    def update_promotion(self, promotion_id, update_data, user_id=None):
        """Update promotion with comprehensive audit logging"""
        try:
            # Get existing promotion for comparison
            existing_promotion = self.collection.find_one({'promotion_id': promotion_id})
            if not existing_promotion:
                # Log attempt to update non-existent promotion
                self.audit_service.log_action(
                    action='promotion_update_failed',
                    resource_type='promotion',
                    resource_id=promotion_id,
                    user_id=user_id,
                    changes={'reason': 'promotion_not_found'},
                    metadata={'attempted_update': update_data}
                )
                return {'success': False, 'message': 'Promotion not found'}
            
            # Validate update data
            validation_result = self._validate_promotion_update(update_data, existing_promotion)
            if not validation_result['is_valid']:
                # Log validation failure
                self.audit_service.log_action(
                    action='promotion_update_failed',
                    resource_type='promotion',
                    resource_id=promotion_id,
                    user_id=user_id,
                    changes={
                        'validation_errors': validation_result['errors'],
                        'attempted_changes': update_data
                    },
                    metadata={'reason': 'validation_failed'}
                )
                return {
                    'success': False,
                    'message': validation_result['message'],
                    'errors': validation_result['errors']
                }
            
            # Prepare update document
            update_doc = {
                '$set': {
                    **update_data,
                    'updated_at': datetime.utcnow(),
                    'updated_by': user_id
                }
            }
            
            # Track what changed for audit
            changes = self._detect_promotion_changes(existing_promotion, update_data)
            
            # Update promotion
            self.collection.update_one(
                {'promotion_id': promotion_id},
                update_doc
            )
            
            # Get updated promotion
            updated_promotion = self.collection.find_one({'promotion_id': promotion_id})
            
            # Log successful update
            self.audit_service.log_action(
                action='promotion_updated',
                resource_type='promotion',
                resource_id=promotion_id,
                user_id=user_id,
                changes={
                    'old_data': self._sanitize_promotion_data_for_audit(existing_promotion),
                    'new_data': self._sanitize_promotion_data_for_audit(updated_promotion),
                    'modified_fields': list(changes.keys()),
                    'field_changes': changes
                },
                metadata={
                    'update_type': self._classify_update_type(changes),
                    'status_changed': 'status' in changes,
                    'dates_modified': any(field in changes for field in ['start_date', 'end_date'])
                }
            )
            
            # Send notification if significant changes
            if self._requires_notification(changes):
                self._send_promotion_notification('updated', updated_promotion, {
                    'changes': changes,
                    'updated_by': user_id
                })
            
            return {
                'success': True,
                'message': f'Promotion {promotion_id} updated successfully',
                'changes': changes,
                'promotion': self._serialize_promotion_data(updated_promotion.copy())  # Add serialization
            }
            
        except Exception as e:
            logger.error(f"Error updating promotion {promotion_id}: {e}")
            # Log error
            self.audit_service.log_action(
                action='promotion_update_error',
                resource_type='promotion',
                resource_id=promotion_id,
                user_id=user_id,
                changes={'error': str(e), 'attempted_update': update_data},
                metadata={'error_type': 'system_error'}
            )
            return {'success': False, 'message': f'Error updating promotion: {str(e)}'}
        
    def activate_promotion(self, promotion_id, user_id=None, auto_activated=False):
        """Activate promotion with audit logging"""
        try:
            promotion = self.collection.find_one({'promotion_id': promotion_id})
            if not promotion:
                self.audit_service.log_action(
                    action='promotion_activation_failed',
                    resource_type='promotion',
                    resource_id=promotion_id,
                    user_id=user_id,
                    changes={'reason': 'promotion_not_found'},
                    metadata={'auto_activated': auto_activated}
                )
                return {'success': False, 'message': 'Promotion not found'}
            
            # Check if deleted
            if promotion.get('isDeleted'):
                return {'success': False, 'message': 'Cannot activate deleted promotion'}
            
            # Store pre-activation state
            pre_activation_status = promotion['status']
            
            # Validate promotion targets still exist
            validation_result = self._validate_promotion_targets(promotion)
            if not validation_result['is_valid']:
                self.audit_service.log_action(
                    action='promotion_activation_failed',
                    resource_type='promotion',
                    resource_id=promotion_id,
                    user_id=user_id,
                    changes={
                        'reason': 'target_validation_failed',
                        'validation_errors': validation_result['errors']
                    },
                    metadata={'auto_activated': auto_activated}
                )
                return {
                    'success': False,
                    'message': 'Promotion targets validation failed',
                    'errors': validation_result['errors']
                }
            
            # Check timing
            now = datetime.utcnow()
            if now < promotion['start_date'] and not auto_activated:
                self.audit_service.log_action(
                    action='promotion_activation_failed',
                    resource_type='promotion',
                    resource_id=promotion_id,
                    user_id=user_id,
                    changes={'reason': 'premature_activation'},
                    metadata={'start_date': promotion['start_date'].isoformat()}
                )
                return {'success': False, 'message': 'Promotion start date has not arrived'}
            
            if now > promotion['end_date']:
                self.audit_service.log_action(
                    action='promotion_activation_failed',
                    resource_type='promotion',
                    resource_id=promotion_id,
                    user_id=user_id,
                    changes={'reason': 'expired_promotion'},
                    metadata={'end_date': promotion['end_date'].isoformat()}
                )
                return {'success': False, 'message': 'Promotion has expired'}
            
            # Activate promotion - ONLY UPDATE STATUS
            self.collection.update_one(
                {'promotion_id': promotion_id},
                {
                    '$set': {
                        'status': 'active',
                        'activated_at': now,
                        'activated_by': user_id,
                        'updated_at': now
                    }
                }
            )
            
            # Get updated promotion
            updated_promotion = self.collection.find_one({'promotion_id': promotion_id})
            
            # Log successful activation
            self.audit_service.log_action(
                action='promotion_activated',
                resource_type='promotion',
                resource_id=promotion_id,
                user_id=user_id,
                changes={
                    'status_change': {'from': pre_activation_status, 'to': 'active'},
                    'activation_time': now.isoformat(),
                    'target_details': self._get_target_details(promotion)
                },
                metadata={
                    'auto_activated': auto_activated,
                    'promotion_type': promotion['type'],
                    'discount_value': promotion['discount_value'],
                    'expected_end_date': promotion['end_date'].isoformat()
                }
            )
            
            # Send activation notification
            self._send_promotion_notification('activated', updated_promotion)
            
            return {
                'success': True,
                'message': f'Promotion {promotion_id} activated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error activating promotion {promotion_id}: {e}")
            # Log error
            self.audit_service.log_action(
                action='promotion_activation_error',
                resource_type='promotion',
                resource_id=promotion_id,
                user_id=user_id,
                changes={'error': str(e)},
                metadata={'auto_activated': auto_activated, 'error_type': 'system_error'}
            )
            return {'success': False, 'message': f'Error activating promotion: {str(e)}'}

    def apply_promotion_to_order(self, order_data, customer_id=None):
        """Apply promotion to order with detailed usage audit"""
        try:
            # Get active promotions
            active_promotions = self.get_active_promotions()
            if not active_promotions['success'] or not active_promotions['promotions']:
                return {
                    'success': True,
                    'discount_applied': 0.0,
                    'promotion_used': None,
                    'message': 'No active promotions available'
                }
            
            best_promotion = None
            best_discount = 0.0
            evaluation_log = []
            
            # Evaluate each promotion and log the process
            for promotion in active_promotions['promotions']:
                discount = self._calculate_promotion_discount(promotion, order_data)
                evaluation_log.append({
                    'promotion_id': promotion['promotion_id'],
                    'calculated_discount': discount,
                    'eligible': discount > 0,
                    'usage_limit_ok': self._check_usage_limit(promotion)
                })
                
                if discount > best_discount and self._check_usage_limit(promotion):
                    best_promotion = promotion
                    best_discount = discount
            
            if not best_promotion:
                # Log no applicable promotion found
                self.audit_service.log_action(
                    action='promotion_application_no_match',
                    resource_type='promotion',
                    resource_id='multiple',
                    user_id=customer_id,
                    changes={
                        'order_summary': self._create_order_summary_for_audit(order_data),
                        'promotions_evaluated': evaluation_log,
                        'reason': 'no_applicable_promotions'
                    },
                    metadata={'available_promotions': len(active_promotions['promotions'])}
                )
                
                return {
                    'success': True,
                    'discount_applied': 0.0,
                    'promotion_used': None,
                    'message': 'No applicable promotions for this order'
                }
            
            # Apply promotion and track usage
            usage_data = {
                'discount_amount': best_discount,
                'customer_id': customer_id,
                'order_summary': self._create_order_summary_for_audit(order_data),
                'used_at': datetime.utcnow()
            }
            
            self._track_promotion_usage(best_promotion['promotion_id'], usage_data)
            
            # Log successful promotion application
            self.audit_service.log_action(
                action='promotion_applied',
                resource_type='promotion',
                resource_id=best_promotion['promotion_id'],
                user_id=customer_id,
                changes={
                    'discount_applied': best_discount,
                    'order_summary': usage_data['order_summary'],
                    'promotions_evaluated': evaluation_log,
                    'selected_promotion': {
                        'id': best_promotion['promotion_id'],
                        'name': best_promotion['name'],
                        'type': best_promotion['type'],
                        'discount_value': best_promotion['discount_value']
                    }
                },
                metadata={
                    'promotion_type': best_promotion['type'],
                    'usage_count_after': best_promotion['current_usage'] + 1,
                    'revenue_impact': best_discount
                }
            )
            
            return {
                'success': True,
                'discount_applied': best_discount,
                'promotion_used': best_promotion,
                'message': f'Promotion {best_promotion["promotion_id"]} applied'
            }
            
        except Exception as e:
            logger.error(f"Error applying promotion to order: {e}")
            # Log error
            self.audit_service.log_action(
                action='promotion_application_error',
                resource_type='promotion',
                resource_id='unknown',
                user_id=customer_id,
                changes={
                    'error': str(e),
                    'order_data': self._create_order_summary_for_audit(order_data)
                },
                metadata={'error_type': 'system_error'}
            )
            return {'success': False, 'message': f'Error applying promotion: {str(e)}'}

    def _sanitize_promotion_data_for_audit(self, promotion_data):
        """Sanitize promotion data for audit logging"""
        try:
            sanitized = {
                'promotion_id': promotion_data.get('promotion_id'),
                'name': promotion_data.get('name'),
                'type': promotion_data.get('type'),
                'discount_value': promotion_data.get('discount_value'),
                'target_type': promotion_data.get('target_type'),
                'target_ids': promotion_data.get('target_ids', []),
                'status': promotion_data.get('status'),
                'usage_limit': promotion_data.get('usage_limit'),
                'current_usage': promotion_data.get('current_usage', 0)
            }
            
            # Add formatted dates
            if promotion_data.get('start_date'):
                sanitized['start_date'] = promotion_data['start_date'].isoformat() if isinstance(promotion_data['start_date'], datetime) else promotion_data['start_date']
            
            if promotion_data.get('end_date'):
                sanitized['end_date'] = promotion_data['end_date'].isoformat() if isinstance(promotion_data['end_date'], datetime) else promotion_data['end_date']
                
            return sanitized
            
        except Exception as e:
            logger.error(f"Error sanitizing promotion data for audit: {e}")
            return {'error': 'sanitization_failed'}

    def _detect_promotion_changes(self, old_data, new_data):
        """Detect specific changes between promotion versions"""
        changes = {}
        
        # Track specific field changes
        trackable_fields = [
            'name', 'description', 'type', 'discount_value', 'target_type', 
            'target_ids', 'start_date', 'end_date', 'usage_limit', 'status'
        ]
        
        for field in trackable_fields:
            if field in new_data:
                old_value = old_data.get(field)
                new_value = new_data[field]
                
                # Handle datetime comparison
                if isinstance(old_value, datetime) and isinstance(new_value, datetime):
                    if old_value != new_value:
                        changes[field] = {
                            'from': old_value.isoformat(),
                            'to': new_value.isoformat()
                        }
                elif old_value != new_value:
                    changes[field] = {
                        'from': old_value,
                        'to': new_value
                    }
        
        return changes

    def _classify_update_type(self, changes):
        """Classify the type of update for metadata"""
        if 'status' in changes:
            return 'status_change'
        elif any(field in changes for field in ['start_date', 'end_date']):
            return 'schedule_change'
        elif any(field in changes for field in ['discount_value', 'type', 'target_ids', 'target_type']):
            return 'promotion_terms_change'
        elif any(field in changes for field in ['name', 'description']):
            return 'metadata_change'
        else:
            return 'general_update'

    def _get_target_details(self, promotion):
        """Get detailed information about promotion targets for audit"""
        try:
            target_details = {
                'target_type': promotion['target_type'],
                'target_count': len(promotion.get('target_ids', []))
            }
            
            if promotion['target_type'] == 'products' and promotion.get('target_ids'):
                # Get product names for audit context
                products = []
                for product_id in promotion['target_ids']:
                    product = self.product_service.get_product_by_id(product_id)
                    if product and product.get('success'):
                        products.append({
                            'id': product_id,
                            'name': product['product'].get('name', 'Unknown')
                        })
                target_details['target_products'] = products
            
            elif promotion['target_type'] == 'categories' and promotion.get('target_ids'):
                # ✅ FIX: Get category names for audit context
                categories = []
                for category_id in promotion['target_ids']:
                    try:
                        category = self.category_service.get_category_by_id(category_id)
                        if category:  # ✅ Check if category exists (not None)
                            categories.append({
                                'id': category_id,
                                'name': category.get('category_name', 'Unknown')
                            })
                    except Exception as e:
                        logger.error(f"Error getting category {category_id} for audit: {e}")
                target_details['target_categories'] = categories
            
            return target_details
            
        except Exception as e:
            logger.error(f"Error getting target details for audit: {e}")
            return {'error': 'target_details_unavailable'}

    def _create_order_summary_for_audit(self, order_data):
        """Create a summary of order data for audit purposes"""
        try:
            return {
                'total_amount': order_data.get('total_amount', 0),
                'item_count': len(order_data.get('items', [])),
                'product_ids': [item.get('product_id') for item in order_data.get('items', [])],
                'categories': list(set([item.get('category_id') for item in order_data.get('items', []) if item.get('category_id')]))
            }
        except Exception as e:
            logger.error(f"Error creating order summary for audit: {e}")
            return {'error': 'order_summary_unavailable'}

    def delete_promotion(self, promotion_id, user_id=None, soft_delete=True):
        """Delete promotion with comprehensive audit logging"""
        try:
            # Get existing promotion for audit
            existing_promotion = self.collection.find_one({'promotion_id': promotion_id})
            if not existing_promotion:
                self.audit_service.log_action(
                    action='promotion_delete_failed',
                    resource_type='promotion',
                    resource_id=promotion_id,
                    user_id=user_id,
                    changes={'reason': 'promotion_not_found'},
                    metadata={'soft_delete': soft_delete}
                )
                return {'success': False, 'message': 'Promotion not found'}
            
            # Check if promotion is currently active
            if existing_promotion.get('status') == 'active':
                self.audit_service.log_action(
                    action='promotion_delete_failed',
                    resource_type='promotion',
                    resource_id=promotion_id,
                    user_id=user_id,
                    changes={'reason': 'promotion_is_active'},
                    metadata={
                        'soft_delete': soft_delete,
                        'current_usage': existing_promotion.get('current_usage', 0)
                    }
                )
                return {'success': False, 'message': 'Cannot delete active promotion. Please deactivate first.'}
            
            if soft_delete:
                # Soft delete - mark as deleted
                self.collection.update_one(
                    {'promotion_id': promotion_id},
                    {
                        '$set': {
                            'status': 'deleted',
                            'isDeleted': True,
                            'deleted_at': datetime.utcnow(),
                            'deleted_by': user_id,
                            'updated_at': datetime.utcnow()
                        }
                    }
                )
                action = 'promotion_soft_deleted'
            else:
                # Hard delete - remove from database
                self.collection.delete_one({'promotion_id': promotion_id})
                action = 'promotion_hard_deleted'
            
            # Log successful deletion
            self.audit_service.log_action(
                action=action,
                resource_type='promotion',
                resource_id=promotion_id,
                user_id=user_id,
                changes={
                    'deleted_promotion_data': self._sanitize_promotion_data_for_audit(existing_promotion),
                    'usage_statistics': {
                        'total_usage': existing_promotion.get('current_usage', 0),
                        'revenue_impact': existing_promotion.get('total_revenue_impact', 0)
                    },
                    'deletion_reason': 'manual_deletion'
                },
                metadata={
                    'soft_delete': soft_delete,
                    'promotion_was_active': existing_promotion.get('status') == 'active',
                    'promotion_type': existing_promotion.get('type')
                }
            )
            
            delete_type = 'soft deleted' if soft_delete else 'permanently deleted'
            return {
                'success': True,
                'message': f'Promotion {promotion_id} {delete_type} successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deleting promotion {promotion_id}: {e}")
            # Log error
            self.audit_service.log_action(
                action='promotion_delete_error',
                resource_type='promotion',
                resource_id=promotion_id,
                user_id=user_id,
                changes={'error': str(e)},
                metadata={'soft_delete': soft_delete, 'error_type': 'system_error'}
            )
            return {'success': False, 'message': f'Error deleting promotion: {str(e)}'}
    
    def hard_delete_promotion(self, promotion_id, user_id, confirmation_token=None):
        """Permanently delete promotion - DANGEROUS operation"""
        try:
            if confirmation_token != "PERMANENT_DELETE_CONFIRMED":
                return {
                    'success': False, 
                    'message': 'Hard delete requires confirmation token'
                }
            
            existing_promotion = self.collection.find_one({'promotion_id': promotion_id})
            if not existing_promotion:
                return {'success': False, 'message': 'Promotion not found'}
            
            # Log before permanent deletion
            self.audit_service.log_action(
                action='promotion_hard_deleted',
                resource_type='promotion',
                resource_id=promotion_id,
                user_id=user_id,
                changes={
                    'permanently_deleted_data': self._sanitize_promotion_data_for_audit(existing_promotion),
                    'final_usage_stats': {
                        'total_usage': existing_promotion.get('current_usage', 0),
                        'revenue_impact': existing_promotion.get('total_revenue_impact', 0)
                    }
                },
                metadata={'deletion_type': 'permanent', 'confirmation_provided': True}
            )
            
            # Permanently delete
            result = self.collection.delete_one({'promotion_id': promotion_id})
            
            return {
                'success': result.deleted_count > 0,
                'message': f'Promotion {promotion_id} permanently deleted'
            }
            
        except Exception as e:
            logger.error(f"Error hard deleting promotion {promotion_id}: {e}")
            return {'success': False, 'message': f'Error permanently deleting promotion: {str(e)}'}
    
    def restore_promotion(self, promotion_id, user_id):
        """Restore soft-deleted promotion"""
        try:
            existing_promotion = self.collection.find_one({'promotion_id': promotion_id})
            if not existing_promotion:
                return {'success': False, 'message': 'Promotion not found'}
            
            if not existing_promotion.get('isDeleted'):
                return {'success': False, 'message': 'Promotion is not deleted'}
            
            # Restore promotion
            restore_status = 'scheduled'
            now = datetime.utcnow()
            
            # Determine appropriate status after restoration
            if now > existing_promotion['end_date']:
                restore_status = 'expired'
            elif now >= existing_promotion['start_date'] and now <= existing_promotion['end_date']:
                restore_status = 'scheduled'
            
            self.collection.update_one(
                {'promotion_id': promotion_id},
                {
                    '$set': {
                        'status': restore_status,
                        'isDeleted': False,
                        'restored_at': now,
                        'restored_by': user_id,
                        'updated_at': now
                    },
                    '$unset': {
                        'deleted_at': '',
                        'deleted_by': ''
                    }
                }
            )
            
            # Log restoration
            self.audit_service.log_action(
                action='promotion_restored',
                resource_type='promotion',
                resource_id=promotion_id,
                user_id=user_id,
                changes={
                    'status_change': {'from': 'deleted', 'to': restore_status},
                    'restoration_time': now.isoformat()
                },
                metadata={'restored_status': restore_status}
            )
            
            return {
                'success': True,
                'message': f'Promotion {promotion_id} restored successfully',
                'new_status': restore_status
            }
            
        except Exception as e:
            logger.error(f"Error restoring promotion {promotion_id}: {e}")
            return {'success': False, 'message': f'Error restoring promotion: {str(e)}'}
    
    def get_deleted_promotions(self, page=1, limit=20):
        """Get all soft-deleted promotions"""
        try:
            query = {'isDeleted': True}
            
            skip = (page - 1) * limit
            
            deleted_promotions = list(self.collection.find(query)
                                    .sort('deleted_at', -1)
                                    .skip(skip)
                                    .limit(limit))
            
            # Serialize promotions
            serialized_promotions = []
            for promotion in deleted_promotions:
                serialized_promotions.append(self._serialize_promotion_data(promotion))
            
            total_count = self.collection.count_documents(query)
            total_pages = (total_count + limit - 1) // limit
            
            return {
                'success': True,
                'promotions': serialized_promotions,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_count': total_count,
                    'has_next': page < total_pages,
                    'has_previous': page > 1
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting deleted promotions: {e}")
            return {'success': False, 'message': f'Error retrieving deleted promotions: {str(e)}'}

    def get_promotion_audit_history(self, promotion_id, limit=50):
        """Get comprehensive audit history for a specific promotion"""
        try:
            audit_history = self.audit_service.get_resource_audit_history(
                resource_type='promotion',
                resource_id=promotion_id,
                limit=limit
            )
            
            if audit_history['success']:
                # Enhance audit history with promotion-specific formatting
                enhanced_history = []
                for audit_entry in audit_history['audit_logs']:
                    enhanced_entry = {
                        **audit_entry,
                        'formatted_action': self._format_audit_action(audit_entry),
                        'impact_summary': self._create_impact_summary(audit_entry)
                    }
                    enhanced_history.append(enhanced_entry)
                
                return {
                    'success': True,
                    'audit_history': enhanced_history,
                    'total_entries': len(enhanced_history)
                }
            
            return audit_history
            
        except Exception as e:
            logger.error(f"Error getting promotion audit history: {e}")
            return {'success': False, 'message': f'Error retrieving audit history: {str(e)}'}

    def _format_audit_action(self, audit_entry):
        """Format audit action for human readability"""
        action_formatters = {
            'promotion_created': 'Promotion was created',
            'promotion_updated': 'Promotion was modified',
            'promotion_activated': 'Promotion was activated',
            'promotion_expired': 'Promotion expired',
            'promotion_applied': 'Promotion was used by customer',
            'promotion_soft_deleted': 'Promotion was soft deleted',
            'promotion_hard_deleted': 'Promotion was permanently deleted'
        }
        
        return action_formatters.get(audit_entry.get('action'), audit_entry.get('action', 'Unknown action'))

    def _create_impact_summary(self, audit_entry):
        """Create impact summary from audit entry"""
        try:
            changes = audit_entry.get('changes', {})
            metadata = audit_entry.get('metadata', {})
            
            if audit_entry.get('action') == 'promotion_applied':
                return f"Customer saved ${changes.get('discount_applied', 0):.2f}"
            elif audit_entry.get('action') == 'promotion_activated':
                return f"Made {metadata.get('promotion_type', 'promotion')} discount available"
            elif audit_entry.get('action') == 'promotion_created':
                return f"New {metadata.get('promotion_type', 'promotion')} targeting {metadata.get('target_type', 'products')}"
            elif audit_entry.get('action') == 'promotion_updated':
                modified_fields = changes.get('modified_fields', [])
                return f"Modified {', '.join(modified_fields)}"
            
            return "System action recorded"
            
        except Exception:
            return "Impact summary unavailable"
        
    def get_active_promotions(self):
        """Get all currently active promotions"""
        try:
            now = datetime.utcnow()
            
            active_promotions = list(self.collection.find({
                'isDeleted': {'$ne': True},
                'status': 'active',
                'start_date': {'$lte': now},
                'end_date': {'$gte': now}
            }).sort('created_at', -1))
            
            return {
                'success': True,
                'promotions': active_promotions,
                'count': len(active_promotions)
            }
            
        except Exception as e:
            logger.error(f"Error getting active promotions: {e}")
            return {'success': False, 'message': f'Error retrieving active promotions: {str(e)}'}

    def get_promotion_by_id(self, promotion_id):
        """Retrieve specific promotion by PROM-#### ID"""
        try:
            promotion = self.collection.find_one({'promotion_id': promotion_id})
            
            if not promotion:
                return {'success': False, 'message': 'Promotion not found'}
            
            # Add computed fields for display
            promotion['is_expired'] = datetime.utcnow() > promotion['end_date']
            promotion['days_remaining'] = (promotion['end_date'] - datetime.utcnow()).days if not promotion['is_expired'] else 0
            promotion['usage_percentage'] = (promotion['current_usage'] / promotion['usage_limit'] * 100) if promotion.get('usage_limit') else 0
            
            return {
                'success': True,
                'promotion': promotion
            }
            
        except Exception as e:
            logger.error(f"Error getting promotion {promotion_id}: {e}")
            return {'success': False, 'message': f'Error retrieving promotion: {str(e)}'}

    def get_all_promotions(self, filters=None, page=1, limit=20, sort_by='created_at', sort_order='desc'):
        """List promotions with filtering and pagination"""
        try:
            query = {}

            # Exclude deleted promotions by default
            if not filters or not filters.get('include_deleted'):
                query['isDeleted'] = {'$ne': True}

            # ============================
            # APPLY FILTERS
            # ============================
            if filters:

                # Filter by status (active, inactive, expired)
                if filters.get('status') and filters['status'] != 'all':
                    query['status'] = filters['status']

                # Filter by type (percentage, fixed_amount, buy_x_get_y)
                if filters.get('type') and filters['type'] != 'all':
                    query['type'] = filters['type']

                # Filter by target_type (supports both schemas)
                if filters.get('target_type') and filters['target_type'] != 'all':
                    query['$or'] = [
                        {'discount_config.target_type': filters['target_type']},
                        {'target_type': filters['target_type']}
                    ]

                # Filter by creator
                if filters.get('created_by'):
                    query['created_by'] = filters['created_by']

                # Search by name
                if filters.get('search_query'):
                    query['name'] = {
                        '$regex': filters['search_query'],
                        '$options': 'i'
                    }

                # Filter by created_at range
                if filters.get('date_from') and filters.get('date_to'):
                    query['created_at'] = {
                        '$gte': filters['date_from'],
                        '$lte': filters['date_to']
                    }

            # ============================
            # Pagination + Sorting
            # ============================
            skip = (page - 1) * limit
            sort_direction = -1 if sort_order.lower() == 'desc' else 1

            promotions = list(
                self.collection.find(query)
                .sort(sort_by, sort_direction)
                .skip(skip)
                .limit(limit)
            )

            # Serialize promotions
            serialized = [self._serialize_promotion_data(p) for p in promotions]

            total_count = self.collection.count_documents(query)
            total_pages = (total_count + limit - 1) // limit

            return {
                'success': True,
                'promotions': serialized,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_count': total_count,
                    'has_next': page < total_pages,
                    'has_previous': page > 1
                }
            }

        except Exception as e:
            logger.error(f"Error getting promotions: {e}")
            return {
                'success': False,
                'message': f'Error retrieving promotions: {str(e)}'
            }

    
    def _serialize_promotion_data(self, promotion):
        """Convert MongoDB ObjectIds to strings for JSON serialization"""
        if promotion:
            # Convert ObjectId to string
            if '_id' in promotion:
                promotion['_id'] = str(promotion['_id'])
            
            # Convert datetime objects to ISO strings
            for field in ['start_date', 'end_date', 'created_at', 'updated_at']:
                if field in promotion and promotion[field]:
                    if hasattr(promotion[field], 'isoformat'):
                        promotion[field] = promotion[field].isoformat()
            
            # Handle nested ObjectIds
            if 'target_ids' in promotion and promotion['target_ids']:
                promotion['target_ids'] = [str(id) if hasattr(id, '__str__') else id for id in promotion['target_ids']]
        
        return promotion

    def _validate_promotion_data(self, promotion_data):
        """Validate promotion creation data"""
        try:
            errors = []
            
            # Required fields
            required_fields = ['name', 'type', 'discount_value', 'target_type', 'start_date', 'end_date']
            for field in required_fields:
                if not promotion_data.get(field):
                    errors.append(f'{field} is required')
            
            # Validate promotion type
            valid_types = ['percentage', 'fixed_amount', 'buy_x_get_y']
            if promotion_data.get('type') not in valid_types:
                errors.append(f'type must be one of: {", ".join(valid_types)}')
            
            # Validate discount value
            try:
                discount_value = float(promotion_data.get('discount_value', 0))
                if discount_value <= 0:
                    errors.append('discount_value must be greater than 0')
                elif promotion_data.get('type') == 'percentage' and discount_value > 100:
                    errors.append('percentage discount cannot exceed 100%')
            except (ValueError, TypeError):
                errors.append('discount_value must be a valid number')
            
            # Validate target type
            valid_target_types = ['products', 'categories', 'all']
            if promotion_data.get('target_type') not in valid_target_types:
                errors.append(f'target_type must be one of: {", ".join(valid_target_types)}')
            
            # Validate target IDs if specified
            if promotion_data.get('target_type') in ['products', 'categories']:
                target_ids = promotion_data.get('target_ids', [])
                if not target_ids:
                    errors.append('target_ids required when target_type is products or categories')
                else:
                    # Validate that targets exist
                    validation_result = self._validate_targets_exist(promotion_data['target_type'], target_ids)
                    if not validation_result['is_valid']:
                        errors.extend(validation_result['errors'])
            
            # Validate dates - FIX TIMEZONE ISSUE
            try:
                start_date = promotion_data.get('start_date')
                end_date = promotion_data.get('end_date')
                
                # Convert string dates to datetime objects and make them timezone-aware
                if isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    if start_date.tzinfo is None:
                        start_date = start_date.replace(tzinfo=timezone.utc)
                elif isinstance(start_date, datetime) and start_date.tzinfo is None:
                    start_date = start_date.replace(tzinfo=timezone.utc)
                    
                if isinstance(end_date, str):
                    end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    if end_date.tzinfo is None:
                        end_date = end_date.replace(tzinfo=timezone.utc)
                elif isinstance(end_date, datetime) and end_date.tzinfo is None:
                    end_date = end_date.replace(tzinfo=timezone.utc)
                
                if start_date and end_date:
                    if end_date <= start_date:
                        errors.append('end_date must be after start_date')
                    
                    # Compare with timezone-aware current time
                    now_utc = datetime.now(timezone.utc)
                    if start_date < now_utc - timedelta(days=1):
                        errors.append('start_date cannot be more than 1 day in the past')
                    
                    duration = (end_date - start_date).days
                    if duration > 365:
                        errors.append('promotion duration cannot exceed 365 days')
                        
            except (ValueError, AttributeError) as e:
                errors.append('Invalid date format provided')
            
            # Validate usage limit
            if promotion_data.get('usage_limit'):
                try:
                    usage_limit = int(promotion_data['usage_limit'])
                    if usage_limit <= 0:
                        errors.append('usage_limit must be greater than 0')
                except (ValueError, TypeError):
                    errors.append('usage_limit must be a valid integer')
            
            return {
                'is_valid': len(errors) == 0,
                'errors': errors,
                'message': 'Validation failed' if errors else 'Validation passed'
            }
            
        except Exception as e:
            logger.error(f"Error validating promotion data: {e}")
            return {
                'is_valid': False,
                'errors': ['Validation system error'],
                'message': f'Validation error: {str(e)}'
            }

    def _validate_promotion_update(self, update_data, existing_promotion):
        """Validate promotion update data"""
        try:
            errors = []
            
            # Cannot update certain fields if promotion is active
            if existing_promotion.get('status') == 'active':
                restricted_fields = ['type', 'discount_value', 'target_type', 'target_ids']
                for field in restricted_fields:
                    if field in update_data:
                        errors.append(f'Cannot modify {field} while promotion is active')
            
            # Validate dates if provided
            if 'start_date' in update_data or 'end_date' in update_data:
                start_date = update_data.get('start_date', existing_promotion['start_date'])
                end_date = update_data.get('end_date', existing_promotion['end_date'])
                
                if isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                if isinstance(end_date, str):
                    end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                
                if end_date <= start_date:
                    errors.append('end_date must be after start_date')
                
                # Cannot modify start date if promotion has already started
                if existing_promotion.get('is_active') and 'start_date' in update_data:
                    errors.append('Cannot modify start_date of active promotion')
            
            # Validate discount value if provided
            if 'discount_value' in update_data:
                try:
                    discount_value = float(update_data['discount_value'])
                    if discount_value <= 0:
                        errors.append('discount_value must be greater than 0')
                    elif existing_promotion.get('type') == 'percentage' and discount_value > 100:
                        errors.append('percentage discount cannot exceed 100%')
                except (ValueError, TypeError):
                    errors.append('discount_value must be a valid number')
            
            # Validate target changes
            if 'target_ids' in update_data and update_data.get('target_ids'):
                target_type = update_data.get('target_type', existing_promotion.get('target_type'))
                validation_result = self._validate_targets_exist(target_type, update_data['target_ids'])
                if not validation_result['is_valid']:
                    errors.extend(validation_result['errors'])
            
            return {
                'is_valid': len(errors) == 0,
                'errors': errors,
                'message': 'Update validation failed' if errors else 'Update validation passed'
            }
            
        except Exception as e:
            logger.error(f"Error validating promotion update: {e}")
            return {
                'is_valid': False,
                'errors': ['Update validation system error'],
                'message': f'Update validation error: {str(e)}'
            }

    def _validate_promotion_targets(self, promotion):
        """Validate that target products/categories still exist"""
        try:
            if promotion['target_type'] == 'all':
                return {'is_valid': True, 'errors': []}
            
            return self._validate_targets_exist(promotion['target_type'], promotion.get('target_ids', []))
            
        except Exception as e:
            logger.error(f"Error validating promotion targets: {e}")
            return {
                'is_valid': False,
                'errors': [f'Target validation error: {str(e)}']
            }

    def _validate_targets_exist(self, target_type, target_ids):
        """Validate that specified target IDs exist"""
        try:
            errors = []
            
            if target_type == 'products':
                for product_id in target_ids:
                    try:
                        product = self.product_service.get_product_by_id(product_id)
                        # Assuming product_service returns dict with 'success' key
                        if not product or not product.get('success'):
                            errors.append(f'Product {product_id} not found')
                    except Exception as e:
                        logger.error(f"Error validating product {product_id}: {e}")
                        errors.append(f'Product {product_id} validation failed')
            
            elif target_type == 'categories':
                for category_id in target_ids:
                    try:
                        # ✅ FIX: CategoryService returns category object directly, not a dict
                        category = self.category_service.get_category_by_id(category_id)
                        
                        # Check if category exists (returns None if not found)
                        if category is None:
                            errors.append(f'Category {category_id} not found')
                            
                    except Exception as e:
                        logger.error(f"Error validating category {category_id}: {e}")
                        errors.append(f'Category {category_id} validation failed: {str(e)}')
            
            return {
                'is_valid': len(errors) == 0,
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Error in _validate_targets_exist: {e}")
            return {
                'is_valid': False,
                'errors': ['Target validation system error']
            }
    
    def _calculate_promotion_discount(self, promotion, order_data):
        """Calculate discount amount based on promotion type"""
        try:
            if not self._is_order_eligible(promotion, order_data):
                return 0.0
            
            eligible_amount = self._get_eligible_order_amount(promotion, order_data)
            
            if promotion['type'] == 'percentage':
                return eligible_amount * (promotion['discount_value'] / 100)
            
            elif promotion['type'] == 'fixed_amount':
                return min(promotion['discount_value'], eligible_amount)
            
            elif promotion['type'] == 'buy_x_get_y':
                return self._calculate_bxgy_discount(promotion, order_data)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating promotion discount: {e}")
            return 0.0

    def _is_order_eligible(self, promotion, order_data):
        """Check if order qualifies for promotion"""
        try:
            # Check if promotion targets match order items
            if promotion['target_type'] == 'all':
                return len(order_data.get('items', [])) > 0
            
            elif promotion['target_type'] == 'products':
                order_product_ids = [item.get('product_id') for item in order_data.get('items', [])]
                return any(product_id in promotion['target_ids'] for product_id in order_product_ids)
            
            elif promotion['target_type'] == 'categories':
                order_category_ids = [item.get('category_id') for item in order_data.get('items', []) if item.get('category_id')]
                return any(category_id in promotion['target_ids'] for category_id in order_category_ids)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking order eligibility: {e}")
            return False

    def _get_eligible_order_amount(self, promotion, order_data):
        """Get portion of order eligible for discount"""
        try:
            eligible_amount = 0.0
            
            if promotion['target_type'] == 'all':
                return order_data.get('total_amount', 0)
            
            for item in order_data.get('items', []):
                item_eligible = False
                
                if promotion['target_type'] == 'products':
                    item_eligible = item.get('product_id') in promotion['target_ids']
                elif promotion['target_type'] == 'categories':
                    item_eligible = item.get('category_id') in promotion['target_ids']
                
                if item_eligible:
                    eligible_amount += item.get('price', 0) * item.get('quantity', 1)
            
            return eligible_amount
            
        except Exception as e:
            logger.error(f"Error calculating eligible order amount: {e}")
            return 0.0

    def _calculate_bxgy_discount(self, promotion, order_data):
        """Calculate Buy X Get Y discount"""
        try:
            # Basic BXGY implementation - can be enhanced based on specific requirements
            discount_config = promotion.get('discount_config', {})
            buy_quantity = discount_config.get('buy_quantity', 2)
            get_quantity = discount_config.get('get_quantity', 1)
            
            eligible_items = []
            for item in order_data.get('items', []):
                if promotion['target_type'] == 'all' or \
                (promotion['target_type'] == 'products' and item.get('product_id') in promotion['target_ids']) or \
                (promotion['target_type'] == 'categories' and item.get('category_id') in promotion['target_ids']):
                    eligible_items.extend([item] * item.get('quantity', 1))
            
            if len(eligible_items) < buy_quantity:
                return 0.0
            
            # Sort by price (lowest first for maximum customer benefit)
            eligible_items.sort(key=lambda x: x.get('price', 0))
            
            # Calculate how many free items customer gets
            sets_qualified = len(eligible_items) // (buy_quantity + get_quantity)
            free_items = sets_qualified * get_quantity
            
            # Calculate discount (sum of cheapest items that are free)
            discount = sum(item.get('price', 0) for item in eligible_items[:free_items])
            
            return discount
            
        except Exception as e:
            logger.error(f"Error calculating BXGY discount: {e}")
            return 0.0

    def _check_usage_limit(self, promotion):
        """Check if promotion usage limit reached"""
        try:
            usage_limit = promotion.get('usage_limit')
            if not usage_limit:
                return True  # No limit set
            
            current_usage = promotion.get('current_usage', 0)
            return current_usage < usage_limit
            
        except Exception as e:
            logger.error(f"Error checking usage limit: {e}")
            return False

    def _track_promotion_usage(self, promotion_id, usage_data):
        """Track when promotion is used on orders"""
        try:
            # Update promotion usage statistics
            self.collection.update_one(
                {'promotion_id': promotion_id},
                {
                    '$inc': {
                        'current_usage': 1,
                        'total_revenue_impact': usage_data['discount_amount']
                    },
                    '$push': {
                        'usage_history': {
                            'customer_id': usage_data.get('customer_id'),
                            'discount_amount': usage_data['discount_amount'],
                            'order_summary': usage_data.get('order_summary', {}),
                            'used_at': usage_data['used_at']
                        }
                    },
                    '$set': {
                        'last_used_at': usage_data['used_at'],
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Error tracking promotion usage: {e}")

    def expire_promotion(self, promotion_id, user_id=None):
        """Expire promotion and generate usage report"""
        try:
            promotion = self.collection.find_one({'promotion_id': promotion_id})
            if not promotion:
                return {'success': False, 'message': 'Promotion not found'}
            
            # Update promotion status - ONLY UPDATE STATUS
            self.collection.update_one(
                {'promotion_id': promotion_id},
                {
                    '$set': {
                        'status': 'expired',
                        'expired_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            # Generate final usage report
            usage_report = self._generate_usage_report(promotion_id)
            
            # Log expiration
            self.audit_service.log_action(
                action='promotion_expired',
                resource_type='promotion',
                resource_id=promotion_id,
                user_id=user_id,
                changes={
                    'status_change': {'from': promotion['status'], 'to': 'expired'},
                    'final_usage_report': usage_report
                },
                metadata={'expiration_type': 'manual' if user_id else 'automatic'}
            )
            
            # Send expiration notification with report
            updated_promotion = self.collection.find_one({'promotion_id': promotion_id})
            self._send_promotion_notification('expired', updated_promotion, {
                'usage_report': usage_report
            })
            
            return {
                'success': True,
                'message': f'Promotion {promotion_id} expired successfully',
                'usage_report': usage_report
            }
            
        except Exception as e:
            logger.error(f"Error expiring promotion {promotion_id}: {e}")
            return {'success': False, 'message': f'Error expiring promotion: {str(e)}'}

    def deactivate_promotion(self, promotion_id, user_id=None):
        """Manually deactivate active promotion"""
        try:
            promotion = self.collection.find_one({'promotion_id': promotion_id})
            if not promotion:
                return {'success': False, 'message': 'Promotion not found'}
            
            if promotion.get('status') != 'active':
                return {'success': False, 'message': 'Promotion is not active'}
            
            # Deactivate promotion - ONLY UPDATE STATUS
            self.collection.update_one(
                {'promotion_id': promotion_id},
                {
                    '$set': {
                        'status': 'inactive',
                        'deactivated_at': datetime.utcnow(),
                        'deactivated_by': user_id,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            # Log deactivation
            self.audit_service.log_action(
                action='promotion_deactivated',
                resource_type='promotion',
                resource_id=promotion_id,
                user_id=user_id,
                changes={
                    'status_change': {'from': 'active', 'to': 'inactive'},
                    'usage_at_deactivation': promotion.get('current_usage', 0)
                },
                metadata={'deactivation_reason': 'manual_deactivation'}
            )
            
            return {
                'success': True,
                'message': f'Promotion {promotion_id} deactivated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deactivating promotion {promotion_id}: {e}")
            return {'success': False, 'message': f'Error deactivating promotion: {str(e)}'}
        
    def _send_promotion_notification(self, action_type, promotion_data, additional_metadata=None):
        """Simple notification helper for promotion actions"""
        try:
            titles = {
                'created': "New Promotion Created",
                'updated': "Promotion Updated", 
                'activated': "Promotion Activated",
                'deactivated': "Promotion Deactivated",
                'expired': "Promotion Expired",
                'deleted': "Promotion Deleted",
                'restored': "Promotion Restored"
            }
            
            promotion_name = promotion_data.get('name', 'Unknown Promotion')
            promotion_id = promotion_data.get('promotion_id', 'Unknown')
            
            if action_type in titles:
                self.notification_service.create_notification(
                    title=titles[action_type],
                    message=f"Promotion '{promotion_name}' ({promotion_id}) has been {action_type.replace('_', ' ')}",
                    priority="high" if action_type in ['activated', 'expired'] else "medium",
                    notification_type="system",
                    metadata={
                        "promotion_id": str(promotion_id),
                        "promotion_name": promotion_name,
                        "action_type": f"promotion_{action_type}",
                        "discount_type": promotion_data.get('type', 'unknown'),
                        "discount_value": str(promotion_data.get('discount_value', 0)),
                        **(additional_metadata or {})
                    }
                )
        except Exception as e:
            logger.error(f"Failed to send promotion notification: {e}")

    def _requires_notification(self, changes):
        """Determine if changes warrant notifications"""
        significant_fields = ['name', 'discount_value', 'start_date', 'end_date', 'status']
        return any(field in changes for field in significant_fields)

    def _schedule_promotion_lifecycle(self, promotion):
        """Schedule automatic activation/expiration"""
        # Placeholder - would integrate with background task system
        logger.info(f"Promotion {promotion['promotion_id']} scheduled for lifecycle management")

    def get_promotion_statistics(self, start_date=None, end_date=None):
        """Get comprehensive promotion statistics"""
        try:
            match_query = {}
            if start_date and end_date:
                match_query['created_at'] = {'$gte': start_date, '$lte': end_date}
            
            pipeline = [
                {'$match': match_query},
                {'$group': {
                    '_id': '$status',
                    'count': {'$sum': 1},
                    'total_usage': {'$sum': '$current_usage'},
                    'total_revenue_impact': {'$sum': '$total_revenue_impact'}
                }}
            ]
            
            stats = list(self.collection.aggregate(pipeline))
            
            return {
                'success': True,
                'statistics': {
                    'by_status': stats,
                    'total_promotions': sum(stat['count'] for stat in stats),
                    'total_customers_served': sum(stat['total_usage'] for stat in stats),
                    'total_revenue_impact': sum(stat['total_revenue_impact'] for stat in stats)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting promotion statistics: {e}")
            return {'success': False, 'message': f'Error getting statistics: {str(e)}'}

    def _generate_usage_report(self, promotion_id):
        """Generate comprehensive usage report for promotion"""
        try:
            promotion = self.collection.find_one({'promotion_id': promotion_id})
            if not promotion:
                return {}
            
            usage_history = promotion.get('usage_history', [])
            
            return {
                'promotion_id': promotion_id,
                'promotion_name': promotion['name'],
                'total_customers': len(usage_history),
                'total_discount': sum(usage['discount_amount'] for usage in usage_history),
                'revenue_impact': promotion.get('total_revenue_impact', 0),
                'period': {
                    'start_date': promotion['start_date'].isoformat(),
                    'end_date': promotion['end_date'].isoformat(),
                    'duration_days': (promotion['end_date'] - promotion['start_date']).days
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating usage report for {promotion_id}: {e}")
            return {}