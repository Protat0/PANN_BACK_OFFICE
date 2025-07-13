from bson import ObjectId
from datetime import datetime
from ..database import db_manager
from ..models import Customer
import bcrypt
from notifications.services import notification_service

class CustomerService:
    def __init__(self):
        self.db = db_manager.get_database()  
        self.customer_collection = self.db.customers  
        self.user_collection = self.db.users 
        self.session_logs = self.db.session_logs
    
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
    
    # ================================================================
    # NOTIFICATION METHODS
    # ================================================================
    
    def _send_customer_notification(self, action_type, customer_data, customer_id=None, old_customer_data=None):
        """
        Send notification for customer-related actions
        
        Args:
            action_type (str): 'created', 'updated', or 'deleted'
            customer_data (dict): Current customer data
            customer_id (str): Customer ID (for updates/deletes)
            old_customer_data (dict): Previous customer data (for updates)
        """
        try:
            customer_name = customer_data.get('full_name', customer_data.get('email', 'Unknown Customer'))
            customer_email = customer_data.get('email', 'No email')
            
            # Configure notification based on action type
            if action_type == 'created':
                title = "New Customer Registration"
                message = f"A new customer '{customer_name}' has registered in the system"
                priority = "low"
                metadata = {
                    "customer_id": str(customer_id) if customer_id else str(customer_data.get('_id', '')),
                    "customer_name": customer_name,
                    "customer_email": customer_email,
                    "phone": customer_data.get('phone', ''),
                    "loyalty_points": customer_data.get('loyalty_points', 0),
                    "action_type": "customer_created",
                    "registration_source": "customer_registration"
                }
            
            elif action_type == 'updated':
                title = "Customer Updated"
                message = f"Customer '{customer_name}' information has been updated"
                priority = "low"
                
                # Track what was changed
                changes = []
                if old_customer_data:
                    if old_customer_data.get('full_name') != customer_data.get('full_name'):
                        changes.append(f"name: '{old_customer_data.get('full_name')}' → '{customer_data.get('full_name')}'")
                    if old_customer_data.get('email') != customer_data.get('email'):
                        changes.append(f"email: '{old_customer_data.get('email')}' → '{customer_data.get('email')}'")
                    if old_customer_data.get('phone') != customer_data.get('phone'):
                        changes.append(f"phone: '{old_customer_data.get('phone')}' → '{customer_data.get('phone')}'")
                    if old_customer_data.get('status') != customer_data.get('status'):
                        changes.append(f"status: '{old_customer_data.get('status')}' → '{customer_data.get('status')}'")
                    if old_customer_data.get('loyalty_points') != customer_data.get('loyalty_points'):
                        old_points = old_customer_data.get('loyalty_points', 0)
                        new_points = customer_data.get('loyalty_points', 0)
                        changes.append(f"loyalty points: {old_points} → {new_points}")
                
                if changes:
                    message += f" - Changes: {', '.join(changes)}"
                
                metadata = {
                    "customer_id": str(customer_id),
                    "customer_name": customer_name,
                    "customer_email": customer_email,
                    "phone": customer_data.get('phone', ''),
                    "loyalty_points": customer_data.get('loyalty_points', 0),
                    "action_type": "customer_updated",
                    "changes": changes
                }
            
            elif action_type == 'deleted':
                title = "Customer Deleted"
                message = f"Customer '{customer_name}' has been removed from the system"
                priority = "medium"
                metadata = {
                    "customer_id": str(customer_id) if customer_id else str(customer_data.get('_id', '')),
                    "customer_name": customer_name,
                    "customer_email": customer_email,
                    "phone": customer_data.get('phone', ''),
                    "loyalty_points": customer_data.get('loyalty_points', 0),
                    "action_type": "customer_deleted"
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
            print(f"Failed to create {action_type} notification for customer: {notification_error}")
            # TODO: Replace with proper logging
    
    # ================================================================
    # CRUD OPERATIONS
    # ================================================================
    
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
            
            # Get created customer and convert ObjectId
            created_customer = self.customer_collection.find_one({'_id': user_id})
            created_customer = self.convert_object_id(created_customer)
            
            # Send notification
            self._send_customer_notification('created', created_customer, user_id)
            
            return created_customer
        
        except Exception as e:
            # Rollback user creation if customer creation fails
            if 'user_id' in locals():
                self.user_collection.delete_one({'_id': user_id})
            raise Exception(f"Error creating customer: {str(e)}")
    
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
    
    def get_all_customers(self):
        """Get all customers"""
        try:
            customers = list(self.customer_collection.find())
            return [self.convert_object_id(customer) for customer in customers]
        except Exception as e:
            raise Exception(f"Error getting customers: {str(e)}")
    
    def update_customer(self, customer_id, customer_data):
        """Update customer in both collections"""
        try:
            if not ObjectId.is_valid(customer_id):
                return None
            
            # Get current customer data for notification comparison
            old_customer = self.customer_collection.find_one({'_id': ObjectId(customer_id)})
            if not old_customer:
                return None
            
            old_customer = self.convert_object_id(old_customer)
            
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
                # Get updated customer
                updated_customer = self.customer_collection.find_one({'_id': ObjectId(customer_id)})
                updated_customer = self.convert_object_id(updated_customer)
                
                # Send notification
                self._send_customer_notification('updated', updated_customer, customer_id, old_customer)
                
                return updated_customer
            return None
        
        except Exception as e:
            raise Exception(f"Error updating customer: {str(e)}")
    
    def delete_customer(self, customer_id):
        """Delete customer from both collections"""
        try:
            if not ObjectId.is_valid(customer_id):
                return False
            
            # Get customer data before deletion for notification
            customer_to_delete = self.customer_collection.find_one({'_id': ObjectId(customer_id)})
            if not customer_to_delete:
                return False
            
            customer_to_delete = self.convert_object_id(customer_to_delete)
            
            # Delete from both collections
            customer_result = self.customer_collection.delete_one({'_id': ObjectId(customer_id)})
            user_result = self.user_collection.delete_one({'_id': ObjectId(customer_id)})
            
            if customer_result.deleted_count > 0 or user_result.deleted_count > 0:
                # Send notification
                self._send_customer_notification('deleted', customer_to_delete, customer_id)
                return True
            
            return False
        
        except Exception as e:
            raise Exception(f"Error deleting customer: {str(e)}")
    
    # ================================================================
    # ANALYTICS AND METRICS
    # ================================================================
    
    def get_active_customers(self):
        """Get count of active customers"""
        try:
            customers = self.customer_collection.count_documents({"status": "active"})
            return customers
        except Exception as e:
            print(f"Database error: {str(e)}")
            raise Exception(f"Error Getting the Count: {str(e)}")

    def get_monthly_users(self):
        """Get count of customers created this month"""
        try:
            today = datetime.now()
            
            # Get the first day of the current month
            start_of_month = datetime(today.year, today.month, 1)
            
            # Get the first day of the next month
            if today.month == 12:
                start_of_next_month = datetime(today.year + 1, 1, 1)
            else:
                start_of_next_month = datetime(today.year, today.month + 1, 1)
            
            print(f"Searching for customers created between {start_of_month} and {start_of_next_month}")
            
            # Query for documents created within this month
            customers = self.customer_collection.count_documents({
                "date_created": {
                    "$gte": start_of_month,
                    "$lt": start_of_next_month
                }
            })
            
            print(f"Found {customers} customers created this month")
            return customers
        
        except Exception as e:
            print(f"Database error: {str(e)}")
            raise Exception(f"Error Getting the Count: {str(e)}")
        
    def get_daily_logins(self):
        """Get count of customer logins today"""
        try:
            today = datetime.now()
            start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = today.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Get unique user_ids from session_logs for today
            daily_login_user_ids = self.session_logs.distinct(
                "user_id", 
                {
                    "login_time": {
                        "$gte": start_of_day,
                        "$lte": end_of_day
                    }
                }
            )
            
            # Count how many of these user_ids exist in customer_collection
            daily_logins_count = self.customer_collection.count_documents({
                "_id": {"$in": daily_login_user_ids}
            })
            
            return daily_logins_count
            
        except Exception as e:
            print(f"Error getting daily logins: {e}")
            return 0
    
    def get_customer_statistics(self):
        """Get comprehensive customer statistics"""
        try:
            stats = {
                'total_customers': self.customer_collection.count_documents({}),
                'active_customers': self.get_active_customers(),
                'monthly_registrations': self.get_monthly_users(),
                'daily_logins': self.get_daily_logins()
            }
            
            # Calculate additional metrics
            stats['inactive_customers'] = stats['total_customers'] - stats['active_customers']
            
            # Get loyalty points statistics
            loyalty_pipeline = [
                {"$group": {
                    "_id": None,
                    "total_loyalty_points": {"$sum": "$loyalty_points"},
                    "avg_loyalty_points": {"$avg": "$loyalty_points"},
                    "max_loyalty_points": {"$max": "$loyalty_points"}
                }}
            ]
            
            loyalty_stats = list(self.customer_collection.aggregate(loyalty_pipeline))
            if loyalty_stats:
                stats.update({
                    'total_loyalty_points': loyalty_stats[0].get('total_loyalty_points', 0),
                    'avg_loyalty_points': round(loyalty_stats[0].get('avg_loyalty_points', 0), 2),
                    'max_loyalty_points': loyalty_stats[0].get('max_loyalty_points', 0)
                })
            
            return stats
            
        except Exception as e:
            print(f"Error getting customer statistics: {e}")
            raise Exception(f"Error getting customer statistics: {str(e)}")
    
    # ================================================================
    # LOYALTY SYSTEM METHODS
    # ================================================================
    
    def update_loyalty_points(self, customer_id, points_to_add, reason="Purchase"):
        """Update customer loyalty points and send notification"""
        try:
            if not ObjectId.is_valid(customer_id):
                return None
            
            # Get current customer data
            customer = self.customer_collection.find_one({'_id': ObjectId(customer_id)})
            if not customer:
                return None
            
            old_points = customer.get('loyalty_points', 0)
            new_points = old_points + points_to_add
            
            # Update loyalty points
            result = self.customer_collection.update_one(
                {'_id': ObjectId(customer_id)},
                {
                    '$set': {
                        'loyalty_points': new_points,
                        'last_updated': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                # Send loyalty points notification
                try:
                    customer_name = customer.get('full_name', customer.get('email', 'Customer'))
                    
                    notification_service.create_notification(
                        title="Loyalty Points Updated",
                        message=f"Customer '{customer_name}' earned {points_to_add} loyalty points. Total: {new_points} points",
                        priority="low",
                        notification_type="system",
                        metadata={
                            "customer_id": str(customer_id),
                            "customer_name": customer_name,
                            "points_added": points_to_add,
                            "old_points": old_points,
                            "new_points": new_points,
                            "reason": reason,
                            "action_type": "loyalty_points_updated"
                        }
                    )
                except Exception as notification_error:
                    print(f"Failed to create loyalty points notification: {notification_error}")
                
                # Return updated customer
                updated_customer = self.customer_collection.find_one({'_id': ObjectId(customer_id)})
                return self.convert_object_id(updated_customer)
            
            return None
            
        except Exception as e:
            raise Exception(f"Error updating loyalty points: {str(e)}")
    
    # ================================================================
    # SEARCH AND FILTER METHODS
    # ================================================================
    
    def search_customers(self, search_term):
        """Search customers by name, email, or phone"""
        try:
            regex_pattern = {'$regex': search_term, '$options': 'i'}
            customers = list(self.customer_collection.find({
                '$or': [
                    {'full_name': regex_pattern},
                    {'email': regex_pattern},
                    {'phone': regex_pattern}
                ]
            }))
            return [self.convert_object_id(customer) for customer in customers]
        except Exception as e:
            raise Exception(f"Error searching customers: {str(e)}")
    
    def get_customers_by_status(self, status):
        """Get customers filtered by status"""
        try:
            customers = list(self.customer_collection.find({'status': status}))
            return [self.convert_object_id(customer) for customer in customers]
        except Exception as e:
            raise Exception(f"Error getting customers by status: {str(e)}")
    
    def get_high_value_customers(self, min_loyalty_points=1000):
        """Get customers with high loyalty points"""
        try:
            customers = list(self.customer_collection.find({
                'loyalty_points': {'$gte': min_loyalty_points}
            }).sort('loyalty_points', -1))
            return [self.convert_object_id(customer) for customer in customers]
        except Exception as e:
            raise Exception(f"Error getting high value customers: {str(e)}")