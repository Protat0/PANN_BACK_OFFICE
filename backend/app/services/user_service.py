from bson import ObjectId
from datetime import datetime
from ..database import db_manager
from ..models import User
import bcrypt
import logging
from .audit_service import AuditLogService
from notifications.services import  NotificationService
logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        """Initialize UserService with audit logging"""
        self.db = db_manager.get_database()
        self.collection = self.db.users
        self.audit_service = AuditLogService()
        self.notification_service = NotificationService()
    
    # ================================================================
    # UTILITY METHODS
    # ================================================================
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        if not password:
            raise ValueError("Password cannot be empty")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        if not password or not hashed:
            return False
        
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    # ================================================================
    # NOTIFICATION METHODS
    # ================================================================
    
    def _send_user_notification(self, action_type, user_name, user_id=None):
        """Simple notification helper for user actions"""
        try:
            titles = {
                'created': "New User Created",
                'updated': "User Updated", 
                'password_changed': "Password Updated",  # Add this line
                'soft_deleted': "User Deleted",
                'hard_deleted': "User Permanently Deleted",
                'restored': "User Restored"
            }
            
            if action_type in titles:
                self.notification_service.create_notification(
                    title=titles[action_type],
                    message=f"User '{user_name}' has been {action_type.replace('_', ' ')}",
                    priority="high" if action_type == 'hard_deleted' else "medium",
                    notification_type="system",
                    metadata={
                        "user_id": str(user_id) if user_id else "",
                        "user_name": user_name,
                        "action_type": f"user_{action_type}"
                    }
                )
        except Exception as e:
            logger.error(f"Failed to send user notification: {e}")

    
    # ================================================================
    # CRUD OPERATIONS
    # ================================================================
    def update_user_profile(self, user_id, user_data, current_user=None, role_context=None):
        """Update user with role-based restrictions"""
        try:
            if not user_id:
                return None
            
            # Get current user data
            old_user = self.collection.find_one({
                '_id': user_id,
                'isDeleted': {'$ne': True}
            })
            if not old_user:
                return None
            
            # Role-based field restrictions
            allowed_fields = {}
            
            if role_context == 'self_service':
                # Employee can only change password
                allowed_fields = {
                    'password': user_data.get('password'),
                    'last_updated': datetime.utcnow()
                }
            elif role_context == 'admin':
                # Admin can change everything
                allowed_fields = user_data.copy()
                allowed_fields['last_updated'] = datetime.utcnow()
            else:
                raise Exception("Invalid role context")
            
            # Remove None values and hash password if present
            update_data = {k: v for k, v in allowed_fields.items() if v is not None}
            if update_data.get('password'):
                update_data['password'] = self.hash_password(update_data['password'])
            
            # Update user
            result = self.collection.update_one(
                {'_id': user_id, 'isDeleted': {'$ne': True}}, 
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                updated_user = self.collection.find_one({'_id': user_id})
                
                # Send appropriate notification
                user_name = updated_user.get('full_name', updated_user.get('username', 'User'))
                action = 'password_changed' if role_context == 'self_service' else 'updated'
                self._send_user_notification(action, user_name, user_id)
                
                return updated_user
            
            return None
            
        except Exception as e:
            raise Exception(f"Error updating user profile: {str(e)}")

    def generate_user_id(self):
        """Generate sequential USER-#### format ID"""
        try:
            # Find the highest existing USER ID
            pipeline = [
                {"$match": {"_id": {"$regex": "^USER-"}}},
                {"$addFields": {
                    "id_number": {
                        "$toInt": {"$substr": ["$_id", 5, -1]}
                    }
                }},
                {"$sort": {"id_number": -1}},
                {"$limit": 1}
            ]
            
            result = list(self.collection.aggregate(pipeline))
            next_number = (result[0]["id_number"] + 1) if result else 1
            
            return f"USER-{next_number:04d}"
            
        except Exception as e:
            logger.error(f"Error generating user ID: {e}")
            # Fallback to timestamp-based ID if aggregation fails
            import time
            return f"USER-{int(time.time()) % 10000:04d}"

    def create_user(self, user_data, current_user=None):
        """Create a new user with sequential USER-#### ID"""
        try:
            if current_user:
                logger.info(f"Creating user with admin: {current_user['username']}")
            
            # Generate sequential ID
            user_id = self.generate_user_id()
            user_data['_id'] = user_id
            
            # Hash password
            if user_data.get('password'):
                user_data['password'] = self.hash_password(user_data['password'])
            
            # Add timestamps and default status
            now = datetime.utcnow()
            user_data.update({
                'date_created': now,
                'last_updated': now,
                'status': user_data.get('status', 'active'),
                'isDeleted': False 
            })
            
            # Insert user (no need for ObjectId conversion)
            result = self.collection.insert_one(user_data)
            
            # Send notification
            user_name = user_data.get('full_name', user_data.get('username', 'User'))
            self._send_user_notification('created', user_name, user_id)
            
            # Audit logging
            if current_user and self.audit_service:
                try:
                    self.audit_service.log_user_create(current_user, user_data)
                    logger.info(f"Audit log created for user creation: {user_id}")
                except Exception as audit_error:
                    logger.error(f"Audit logging failed: {audit_error}")
            
            return user_data  # Already a clean dict, no conversion needed
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise Exception(f"Error creating user: {str(e)}")
        
    def get_users(self, page=1, limit=50, status=None, include_deleted=False):
        """Get users with optional status filter"""
        try:
            query = {}
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
            if status:  # 'active', 'disabled', 'pending', etc.
                query['status'] = status
                
            skip = (page - 1) * limit
            users = list(self.collection.find(query).skip(skip).limit(limit))
            total = self.collection.count_documents(query)
            
            return {
                'users': users,
                'total': total,
                'page': page,
                'limit': limit,
                'has_more': skip + limit < total
            }
        except Exception as e:
            raise Exception(f"Error getting users: {str(e)}")
    
    def get_user_by_id(self, user_id, include_deleted=False):
        """Get user by USER-#### ID"""
        try:
            if not user_id:
                return None
            
            query = {'_id': user_id}  # No ObjectId conversion needed
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}

            return self.collection.find_one(query)  # No conversion needed
        except Exception as e:
            raise Exception(f"Error getting user: {str(e)}")
        
    def get_user_by_username(self, username, include_deleted=False):
        """Get user by username - needed for login"""
        try:
            if not username:
                return None
            
            query = {'username': username}
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
                
            return self.collection.find_one(query)
        except Exception as e:
            raise Exception(f"Error getting user by username: {str(e)}")

    def get_user_by_email(self, email, include_deleted=False):
        """Get user by email - needed for login"""
        try:
            if not email:
                return None
            
            query = {'email': email}
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}

            return self.collection.find_one(query)
        except Exception as e:
            raise Exception(f"Error getting user by email: {str(e)}")

    def soft_delete_user(self, user_id, current_user=None):
        """Soft delete user - streamlined"""
        try:
            logger.info(f"Soft deleting user {user_id}")
            if current_user:
                logger.info(f"Deleted by: {current_user['username']}")
            
            if not user_id:
                return False
            
            # Get user data before deletion (only active users)
            user_to_delete = self.collection.find_one({
                '_id': user_id,  # No ObjectId needed
                'isDeleted': {'$ne': True}
            })
            
            if not user_to_delete:
                return False
            
            # Soft delete
            update_data = {
                'isDeleted': True,
                'deletedAt': datetime.utcnow(),
                'deletedBy': current_user.get('username') if current_user else 'system',
                'last_updated': datetime.utcnow()
            }
            
            result = self.collection.update_one(
                {'_id': user_id},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                # Send notification
                user_name = user_to_delete.get('full_name', user_to_delete.get('username', 'User'))
                self._send_user_notification('soft_deleted', user_name, user_id)
                
                # Audit logging
                if current_user and self.audit_service:
                    try:
                        self.audit_service.log_user_delete(current_user, user_to_delete, deletion_type="soft_delete")
                        logger.info("Audit log created for user soft deletion")
                    except Exception as audit_error:
                        logger.error(f"Audit logging failed: {audit_error}")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error soft deleting user {user_id}: {str(e)}")
            raise Exception(f"Error soft deleting user: {str(e)}")
        
    def restore_user(self, user_id, current_user=None):
        """Restore soft-deleted user (compliance feature)"""
        try:
            if not user_id:
                return False
            
            # Find deleted user
            deleted_user = self.collection.find_one({
                '_id': user_id,
                'isDeleted': True
            })
            
            if not deleted_user:
                return False
            
            # Restore with minimal data
            result = self.collection.update_one(
                {'_id': user_id},
                {
                    '$set': {
                        'isDeleted': False,
                        'restoredAt': datetime.utcnow(),
                        'restoredBy': current_user.get('username') if current_user else 'system',
                        'last_updated': datetime.utcnow(),
                        'status': 'active'
                    },
                    '$unset': {
                        'deletedAt': "",
                        'deletedBy': ""
                    }
                }
            )
            
            if result.modified_count > 0:
                user_name = deleted_user.get('full_name', deleted_user.get('username', 'User'))
                self._send_user_notification('restored', user_name, user_id)
                
                # Audit for compliance
                if current_user and self.audit_service:
                    self.audit_service.log_user_restore(current_user, deleted_user)
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error restoring user {user_id}: {str(e)}")
            raise Exception(f"Error restoring user: {str(e)}")
    
    def hard_delete_user(self, user_id, current_user=None, confirmation_token=None):
        """PERMANENT deletion - compliance only (requires confirmation)"""
        try:
            # Extra safety check
            if not confirmation_token or confirmation_token != "PERMANENT_DELETE_CONFIRMED":
                raise Exception("Hard delete requires explicit confirmation token")
            
            logger.warning(f"PERMANENT DELETION initiated for {user_id}")
            
            if not user_id:
                return False
            
            # Get user before permanent deletion
            user_to_delete = self.collection.find_one({'_id': user_id})
            if not user_to_delete:
                return False
            
            # PERMANENTLY DELETE
            result = self.collection.delete_one({'_id': user_id})
            
            if result.deleted_count > 0:
                user_name = user_to_delete.get('full_name', user_to_delete.get('username', 'User'))
                
                # Critical notification
                self._send_user_notification('hard_deleted', user_name, user_id)
                
                # Compliance audit
                if current_user and self.audit_service:
                    self.audit_service.log_user_hard_delete(current_user, user_to_delete)
                
                logger.warning(f"User {user_id} PERMANENTLY DELETED")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error permanently deleting user {user_id}: {str(e)}")
            raise Exception(f"Error permanently deleting user: {str(e)}")

    def get_disabled_users(self, page=1, limit=50):
        """Get users with disabled status"""
        try:
            query = {
                'status': 'disabled',
                'isDeleted': {'$ne': True}  # Not actually deleted, just disabled
            }
            
            skip = (page - 1) * limit
            users = list(self.collection.find(query).skip(skip).limit(limit))
            total = self.collection.count_documents(query)
            
            return {
                'users': users,
                'total': total,
                'page': page,
                'limit': limit,
                'has_more': skip + limit < total
            }
        except Exception as e:
            raise Exception(f"Error getting disabled users: {str(e)}")
        