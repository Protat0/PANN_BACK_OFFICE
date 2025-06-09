from bson import ObjectId
from datetime import datetime
from ..database import db_manager  # ✅ Updated import
from ..models import Customer
import bcrypt

class CustomerService:
    def __init__(self):
        self.db = db_manager.get_database()  # ✅ Get database connection
        self.customer_collection = self.db.customers  # ✅ Use cloud database
        self.user_collection = self.db.users  # ✅ Use cloud database
    
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
    
    def create_customer(self, customer_data):
        """Create a new customer in both users and customers collections"""
        try:
            # Extract user-related data
            user_data = {
                "username": customer_data.get("username", customer_data.get("email")),
                "email": customer_data["email"],
                "password": self.hash_password(customer_data.get("password", "defaultpassword")),
                "full_name": customer_data.get("full_name", ""),
                "role": "customer",
                "status": "active",
                "date_created": datetime.utcnow(),
                "last_updated": datetime.utcnow(),
                "source": "customer_registration"
            }
            
            # Insert into users collection first
            user_result = self.user_collection.insert_one(user_data)
            user_id = user_result.inserted_id
            
            # Prepare customer-specific data
            customer_specific_data = {
                "_id": user_id,  # Same ID as user
                "customer_id": str(user_id),
                "full_name": customer_data.get("full_name", ""),
                "email": customer_data["email"],
                "phone": customer_data.get("phone", ""),
                "delivery_address": customer_data.get("delivery_address", {}),
                "loyalty_points": customer_data.get("loyalty_points", 0),
                "last_purchase": customer_data.get("last_purchase"),
                "date_created": datetime.utcnow(),
                "last_updated": datetime.utcnow(),
                "status": "active",
                "source": "customer_registration"
            }
            
            # Insert into customers collection
            self.customer_collection.insert_one(customer_specific_data)
            
            # Return the customer data
            created_customer = self.customer_collection.find_one({'_id': user_id})
            return self.convert_object_id(created_customer)
        
        except Exception as e:
            # Rollback user creation if customer creation fails
            if 'user_id' in locals():
                self.user_collection.delete_one({'_id': user_id})
            raise Exception(f"Error creating customer: {str(e)}")
    
    def get_all_customers(self):
        """Get all customers"""
        try:
            customers = list(self.customer_collection.find())
            return [self.convert_object_id(customer) for customer in customers]
        except Exception as e:
            raise Exception(f"Error getting customers: {str(e)}")
    
    def get_customer_by_id(self, customer_id):
        """Get customer by ID (searches both collections)"""
        try:
            if not ObjectId.is_valid(customer_id):
                return None
            
            # First try customers collection
            customer = self.customer_collection.find_one({'_id': ObjectId(customer_id)})
            if customer:
                return self.convert_object_id(customer)
            
            # Then try users collection (in case it's a user ID)
            user = self.user_collection.find_one({'_id': ObjectId(customer_id)})
            if user and user.get('role') == 'customer':
                # Find corresponding customer record by email
                customer = self.customer_collection.find_one({'email': user['email']})
                if customer:
                    return self.convert_object_id(customer)
                else:
                    # Create customer record from user data
                    customer_data = {
                        "_id": user["_id"],
                        "customer_id": str(user["_id"]),
                        "full_name": user.get("full_name", ""),
                        "email": user["email"],
                        "phone": "",
                        "delivery_address": {},
                        "loyalty_points": 0,
                        "last_purchase": None,
                        "date_created": user.get("date_created", datetime.utcnow()),
                        "last_updated": datetime.utcnow(),
                        "status": user.get("status", "active"),
                        "source": "users_collection"
                    }
                    self.customer_collection.insert_one(customer_data)
                    return self.convert_object_id(customer_data)
            
            return None
        except Exception as e:
            raise Exception(f"Error getting customer: {str(e)}")
    
    def update_customer(self, customer_id, customer_data):
        """Update customer in both collections"""
        try:
            if not ObjectId.is_valid(customer_id):
                return None
            
            # Update timestamp
            customer_data['last_updated'] = datetime.utcnow()
            
            # Extract fields that should be updated in users collection
            user_update_data = {}
            for field in ["email", "full_name", "password"]:
                if field in customer_data:
                    user_update_data[field] = customer_data[field]
            
            # Hash password if updating
            if "password" in user_update_data:
                user_update_data["password"] = self.hash_password(user_update_data["password"])
            
            # Update users collection if any user fields are present
            if user_update_data:
                user_update_data["last_updated"] = datetime.utcnow()
                self.user_collection.update_one(
                    {'_id': ObjectId(customer_id)}, 
                    {'$set': user_update_data}
                )
            
            # Update customers collection
            customer_result = self.customer_collection.update_one(
                {'_id': ObjectId(customer_id)}, 
                {'$set': customer_data}
            )
            
            if customer_result.modified_count > 0 or user_update_data:
                updated_customer = self.customer_collection.find_one({'_id': ObjectId(customer_id)})
                return self.convert_object_id(updated_customer)
            return None
        
        except Exception as e:
            raise Exception(f"Error updating customer: {str(e)}")
    
    def delete_customer(self, customer_id):
        """Delete customer from both collections"""
        try:
            if not ObjectId.is_valid(customer_id):
                return False
            
            # Delete from both collections
            customer_result = self.customer_collection.delete_one({'_id': ObjectId(customer_id)})
            user_result = self.user_collection.delete_one({'_id': ObjectId(customer_id)})
            
            return customer_result.deleted_count > 0 or user_result.deleted_count > 0
        
        except Exception as e:
            raise Exception(f"Error deleting customer: {str(e)}")