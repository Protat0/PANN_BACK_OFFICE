from bson import ObjectId
from datetime import datetime
from ..database import get_collection
from ..models import User
import bcrypt

class UserService:
    def __init__(self):
        self.collection = get_collection('users')
    
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
    
    def create_user(self, user_data):
        """Create a new user"""
        try:
            # Hash password
            if 'password' in user_data:
                user_data['password'] = self.hash_password(user_data['password'])
            
            # Add timestamps and default status
            user_data['date_created'] = datetime.utcnow()
            user_data['last_updated'] = datetime.utcnow()
            user_data['status'] = user_data.get('status', 'active')  # Add this line
            
            # Insert user
            result = self.collection.insert_one(user_data)
            
            # Get created user
            created_user = self.collection.find_one({'_id': result.inserted_id})
            return self.convert_object_id(created_user)
        
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
                updated_user = self.collection.find_one({'_id': ObjectId(user_id)})
                return self.convert_object_id(updated_user)
            return None
        
        except Exception as e:
            raise Exception(f"Error updating user: {str(e)}")
    
    def delete_user(self, user_id):
        """Delete user"""
        try:
            if not ObjectId.is_valid(user_id):
                return False
            
            result = self.collection.delete_one({'_id': ObjectId(user_id)})
            return result.deleted_count > 0
        
        except Exception as e:
            raise Exception(f"Error deleting user: {str(e)}")