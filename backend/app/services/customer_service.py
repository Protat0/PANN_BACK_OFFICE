from bson import ObjectId
from datetime import datetime, timedelta
from ..database import db_manager
import bcrypt
from .audit_service import AuditLogService

class CustomerService:
    def __init__(self):
        """Initialize CustomerService with audit logging"""
        self.db = db_manager.get_database()  
        self.customer_collection = self.db.customers  
        self.user_collection = self.db.users 
        self.session_logs = self.db.session_logs
        self.audit_service = AuditLogService()
        
    # ================================================================
    # UTILITY METHODS
    # ================================================================
    
    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
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
    
    def validate_object_id(self, object_id):
        """Validate and convert to ObjectId"""
        if not object_id or not ObjectId.is_valid(object_id):
            return None
        return ObjectId(object_id)
    
    # ================================================================
    # CRUD OPERATIONS
    # ================================================================
    
    def create_customer(self, customer_data, current_user=None):
        """Create a new customer in both users and customers collections"""
        try:
            # Validate required fields
            if not customer_data.get("email"):
                raise ValueError("Email is required for customer creation")
            
            if not customer_data.get("password"):
                raise ValueError("Password is required for customer creation")
            
            now = datetime.utcnow()
            user_id = None

            # Create user record
            user_data = {
                "username": customer_data.get("username", customer_data["email"]),  # Use email as username if not provided
                "email": customer_data["email"],
                "password": self.hash_password(customer_data["password"]),
                "full_name": customer_data.get("full_name", ""),
                "role": "customer",
                "status": "active",
                "isDeleted": False,
                "date_created": now,
                "last_updated": now,
                "source": "customer_registration"
            }

            user_result = self.user_collection.insert_one(user_data)
            user_id = user_result.inserted_id

            # Create customer record with same ID
            customer_specific_data = {
                "_id": user_id,  # Same ID as user
                "customer_id": str(user_id),
                "full_name": customer_data.get("full_name", ""),
                "email": customer_data["email"],
                "phone": customer_data.get("phone", ""),
                "delivery_address": customer_data.get("delivery_address", {}),
                "loyalty_points": customer_data.get("loyalty_points", 0),
                "last_purchase": customer_data.get("last_purchase"),
                "isDeleted": False,
                "date_created": now,
                "last_updated": now,
                "status": "active",
                "source": "customer_registration"
            }   

            self.customer_collection.insert_one(customer_specific_data)

            # Get created customer and convert ObjectIds
            created_customer = self.customer_collection.find_one({'_id': user_id})
            created_customer = self.convert_object_id(created_customer)

            # Audit logging
            if current_user and self.audit_service:
                try:
                    self.audit_service.log_customer_create(current_user, created_customer)
                except Exception as audit_error:
                    print(f"Audit logging failed: {audit_error}")
            
            return created_customer
        
        except Exception as e:
            # Rollback user creation if customer creation fails
            if user_id:
                try:
                    self.user_collection.delete_one({'_id': user_id})
                except Exception as rollback_error:
                    print(f"Rollback failed: {rollback_error}")
            
            raise Exception(f"Error creating customer: {str(e)}")
    
    def get_customer_by_id(self, customer_id):
        """Get customer by ID"""
        try:
            object_id = self.validate_object_id(customer_id)
            if not object_id:
                return None
                
            customer = self.customer_collection.find_one({'_id': object_id})
            return self.convert_object_id(customer) if customer else None
            
        except Exception as e:
           raise Exception(f"Error getting customer data: {str(e)}")
    
    def get_all_customers(self, include_deleted=False):
        """Get all customers with optional deleted filter"""
        try:
            query = {} if include_deleted else {"isDeleted": {"$ne": True}}
            customers = list(self.customer_collection.find(query))
            return [self.convert_object_id(customer) for customer in customers]
        except Exception as e:
            raise Exception(f"Error getting customers: {str(e)}")
    
    def update_customer(self, customer_id, customer_data, current_user=None):
        """Update customer in both collections"""
        try:
            object_id = self.validate_object_id(customer_id)
            if not object_id:
                return None

            # Get old customer data for audit logging
            old_customer = self.customer_collection.find_one({'_id': object_id})
            if not old_customer:
                return None
            
            old_customer = self.convert_object_id(old_customer)

            # Prepare update data
            update_data = customer_data.copy()
            update_data['last_updated'] = datetime.utcnow()

            # Handle password hashing if provided
            if "password" in update_data:
                update_data["password"] = self.hash_password(update_data["password"])

            # Update user collection for relevant fields
            user_sync_fields = ["email", "full_name", "password"]
            user_update_data = {
                field: update_data[field]
                for field in user_sync_fields
                if field in update_data
            }

            if user_update_data:
                user_update_data["last_updated"] = update_data['last_updated']   
                self.user_collection.update_one(
                    {'_id': object_id},
                    {'$set': user_update_data}
                )

            # Update customer collection
            customer_result = self.customer_collection.update_one(
                {'_id': object_id},
                {'$set': update_data}
            )

            if customer_result.modified_count == 0 and not user_update_data:
                return old_customer  # No changes made

            # Get updated customer
            updated_customer = self.customer_collection.find_one({'_id': object_id})
            updated_customer = self.convert_object_id(updated_customer)

            # Audit logging
            if current_user and self.audit_service:
                try:
                    self.audit_service.log_customer_update(
                        current_user,
                        customer_id,
                        old_customer,
                        update_data
                    )
                except Exception as audit_error:
                    print(f"Audit logging failed: {audit_error}")

            return updated_customer

        except Exception as e:
            raise Exception(f"Error updating customer: {str(e)}")
    
    def delete_customer(self, customer_id, current_user=None):
        """Delete customer by delegating to UserService"""
        try:
            # Import here to avoid circular imports
            from .user_service import UserService
            
            user_service = UserService()
            
            # Verify this is actually a customer before deleting
            customer = self.get_customer_by_id(customer_id)
            if not customer:
                return False
            
            # Delegate to UserService for consistent deletion logic
            result = user_service.soft_delete_user(customer_id, current_user)
            
            # Additional customer-specific cleanup if needed
            if result:
                # Could add customer-specific cleanup here if needed
                # e.g., cancel orders, clear shopping cart, etc.
                pass
            
            return result
            
        except Exception as e:
            raise Exception(f"Error deleting customer: {str(e)}")
    
    def restore_customer(self, customer_id, current_user=None):
        """Restore customer by delegating to UserService"""
        try:
            from .user_service import UserService
            
            user_service = UserService()
            return user_service.restore_user(customer_id, current_user)
            
        except Exception as e:
            raise Exception(f"Error restoring customer: {str(e)}")

    def hard_delete_customer(self, customer_id, current_user=None):
        """Permanently delete customer by delegating to UserService"""
        try:
            from .user_service import UserService
            
            user_service = UserService()
            
            # Additional customer-specific cleanup before permanent deletion
            # e.g., anonymize orders, clear personal data, etc.
            
            return user_service.hard_delete_user(customer_id, current_user)
            
        except Exception as e:
            raise Exception(f"Error permanently deleting customer: {str(e)}")
    
    # ================================================================
    # ANALYTICS AND METRICS
    # ================================================================
    
    def get_customer_statistics(self):
        """Get comprehensive customer statistics"""
        try:
            # Basic counts
            total_customers = self.customer_collection.count_documents({"isDeleted": {"$ne": True}})
            active_customers = self.customer_collection.count_documents({
                "status": "active",
                "isDeleted": {"$ne": True}
            })
            
            # Monthly registrations
            today = datetime.now()
            start_of_month = datetime(today.year, today.month, 1)
            start_of_next_month = datetime(today.year + 1, 1, 1) if today.month == 12 else datetime(today.year, today.month + 1, 1)
            
            monthly_registrations = self.customer_collection.count_documents({
                "date_created": {"$gte": start_of_month, "$lt": start_of_next_month},
                "isDeleted": {"$ne": True}
            })
            
            # Daily logins
            start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
            start_of_next_day = start_of_day + timedelta(days=1)
            
            daily_login_user_ids = self.session_logs.distinct("user_id", {
                "login_time": {"$gte": start_of_day, "$lt": start_of_next_day}
            })
            
            if daily_login_user_ids:
                try:
                    object_ids = [ObjectId(uid) if isinstance(uid, str) else uid for uid in daily_login_user_ids]
                    daily_logins = self.customer_collection.count_documents({
                        "_id": {"$in": object_ids},
                        "isDeleted": {"$ne": True}
                    })
                except:
                    daily_logins = 0
            else:
                daily_logins = 0
            
            # Loyalty points statistics
            loyalty_pipeline = [
                {"$match": {"isDeleted": {"$ne": True}}},
                {"$group": {
                    "_id": None,
                    "total_loyalty_points": {"$sum": "$loyalty_points"},
                    "avg_loyalty_points": {"$avg": "$loyalty_points"},
                    "max_loyalty_points": {"$max": "$loyalty_points"}
                }}
            ]

            loyalty_stats = list(self.customer_collection.aggregate(loyalty_pipeline))
            loyalty_data = loyalty_stats[0] if loyalty_stats else {}
           
            stats = {
                'total_customers': total_customers,
                'active_customers': active_customers,
                'inactive_customers': total_customers - active_customers,
                'monthly_registrations': monthly_registrations,
                'daily_logins': daily_logins,
                'total_loyalty_points': loyalty_data.get('total_loyalty_points', 0) or 0,
                'avg_loyalty_points': round(loyalty_data.get('avg_loyalty_points', 0) or 0, 2),
                'max_loyalty_points': loyalty_data.get('max_loyalty_points', 0) or 0
            }
            
            return stats

        except Exception as e:
            raise Exception(f"Error getting customer statistics: {str(e)}")
    
    # ================================================================
    # LOYALTY SYSTEM METHODS
    # ================================================================
    
    def update_loyalty_points(self, customer_id, points_to_add, reason="Purchase", current_user=None):
        """Update customer loyalty points"""
        try:
            object_id = self.validate_object_id(customer_id)
            if not object_id:
                return None
            
            if not isinstance(points_to_add, (int, float)) or points_to_add < 0:
                raise ValueError("Points to add must be a positive number")
            
            # Get current customer data for audit logging
            customer = self.customer_collection.find_one({'_id': object_id})
            if not customer:
                return None
            
            old_points = customer.get('loyalty_points', 0)
            
            # Update loyalty points
            result = self.customer_collection.update_one(
                {'_id': object_id},
                {
                    '$inc': {'loyalty_points': points_to_add},
                    '$set': {'last_updated': datetime.utcnow()}
                }
            )
            
            if result.modified_count == 0:
                return None
            
            # Get updated customer
            updated_customer = self.customer_collection.find_one({'_id': object_id})
            updated_customer = self.convert_object_id(updated_customer)

            # Audit logging
            if current_user and self.audit_service:
                try:
                    self.audit_service.log_customer_update(
                        current_user,
                        customer_id,
                        {"loyalty_points": old_points},
                        {"loyalty_points": old_points + points_to_add, "reason": reason}
                    )
                except Exception as audit_error:
                    print(f"Audit logging failed: {audit_error}")

            return updated_customer
            
        except Exception as e:
            raise Exception(f"Error updating loyalty points: {str(e)}")
    
    # ================================================================
    # SEARCH AND FILTER METHODS
    # ================================================================
    
    def search_customers(self, search_term, include_deleted=False):
        """Search customers by name, email, or phone"""
        try:
            if not search_term or not search_term.strip():
                return []

            import re
            escaped_term = re.escape(search_term.strip())
            regex_pattern = {'$regex': escaped_term, '$options': 'i'}

            query = {
                '$or': [
                    {'full_name': regex_pattern},
                    {'email': regex_pattern},
                    {'phone': regex_pattern}
                ]
            }
            
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}

            customers = list(self.customer_collection.find(query).limit(100))
            return [self.convert_object_id(customer) for customer in customers]

        except Exception as e:
            raise Exception(f"Error searching customers: {str(e)}")
    
    def get_customers_by_status(self, status, include_deleted=False):
        """Get customers filtered by status"""
        try:
            if not status or not status.strip():
                return []
            
            query = {'status': status.strip().lower()}
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
                
            customers = list(self.customer_collection.find(query))
            return [self.convert_object_id(customer) for customer in customers]
        except Exception as e:
            raise Exception(f"Error getting customers by status: {str(e)}")
    
    def get_high_value_customers(self, min_loyalty_points=1000, include_deleted=False):
        """Get customers with high loyalty points"""
        try:
            if min_loyalty_points < 0:
                raise ValueError("Minimum loyalty points cannot be negative")
            
            query = {'loyalty_points': {'$gte': min_loyalty_points}}
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
                
            customers = list(self.customer_collection.find(query).sort('loyalty_points', -1))
            return [self.convert_object_id(customer) for customer in customers]
        except Exception as e:
            raise Exception(f"Error getting high value customers: {str(e)}")
    
    def get_customer_by_email(self, email, include_deleted=False):
        """Get customer by email"""
        try:
            if not email:
                return None
                
            query = {'email': email.strip().lower()}
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
                
            customer = self.customer_collection.find_one(query)
            return self.convert_object_id(customer) if customer else None
        except Exception as e:
            raise Exception(f"Error getting customer by email: {str(e)}")
    
    def get_deleted_customers(self):
        """Get all soft-deleted customers"""
        try:
            customers = list(self.customer_collection.find({"isDeleted": True}))
            return [self.convert_object_id(customer) for customer in customers]
        except Exception as e:
            raise Exception(f"Error getting deleted customers: {str(e)}")