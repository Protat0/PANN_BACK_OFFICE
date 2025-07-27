from bson import ObjectId
from datetime import datetime
from ..database import db_manager
from ..models import Customer
import bcrypt
from notifications.services import notification_service

class CustomerService:
    def __init__(self):
        """Initialize CustomerService with audit logging"""
        self.db = db_manager.get_database()  
        self.customer_collection = self.db.customers  
        self.user_collection = self.db.users 
        self.session_logs = self.db.session_logs
        
        # ✅ ADD: Initialize audit service
        try:
            from .audit_service import AuditLogService
            self.audit_service = AuditLogService()
            print("✅ Audit service initialized for CustomerService")
        except Exception as e:
            print(f"⚠️ Could not initialize audit service: {e}")
            self.audit_service = None
    
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
    
    def create_customer(self, customer_data, current_user=None):
        """Create a new customer in both users and customers collections with audit logging"""
        try:
            print(f"🔍 Creating new customer")
            print(f"🔍 Customer data: {customer_data}")
            if current_user:
                print(f"🔍 User: {current_user['username']}")
            
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
            
            # ✅ ADD: Audit logging for successful creation
            if current_user and hasattr(self, 'audit_service'):
                try:
                    # Create audit log for customer creation
                    audit_customer_data = created_customer.copy()
                    audit_customer_data['_id'] = user_id
                    
                    self.audit_service.log_customer_create(current_user, audit_customer_data)
                    print(f"✅ Audit log created for customer creation")
                except Exception as audit_error:
                    print(f"❌ Audit logging failed: {audit_error}")
            
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
    
    def update_customer(self, customer_id, customer_data, current_user=None):
        """Update customer in both collections with audit logging"""
        try:
            print(f"🔍 Updating customer {customer_id}")
            print(f"🔍 Update data: {customer_data}")
            if current_user:
                print(f"🔍 User: {current_user['username']}")
            
            if not ObjectId.is_valid(customer_id):
                return None
            
            # Get current customer data for notification comparison and audit
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
                
                # ✅ ADD: Audit logging for successful update
                if current_user and hasattr(self, 'audit_service'):
                    try:
                        # Create audit log for customer update
                        self.audit_service.log_customer_update(
                            current_user, 
                            customer_id, 
                            old_customer, 
                            customer_data
                        )
                        print(f"✅ Audit log created for customer update")
                    except Exception as audit_error:
                        print(f"❌ Audit logging failed: {audit_error}")
                
                return updated_customer
            return None
        
        except Exception as e:
            raise Exception(f"Error updating customer: {str(e)}")
    
    def delete_customer(self, customer_id, current_user=None):
        """Delete customer from both collections with audit logging"""
        try:
            print(f"🔍 Deleting customer {customer_id}")
            if current_user:
                print(f"🔍 User: {current_user['username']}")
            
            if not ObjectId.is_valid(customer_id):
                return False
            
            # Get customer data before deletion for notification and audit
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
                
                # ✅ ADD: Audit logging for successful deletion
                if current_user and hasattr(self, 'audit_service'):
                    try:
                        # Create audit log for customer deletion
                        self.audit_service.log_customer_delete(current_user, customer_to_delete)
                        print(f"✅ Audit log created for customer deletion")
                    except Exception as audit_error:
                        print(f"❌ Audit logging failed: {audit_error}")
                
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
    
    def update_loyalty_points(self, customer_id, points_to_add, reason="Purchase", current_user=None):
        """Update customer loyalty points and send notification with audit logging"""
        try:
            print(f"🔍 Updating loyalty points for customer {customer_id}")
            print(f"🔍 Points to add: {points_to_add}, reason: {reason}")
            if current_user:
                print(f"🔍 User: {current_user['username']}")
            
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
                
                # ✅ ADD: Audit logging for successful loyalty points update
                if current_user and hasattr(self, 'audit_service'):
                    try:
                        # Create audit log for loyalty points update
                        self.audit_service.log_customer_update(
                            current_user,
                            customer_id,
                            old_values={"loyalty_points": old_points},
                            new_values={"loyalty_points": new_points, "points_added": points_to_add, "reason": reason}
                        )
                        print(f"✅ Audit log created for loyalty points update")
                    except Exception as audit_error:
                        print(f"❌ Audit logging failed: {audit_error}")
                
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
        
    def bulk_delete_customers(self, customer_ids, current_user=None):
        """Bulk delete multiple customers with audit logging"""
        try:
            print(f"🔍 Bulk deleting {len(customer_ids)} customers")
            if current_user:
                print(f"🔍 User: {current_user['username']}")
            
            if not isinstance(customer_ids, list) or not customer_ids:
                return {"success": False, "error": "Invalid customer IDs"}
            
            # Validate ObjectIds
            valid_ids = []
            for customer_id in customer_ids:
                if ObjectId.is_valid(customer_id):
                    valid_ids.append(ObjectId(customer_id))
            
            if not valid_ids:
                return {"success": False, "error": "No valid customer IDs provided"}
            
            # Get customers to delete for audit logging
            customers_to_delete = list(self.customer_collection.find({'_id': {'$in': valid_ids}}))
            
            # Delete from both collections
            customer_result = self.customer_collection.delete_many({'_id': {'$in': valid_ids}})
            user_result = self.user_collection.delete_many({'_id': {'$in': valid_ids}})
            
            deleted_count = customer_result.deleted_count
            
            if deleted_count > 0:
                # Send notification for bulk deletion
                try:
                    notification_service.create_notification(
                        title="Bulk Customer Deletion",
                        message=f"{deleted_count} customers have been deleted from the system",
                        priority="high",
                        notification_type="system",
                        metadata={
                            "deleted_count": deleted_count,
                            "requested_count": len(customer_ids),
                            "action_type": "customers_bulk_deleted"
                        }
                    )
                except Exception as notification_error:
                    print(f"Failed to create bulk deletion notification: {notification_error}")
                
                # ✅ ADD: Audit logging for successful bulk deletion
                if current_user and hasattr(self, 'audit_service'):
                    try:
                        # Create audit log for bulk deletion
                        deleted_ids = [str(customer['_id']) for customer in customers_to_delete]
                        self.audit_service.log_customer_bulk_delete(
                            current_user, 
                            deleted_count, 
                            deleted_ids
                        )
                        print(f"✅ Audit log created for bulk customer deletion")
                    except Exception as audit_error:
                        print(f"❌ Audit logging failed: {audit_error}")
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "requested_count": len(customer_ids)
            }
        
        except Exception as e:
            raise Exception(f"Error bulk deleting customers: {str(e)}")
        
def check_low_stock_warnings(self, checkout_data, current_user=None):
    """Check if any products will go below low stock threshold and send notifications"""
    warnings = []
    
    for item in checkout_data:
        product = self.products_collection.find_one({'_id': ObjectId(item['product_id'])})
        
        if product:
            current_stock = product.get('stock', 0)
            quantity_sold = item['quantity']
            low_stock_threshold = product.get('low_stock_threshold', 5)
            
            new_stock = current_stock - quantity_sold
            product_name = product.get('product_name', 'Unknown Product')
            
            # Check for different stock warning levels
            if new_stock <= 0:
                warning_msg = f"⚠️ {product_name} will be OUT OF STOCK!"
                warnings.append(warning_msg)
                
                # Send OUT OF STOCK notification
                self._send_stock_notification(
                    'out_of_stock', 
                    product, 
                    current_stock, 
                    new_stock, 
                    quantity_sold,
                    current_user
                )
                
            elif new_stock <= low_stock_threshold:
                warning_msg = f"🔶 {product_name} will be LOW STOCK ({new_stock} remaining)"
                warnings.append(warning_msg)
                
                # Send LOW STOCK notification
                self._send_stock_notification(
                    'low_stock', 
                    product, 
                    current_stock, 
                    new_stock, 
                    quantity_sold,
                    current_user
                )
    
    return warnings

def _send_stock_notification(self, alert_type, product, current_stock, new_stock, quantity_sold, current_user=None):
    """
    Send notification for stock-related alerts
    
    Args:
        alert_type (str): 'low_stock' or 'out_of_stock'
        product (dict): Product data
        current_stock (int): Current stock level
        new_stock (int): Stock level after sale
        quantity_sold (int): Quantity being sold
        current_user (dict): User performing the transaction
    """
    try:
        product_name = product.get('product_name', 'Unknown Product')
        product_id = str(product.get('_id', ''))
        low_stock_threshold = product.get('low_stock_threshold', 5)
        
        # Configure notification based on alert type
        if alert_type == 'out_of_stock':
            title = "⚠️ PRODUCT OUT OF STOCK"
            message = f"'{product_name}' is now OUT OF STOCK after selling {quantity_sold} units"
            priority = "urgent"
            
        elif alert_type == 'low_stock':
            title = "🔶 LOW STOCK ALERT"
            message = f"'{product_name}' is running low on stock. Only {new_stock} units remaining (threshold: {low_stock_threshold})"
            priority = "high"
            
        else:
            return  # Unknown alert type
        
        # Common metadata for both alert types
        metadata = {
            "product_id": product_id,
            "product_name": product_name,
            "sku": product.get('SKU', ''),
            "category_id": product.get('category_id', ''),
            "current_stock": current_stock,
            "new_stock": new_stock,
            "quantity_sold": quantity_sold,
            "low_stock_threshold": low_stock_threshold,
            "alert_type": alert_type,
            "action_type": "stock_alert",
            "cashier_id": current_user.get('_id') if current_user else None,
            "cashier_name": current_user.get('username') if current_user else None,
            "cost_price": product.get('cost_price', 0),
            "selling_price": product.get('selling_price', 0),
            "supplier_id": product.get('supplier_id'),
            "reorder_suggested": new_stock <= low_stock_threshold
        }
        
        # Import notification service (same as customer service)
        from notifications.services import notification_service
        
        # Send the notification
        notification_service.create_notification(
            title=title,
            message=message,
            priority=priority,
            notification_type="inventory",  # Different type for inventory alerts
            metadata=metadata
        )
        
        print(f"📢 Stock notification sent: {title} for {product_name}")
        
    except Exception as notification_error:
        # Log the notification error but don't fail the main operation
        print(f"❌ Failed to create {alert_type} notification for product {product.get('product_name', 'Unknown')}: {notification_error}")