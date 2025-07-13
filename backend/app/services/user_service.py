from bson import ObjectId
from datetime import datetime
from ..database import db_manager
from ..models import User
import bcrypt

class UserService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.collection = self.db.users 
    
    # ================================================================
    # UTILITY METHODS
    # ================================================================
    
    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
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
            from notifications.services import notification_service
            
            user_role = user_data.get('role', '').lower()
            
            # Only send notifications for employees
            if user_role != 'employee':
                return
            
            user_name = user_data.get('full_name', user_data.get('username', 'Employee'))
            user_email = user_data.get('email', '')
            
            # Configure notification based on action type
            if action_type == 'created':
                title = "New Employee Added"
                message = f"A new employee '{user_name}' has been added to the system"
                priority = "medium"
                metadata = {
                    "user_id": str(user_id) if user_id else str(user_data.get('_id', '')),
                    "employee_name": user_name,
                    "employee_email": user_email,
                    "employee_role": user_role,
                    "action_type": "employee_created",
                    "source": "user_management"
                }
            
            elif action_type == 'updated':
                title = "Employee Updated"
                message = f"Employee '{user_name}' information has been updated"
                priority = "low"
                
                # Track what was changed
                changes = []
                if old_user_data:
                    if old_user_data.get('full_name') != user_data.get('full_name'):
                        changes.append(f"name: '{old_user_data.get('full_name')}' → '{user_data.get('full_name')}'")
                    if old_user_data.get('email') != user_data.get('email'):
                        changes.append(f"email: '{old_user_data.get('email')}' → '{user_data.get('email')}'")
                    if old_user_data.get('status') != user_data.get('status'):
                        changes.append(f"status: '{old_user_data.get('status')}' → '{user_data.get('status')}'")
                
                if changes:
                    message += f" - Changes: {', '.join(changes)}"
                
                metadata = {
                    "user_id": str(user_id),
                    "employee_name": user_name,
                    "employee_email": user_email,
                    "employee_role": user_role,
                    "action_type": "employee_updated",
                    "source": "user_management",
                    "changes": changes
                }
            
            elif action_type == 'deleted':
                title = "Employee Removed"
                message = f"Employee '{user_name}' has been removed from the system"
                priority = "high"
                metadata = {
                    "user_id": str(user_id) if user_id else str(user_data.get('_id', '')),
                    "employee_name": user_name,
                    "employee_email": user_email,
                    "employee_role": user_role,
                    "action_type": "employee_deleted",
                    "source": "user_management"
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
            print(f"Failed to create {action_type} notification for employee: {notification_error}")
            # TODO: Replace with proper logging
    
    # ================================================================
    # CRUD OPERATIONS
    # ================================================================
    
    def create_user(self, user_data):
        """Create a new user"""
        try:
            # Hash password
            if 'password' in user_data:
                user_data['password'] = self.hash_password(user_data['password'])
            
            # Add timestamps and default status
            user_data['date_created'] = datetime.utcnow()
            user_data['last_updated'] = datetime.utcnow()
            user_data['status'] = user_data.get('status', 'active')
            
            # Insert user
            result = self.collection.insert_one(user_data)
            user_id = result.inserted_id
            
            # Get created user
            created_user = self.collection.find_one({'_id': user_id})
            created_user = self.convert_object_id(created_user)
            
            # Send notification if employee
            self._send_employee_notification('created', created_user, user_id)
            
            return created_user
        
        except Exception as e:
            raise Exception(f"Error creating user: {str(e)}")
    
    def get_all_users(self):
        """Get all users"""
        try:
            users = list(self.collection.find())
            return [self.convert_object_id(user) for user in users]
        except Exception as e:
            raise Exception(f"Error getting users: {str(e)}")
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            if not ObjectId.is_valid(user_id):
                return None
            
            user = self.collection.find_one({'_id': ObjectId(user_id)})
            return self.convert_object_id(user) if user else None
        except Exception as e:
            raise Exception(f"Error getting user: {str(e)}")
    
    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            user = self.collection.find_one({'email': email})
            return self.convert_object_id(user) if user else None
        except Exception as e:
            raise Exception(f"Error getting user by email: {str(e)}")
    
    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            user = self.collection.find_one({'username': username})
            return self.convert_object_id(user) if user else None
        except Exception as e:
            raise Exception(f"Error getting user by username: {str(e)}")
    
    def update_user(self, user_id, user_data):
        """Update user"""
        try:
            if not ObjectId.is_valid(user_id):
                return None
            
            # Get current user data for notification comparison
            old_user = self.collection.find_one({'_id': ObjectId(user_id)})
            if not old_user:
                return None
            
            old_user = self.convert_object_id(old_user)
            
            # Hash password if provided
            if 'password' in user_data:
                user_data['password'] = self.hash_password(user_data['password'])
            
            # Update timestamp
            user_data['last_updated'] = datetime.utcnow()
            
            # Update user
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)}, 
                {'$set': user_data}
            )
            
            if result.modified_count > 0:
                # Get updated user
                updated_user = self.collection.find_one({'_id': ObjectId(user_id)})
                updated_user = self.convert_object_id(updated_user)
                
                # Send notification if employee (check both old and new role)
                if (old_user.get('role', '').lower() == 'employee' or 
                    updated_user.get('role', '').lower() == 'employee'):
                    self._send_employee_notification('updated', updated_user, user_id, old_user)
                
                return updated_user
            return None
        
        except Exception as e:
            raise Exception(f"Error updating user: {str(e)}")
    
    def delete_user(self, user_id):
        """Delete user"""
        try:
            if not ObjectId.is_valid(user_id):
                return False
            
            # Get user data before deletion for notification
            user_to_delete = self.collection.find_one({'_id': ObjectId(user_id)})
            if not user_to_delete:
                return False
            
            user_to_delete = self.convert_object_id(user_to_delete)
            
            # Delete user
            result = self.collection.delete_one({'_id': ObjectId(user_id)})
            
            if result.deleted_count > 0:
                # Send notification if employee
                self._send_employee_notification('deleted', user_to_delete, user_id)
                return True
            
            return False
        
        except Exception as e:
            raise Exception(f"Error deleting user: {str(e)}")