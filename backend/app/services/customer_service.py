from bson import ObjectId
from datetime import datetime, timedelta
from ..database import db_manager
import bcrypt
import logging
from .audit_service import AuditLogService
logger = logging.getLogger(__name__)

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
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        if not password:
            raise ValueError("Password cannot be empty")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    # ================================================================
    # CRUD OPERATIONS
    # ================================================================
    def get_customers(self, page=1, limit=50, status=None, min_loyalty_points=None, include_deleted=False, sort_by=None):
        """Get customers with pagination and filters - handles all customer queries"""
        try:
            query = {}
            
            # Build query filters
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
            if status:
                query['status'] = status
            if min_loyalty_points:
                query['loyalty_points'] = {'$gte': min_loyalty_points}
            
            # Handle sorting
            sort_options = {}
            if sort_by == 'loyalty_desc':
                sort_options = [('loyalty_points', -1)]
            elif sort_by == 'date_desc':
                sort_options = [('date_created', -1)]
            else:
                sort_options = [('date_created', -1)]  # Default sort
                
            skip = (page - 1) * limit
            
            # Execute query with sorting
            if sort_options:
                customers = list(self.customer_collection.find(query).sort(sort_options).skip(skip).limit(limit))
            else:
                customers = list(self.customer_collection.find(query).skip(skip).limit(limit))
                
            total = self.customer_collection.count_documents(query)
            
            return {
                'customers': customers,
                'total': total,
                'page': page,
                'limit': limit,
                'has_more': skip + limit < total,
                'filters_applied': {
                    'status': status,
                    'min_loyalty_points': min_loyalty_points,
                    'include_deleted': include_deleted
                }
            }
        except Exception as e:
            raise Exception(f"Error getting customers: {str(e)}")
    
    def generate_customer_id(self):
        """Generate sequential CUST-##### format ID"""
        try:
            pipeline = [
                {"$match": {"_id": {"$regex": "^CUST-"}}},
                {"$addFields": {
                    "id_number": {
                        "$toInt": {"$substr": ["$_id", 5, -1]}
                    }
                }},
                {"$sort": {"id_number": -1}},
                {"$limit": 1}
            ]
            
            result = list(self.customer_collection.aggregate(pipeline))
            next_number = (result[0]["id_number"] + 1) if result else 1
            
            return f"CUST-{next_number:05d}"  # 5 digits
            
        except Exception as e:
            logger.error(f"Error generating customer ID: {e}")
            import time
            return f"CUST-{int(time.time()) % 100000:05d}"

    def create_customer(self, customer_data, current_user=None):
        """Create customer with sequential CUST-##### ID"""
        try:
            if not customer_data.get("email") or not customer_data.get("password"):
                raise ValueError("Email and password are required")
            
            # Generate sequential ID
            customer_id = self.generate_customer_id()
            now = datetime.utcnow()
            
            # Create user record
            user_data = {
                "_id": customer_id,
                "username": customer_data.get("username", customer_data["email"]),
                "email": customer_data["email"],
                "password": self.hash_password(customer_data["password"]),
                "full_name": customer_data.get("full_name", ""),
                "role": "customer",
                "status": "active",
                "isDeleted": False,
                "date_created": now,
                "last_updated": now
            }
            
            # Create customer record
            customer_record = {
                "_id": customer_id,
                "customer_id": customer_id,
                "full_name": customer_data.get("full_name", ""),
                "email": customer_data["email"],
                "phone": customer_data.get("phone", ""),
                "delivery_address": customer_data.get("delivery_address", {}),
                "loyalty_points": customer_data.get("loyalty_points", 0),
                "last_purchase": customer_data.get("last_purchase"),
                "isDeleted": False,
                "date_created": now,
                "last_updated": now,
                "status": "active"
            }
            
            # Insert both records
            self.user_collection.insert_one(user_data)
            self.customer_collection.insert_one(customer_record)
            
            # Audit logging
            if current_user and self.audit_service:
                try:
                    self.audit_service.log_customer_create(current_user, customer_record)
                except Exception as audit_error:
                    logger.error(f"Audit logging failed: {audit_error}")
            
            return customer_record
            
        except Exception as e:
            raise Exception(f"Error creating customer: {str(e)}")
    
    def get_customer_by_id(self, customer_id, include_deleted=False):
        """Get customer by CUST-##### ID"""
        try:
            if not customer_id:
                return None
                
            query = {'_id': customer_id}
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
                
            return self.customer_collection.find_one(query)
            
        except Exception as e:
           raise Exception(f"Error getting customer: {str(e)}")
    
    def update_customer(self, customer_id, customer_data, current_user=None):
        """Update customer in both collections"""
        try:
            if not customer_id:
                return None

            # Get old customer data for audit
            old_customer = self.customer_collection.find_one({
                '_id': customer_id,
                'isDeleted': {'$ne': True}
            })
            if not old_customer:
                return None

            # Prepare update data
            update_data = customer_data.copy()
            update_data['last_updated'] = datetime.utcnow()

            # Handle password hashing
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
                    {'_id': customer_id},
                    {'$set': user_update_data}
                )

            # Update customer collection
            result = self.customer_collection.update_one(
                {'_id': customer_id, 'isDeleted': {'$ne': True}},
                {'$set': update_data}
            )

            if result.modified_count == 0 and not user_update_data:
                return old_customer

            # Get updated customer
            updated_customer = self.customer_collection.find_one({'_id': customer_id})

            # Audit logging
            if current_user and self.audit_service:
                try:
                    self.audit_service.log_customer_update(
                        current_user, customer_id, old_customer, update_data
                    )
                except Exception as audit_error:
                    logger.error(f"Audit logging failed: {audit_error}")

            return updated_customer

        except Exception as e:
            raise Exception(f"Error updating customer: {str(e)}")
    
    def delete_customer(self, customer_id, current_user=None):
        """Delete customer by delegating to UserService"""
        try:
            from .user_service import UserService
            user_service = UserService()
            
            customer = self.get_customer_by_id(customer_id)
            if not customer:
                return False
            
            return user_service.soft_delete_user(customer_id, current_user)
            
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

    def hard_delete_customer(self, customer_id, current_user=None, confirmation_token=None):
        """Permanently delete customer by delegating to UserService"""
        try:
            from .user_service import UserService
            user_service = UserService()
            return user_service.hard_delete_user(customer_id, current_user, confirmation_token)
            
        except Exception as e:
            raise Exception(f"Error permanently deleting customer: {str(e)}")
    
    # ================================================================
    # ANALYTICS AND METRICS
    # ================================================================
    
    def get_customer_statistics(self):
        """Get customer statistics"""
        try:
            total_customers = self.customer_collection.count_documents({"isDeleted": {"$ne": True}})
            active_customers = self.customer_collection.count_documents({
                "status": "active", "isDeleted": {"$ne": True}
            })
            
            # Monthly registrations
            today = datetime.now()
            start_of_month = datetime(today.year, today.month, 1)
            monthly_registrations = self.customer_collection.count_documents({
                "date_created": {"$gte": start_of_month},
                "isDeleted": {"$ne": True}
            })
            
            # Loyalty stats
            loyalty_pipeline = [
                {"$match": {"isDeleted": {"$ne": True}}},
                {"$group": {
                    "_id": None,
                    "total_loyalty_points": {"$sum": "$loyalty_points"},
                    "avg_loyalty_points": {"$avg": "$loyalty_points"}
                }}
            ]

            loyalty_stats = list(self.customer_collection.aggregate(loyalty_pipeline))
            loyalty_data = loyalty_stats[0] if loyalty_stats else {}
           
            return {
                'total_customers': total_customers,
                'active_customers': active_customers,
                'inactive_customers': total_customers - active_customers,
                'monthly_registrations': monthly_registrations,
                'total_loyalty_points': loyalty_data.get('total_loyalty_points', 0) or 0,
                'avg_loyalty_points': round(loyalty_data.get('avg_loyalty_points', 0) or 0, 2)
            }

        except Exception as e:
            raise Exception(f"Error getting customer statistics: {str(e)}")
    
    # ================================================================
    # LOYALTY SYSTEM METHODS
    # ================================================================
    
    def update_loyalty_points(self, customer_id, points_to_add, reason="Purchase", current_user=None):
        """Update customer loyalty points"""
        try:
            if not customer_id or points_to_add < 0:
                return None
            
            result = self.customer_collection.update_one(
                {'_id': customer_id, 'isDeleted': {'$ne': True}},
                {
                    '$inc': {'loyalty_points': points_to_add},
                    '$set': {'last_updated': datetime.utcnow()}
                }
            )
            
            if result.modified_count == 0:
                return None
            
            return self.customer_collection.find_one({'_id': customer_id})
            
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
            return customers

        except Exception as e:
            raise Exception(f"Error searching customers: {str(e)}")
    
    
    def get_customer_by_email(self, email, include_deleted=False):
        """Get customer by email"""
        try:
            if not email:
                return None
                
            query = {'email': email.strip().lower()}
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
                
            return self.customer_collection.find_one(query)
        except Exception as e:
            raise Exception(f"Error getting customer by email: {str(e)}")
    
