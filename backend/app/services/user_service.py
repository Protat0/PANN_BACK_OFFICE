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
    
    def _send_employee_notification(self, action_type, user_data, user_id=None, old_user_data=None):
        """
        Send notification for employee-related actions
        
        Args:
            action_type (str): 'created', 'updated', or 'deleted'
            user_data (dict): Current user data
            user_id (str): User ID (for updates/deletes)
            old_user_data (dict): Previous user data (for updates)
        """
        try: 
            user_role = user_data.get('role', '').lower()
            
            # Only send notifications for employees
            if user_role != 'employee':
                return
            
            user_name = user_data.get('full_name', user_data.get('username', 'Employee'))
            # Notification configurations
            configs = {
                'created': {
                    'title': "New Employee Added",
                    'message': f"A new employee '{user_name}' has been added to the system",
                    'priority': "medium"
                },
                'updated': {
                    'title': "Employee Updated", 
                    'message': f"Employee '{user_name}' information has been updated",
                    'priority': "low"
                },
                'deleted': {
                    'title': "Employee Removed",
                    'message': f"Employee '{user_name}' has been removed from the system",
                    'priority': "high"
                },
                'restored': {
                    'title': "Employee Restored",
                    'message': f"Employee '{user_name}' has been restored to the system",
                    'priority': "medium"
                }
            }

            if action_type not in configs:
                return
            config = configs[action_type]

            if action_type == 'updated' and old_user_data: # Add change details for updates
                changes = []
                for field in ['full_name', 'email', 'status']:
                    old_val = old_user_data.get(field)
                    new_val = user_data.get(field)
                    if old_val != new_val:
                        changes.append(f"{field}: '{old_val}' → '{new_val}'")
                
                if changes:
                    config['message'] += f" - Changes: {', '.join(changes)}"

            # Create metadata
            metadata = {
                "user_id": str(user_id or user_data.get('_id', '')),
                "employee_name": user_name,
                "employee_email": user_data.get('email', ''),
                "employee_role": user_data.get('role', ''),
                "action_type": f"employee_{action_type}",
                "source": "user_management"
            }

            if action_type == 'updated' and 'changes' in locals():
                metadata["changes"] = changes
        
            # Send notification
            self.notification_service.create_notification(
                title=config['title'],
                message=config['message'],
                priority=config['priority'],
                notification_type="system",
                metadata=metadata
            )

        except Exception as e:
            print(f"Failed to create {action_type} notification for employee: {e}")

    

    # ================================================================
    # CRUD OPERATIONS
    # ================================================================
    
    def create_user(self, user_data, current_user=None):
        """Create a new user with audit logging"""
        try:
            # ✅ ADD: Log who is creating the user
            if current_user:
                print(f"🔍 Creating user with admin: {current_user['username']}")
            
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
            
            # Insert user
            result = self.collection.insert_one(user_data)
            user_id = result.inserted_id
            
            # Get created user
            created_user = self.collection.find_one({'_id': user_id})
            created_user = self.convert_object_id(created_user)
            
            # Send notification if employee
            self._send_employee_notification('created', created_user, user_id)
            
            if current_user and self.audit_service:
                try:
                    self.audit_service.log_user_create(current_user, created_user)
                    print(f"✅ Audit log created for user creation")
                except Exception as audit_error:
                    print(f"❌ Audit logging failed: {audit_error}")
        
            return created_user

        except Exception as e:
            raise Exception(f"Error creating user: {str(e)}")
        
    def get_all_users(self, include_deleted=False):
        """Get all users"""
        try:
            query = {}
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
            users = list(self.collection.find(query))
            return [self.convert_object_id(user) for user in users]
        except Exception as e:
            raise Exception(f"Error getting users: {str(e)}")
    
    def get_user_by_id(self, user_id, include_deleted=False):
        """Get user by ID"""
        try:
            if not user_id or not ObjectId.is_valid(user_id):
                return None
            
            query = {'_id': ObjectId(user_id)}
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}

            user = self.collection.find_one(query)
            return self.convert_object_id(user) if user else None
        except Exception as e:
            raise Exception(f"Error getting user: {str(e)}")
        
    def get_user_by_email(self, email, include_deleted=False):
        """Get user by email"""
        try:
            if not email:
                return None
            
            query = {'email': email}
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}

            user = self.collection.find_one(query)
            return self.convert_object_id(user) if user else None
        except Exception as e:
            raise Exception(f"Error getting user by email: {str(e)}")

    def get_user_by_username(self, username, include_deleted=False):
        """Get user by username"""
        try:
            if not username:
                return None
            query = {'username': username}
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
                
            user = self.collection.find_one(query)
            return self.convert_object_id(user) if user else None
        except Exception as e:
            raise Exception(f"Error getting user by username: {str(e)}")

    def update_user(self, user_id, user_data, current_user=None):
        """Update user with audit logging"""
        try:
            # ✅ ADD: Log who is updating the user
            if current_user:
                print(f"🔍 Updating user {user_id} with admin: {current_user['username']}")
            
            if not user_id or not ObjectId.is_valid(user_id):
                return None
            
            # Get current user data for notification comparison and audit
            old_user = self.collection.find_one({
                '_id': ObjectId(user_id),
                'isDeleted': {'$ne': True}  
            })
            if not old_user:
                return None
            
            old_user = self.convert_object_id(old_user)
            
            update_data = user_data.copy()
            if update_data.get('password'):
                update_data['password'] = self.hash_password(update_data['password'])
            update_data['last_updated'] = datetime.utcnow()

            result = self.collection.update_one(
                {
                    '_id': ObjectId(user_id),
                    'isDeleted': {'$ne': True}  # ✅ CHANGE: Only update active users
                }, 
                {'$set': update_data}
            )
            
            if result.modified_count == 0:
                return None

            updated_user = self.collection.find_one({'_id': ObjectId(user_id)})
            updated_user = self.convert_object_id(updated_user)
            
            # Send notification if employee (either old or new role)
          ##  self._notify_role_based_action('updated', updated_user, user_id, current_user) OLD
            self._send_employee_notification('updated', updated_user, user_id, old_user)
            
            # Audit logging
            if current_user and self.audit_service:
                try:
                    self.audit_service.log_user_update(current_user, user_id, old_user, update_data)
                    print(f"✅ Audit log created for user update")
                except Exception as audit_error:
                    print(f"❌ Audit logging failed: {audit_error}")
            
            return updated_user

        except Exception as e:
            raise Exception(f"Error updating user: {str(e)}")
    
    def soft_delete_user(self, user_id, current_user=None, deletion_context=None):
        """Soft delete user and related data"""
        try:
            logger.info(f"Soft deleting user {user_id}")
            if current_user:
                logger.info(f"Deleted by: {current_user['username']}")
            
            if not user_id or not ObjectId.is_valid(user_id):
                return False
            
            object_id = ObjectId(user_id)
            
            # Get user data before deletion (only active users)
            user_to_delete = self.collection.find_one({
                '_id': object_id,
                'isDeleted': {'$ne': True}
            })
            
            if not user_to_delete:
                return False
            
            user_role = user_to_delete.get('role', '').lower()
            now = datetime.utcnow()
            
            # Soft delete data
            update_data = {
                'isDeleted': True,
                'deletedAt': now,
                'deletedBy': current_user.get('username') if current_user else 'system',
                'last_updated': now,
                'deletionContext': deletion_context or f"{user_role}_deletion"
            }
            
            # Update users collection
            user_result = self.collection.update_one(
                {'_id': object_id},
                {'$set': update_data}
            )
            
            # Update role-specific collection based on user role
            role_result = None
            if user_role == 'customer':
                role_result = self.db.customers.update_one(
                    {'_id': object_id},
                    {'$set': update_data}
                )
            elif user_role == 'employee':
                # For employees, you might have an employees collection
                # role_result = self.db.employees.update_one(
                #     {'_id': object_id},
                #     {'$set': update_data}
                # )
                pass
            
            if user_result.modified_count > 0:
                user_to_delete = self.convert_object_id(user_to_delete)
                
                # Send role-based notification
                ##self._notify_role_based_action('deleted', user_to_delete, user_id, current_user) OLD
                self._send_employee_notification('deleted', user_to_delete, user_id)
                
                # Audit logging
                if current_user and self.audit_service:
                    try:
                        self.audit_service.log_user_delete(
                            current_user, 
                            user_to_delete,
                            deletion_type="soft_delete"
                        )
                        logger.info("Audit log created for user soft deletion")
                    except Exception as audit_error:
                        logger.error(f"Audit logging failed: {audit_error}")
                
                logger.info(f"User ({user_role}) soft deleted successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error soft deleting user {user_id}: {str(e)}")
            raise Exception(f"Error soft deleting user: {str(e)}")
    
    def restore_user(self, user_id, current_user=None):
        """Restore a soft-deleted user"""
        try:
            logger.info(f"Restoring user {user_id}")
            if current_user:
                logger.info(f"Restored by: {current_user['username']}")
            
            if not user_id or not ObjectId.is_valid(user_id):
                return False
            
            object_id = ObjectId(user_id)
            
            # Find deleted user
            deleted_user = self.collection.find_one({
                '_id': object_id,
                'isDeleted': True
            })
            
            if not deleted_user:
                return False
            
            user_role = deleted_user.get('role', '').lower()
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
                'deletedAt': "",
                'deletedBy': "",
                'deletionContext': ""
            }
            
            # Restore in users collection
            user_result = self.collection.update_one(
                {'_id': object_id},
                {'$set': restore_data, '$unset': unset_data}
            )
            
            # Restore in role-specific collection
            role_result = None
            if user_role == 'customer':
                role_result = self.db.customers.update_one(
                    {'_id': object_id},
                    {'$set': restore_data, '$unset': unset_data}
                )
            elif user_role == 'employee':
                # role_result = self.db.employees.update_one(...)
                pass
            
            if user_result.modified_count > 0:
                restored_user = self.collection.find_one({'_id': object_id})
                restored_user = self.convert_object_id(restored_user)
                
                # Send role-based notification
                ##self._notify_role_based_action('restored', restored_user, user_id, current_user) OLD
            
                self._send_employee_notification('restored', restored_user, user_id)
                # Audit logging
                if current_user and self.audit_service:
                    try:
                        self.audit_service.log_user_restore(current_user, restored_user)
                        logger.info("Audit log created for user restoration")
                    except Exception as audit_error:
                        logger.error(f"Audit logging failed: {audit_error}")
                
                logger.info(f"User ({user_role}) restored successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error restoring user {user_id}: {str(e)}")
            raise Exception(f"Error restoring user: {str(e)}")
    
    def hard_delete_user(self, user_id, current_user=None):
        """Permanently delete user (use with extreme caution)"""
        try:
            logger.warning(f"HARD DELETING user {user_id} - THIS IS PERMANENT!")
            if current_user:
                logger.info(f"Deleted by: {current_user['username']}")
            
            if not user_id or not ObjectId.is_valid(user_id):
                return False
            
            object_id = ObjectId(user_id)
            
            # Get user data before permanent deletion
            user_to_delete = self.collection.find_one({'_id': object_id})
            if not user_to_delete:
                return False
            
            user_role = user_to_delete.get('role', '').lower()
            user_name = user_to_delete.get('full_name', user_to_delete.get('username', 'User'))
            
            # Permanently delete from users collection
            user_result = self.collection.delete_one({'_id': object_id})
            
            # Delete from role-specific collection
            role_result = None
            if user_role == 'customer':
                role_result = self.db.customers.delete_one({'_id': object_id})
            elif user_role == 'employee':
                # role_result = self.db.employees.delete_one({'_id': object_id})
                pass
            
            if user_result.deleted_count > 0:
                # Send critical notification for permanent deletion
                try:
                    self.notification_service.create_notification(
                        title="⚠️ USER PERMANENTLY DELETED",
                        message=f"{user_role.title()} '{user_name}' has been PERMANENTLY deleted from the system",
                        priority="urgent",
                        notification_type="system",
                        metadata={
                            "user_id": str(user_id),
                            "user_name": user_name,
                            "user_role": user_role,
                            "action_type": f"{user_role}_hard_deleted",
                            "warning": "PERMANENT_DELETION"
                        }
                    )
                except Exception as e:
                    logger.error(f"Failed to send hard deletion notification: {e}")
                
                # Audit logging
                if current_user and self.audit_service:
                    try:
                        self.audit_service.log_user_hard_delete(
                            current_user,
                            self.convert_object_id(user_to_delete)
                        )
                        logger.info("Audit log created for PERMANENT user deletion")
                    except Exception as audit_error:
                        logger.error(f"Audit logging failed: {audit_error}")
                
                logger.warning(f"User ({user_role}) PERMANENTLY deleted")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error permanently deleting user {user_id}: {str(e)}")
            raise Exception(f"Error permanently deleting user: {str(e)}")

    def get_deleted_users(self):
        """Get all soft-deleted users"""
        try:
            users = list(self.collection.find({'isDeleted': True}))
            return [self.convert_object_id(user) for user in users]
        except Exception as e:
            logger.error(f"Error getting deleted users: {str(e)}")
            raise Exception(f"Error getting deleted users: {str(e)}")
    