# ========================================
# ENHANCED AUDIT SERVICE with Proper ID Formats
# audit_service.py - All POS System Modules with Correct ID Patterns
# ========================================

from datetime import datetime
from bson import ObjectId
from ..database import db_manager
import logging

class AuditLogService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.collection = self.db.audit_logs
    
    def generate_audit_id(self):
        """Generate sequential AUD-###### ID (6 digits - high volume system logs)"""
        try:
            # Use aggregation to find highest existing number
            pipeline = [
                {
                    '$match': {
                        'audit_id': {'$regex': '^AUD-\\d{6}$'}
                    }
                },
                {
                    '$addFields': {
                        'numeric_part': {
                            '$toInt': {'$substr': ['$audit_id', 4, 6]}
                        }
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'max_number': {'$max': '$numeric_part'}
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            if result and result[0]['max_number'] is not None:
                next_number = result[0]['max_number'] + 1
            else:
                # Fallback to count-based approach
                next_number = self.collection.count_documents({}) + 1
            
            return f"AUD-{next_number:06d}"
            
        except Exception as e:
            logging.error(f"Error generating audit ID: {e}")
            # Emergency fallback using timestamp
            import time
            fallback_number = int(time.time()) % 1000000  # Last 6 digits of timestamp
            return f"AUD-{fallback_number:06d}"
    
    def convert_object_id(self, document):
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    def _create_audit_log(self, event_type, user_data, target_data=None, old_values=None, new_values=None, metadata=None):
        """Create a standardized audit log entry with sequential AUD-###### ID"""
        try:
            audit_id = self.generate_audit_id()
            
            audit_data = {
                "audit_id": audit_id,  # AUD-###### (6 digits)
                "event_type": event_type,
                "user_id": user_data.get("user_id", user_data.get("username", "system")),  # USER-#### format
                "username": user_data.get("username", user_data.get("email", "system")),
                "branch_id": user_data.get("branch_id", 1),
                "ip_address": user_data.get("ip_address"),
                "user_agent": user_data.get("user_agent"),
                "timestamp": datetime.utcnow(),
                "status": "success",
                "source": "audit_service",
                "last_updated": datetime.utcnow()
            }
            
            # Add target information if provided
            if target_data:
                audit_data.update({
                    "target_type": target_data.get("type"),
                    "target_id": target_data.get("id"),  # Will be proper format (PROD-#####, CUST-#####, etc.)
                    "target_name": target_data.get("name")
                })
            
            # Add change information if provided
            if old_values or new_values:
                audit_data["changes"] = {
                    "old_values": old_values or {},
                    "new_values": new_values or {},
                    "changed_fields": list(new_values.keys()) if new_values else []
                }
            
            # Add metadata if provided
            if metadata:
                audit_data["metadata"] = metadata
            
            result = self.collection.insert_one(audit_data)
            return {"audit_id": audit_id, "db_id": str(result.inserted_id)}
            
        except Exception as e:
            raise Exception(f"Error creating audit log: {str(e)}")

    # ========================================
    # CORE BUSINESS ENTITIES - HIGH FREQUENCY
    # ========================================
    
    # SALE-###### (6 digits - highest transaction volume)
    def log_sale_create(self, user_data, sale_data):
        """Log sale transaction - SALE-###### format"""
        return self._create_audit_log(
            event_type="sale_create",
            user_data=user_data,
            target_data={
                "type": "sale",
                "id": sale_data.get("sale_id", "Unknown"),  # SALE-######
                "name": f"Sale #{sale_data.get('sale_id', 'Unknown')}"
            },
            new_values={
                "sale_id": sale_data.get("sale_id"),  # SALE-######
                "customer_id": sale_data.get("customer_id"),  # CUST-#####
                "user_id": sale_data.get("user_id"),  # USER-####
                "total_amount": sale_data.get("total_amount", 0),
                "payment_method": sale_data.get("payment_method"),
                "items_count": len(sale_data.get("items", [])),
                "discount_applied": sale_data.get("discount_applied", 0),
                "promotion_id": sale_data.get("promotion_id")  # PROM-####
            },
            metadata={
                "action": "create",
                "module": "sales",
                "item_count": len(sale_data.get("items", [])),
                "net_amount": sale_data.get("total_amount", 0) - sale_data.get("discount_applied", 0)
            }
        )
    
    # ORDR-###### (6 digits - online + POS orders)
    def log_order_create(self, user_data, order_data):
        """Log order creation - ORDR-###### format"""
        return self._create_audit_log(
            event_type="order_create",
            user_data=user_data,
            target_data={
                "type": "order",
                "id": order_data.get("order_id", "Unknown"),  # ORDR-######
                "name": f"Order #{order_data.get('order_id', 'Unknown')}"
            },
            new_values={
                "order_id": order_data.get("order_id"),  # ORDR-######
                "customer_id": order_data.get("customer_id"),  # CUST-#####
                "order_type": order_data.get("order_type", "POS"),  # POS or Online
                "status": order_data.get("status", "pending"),
                "total_amount": order_data.get("total_amount", 0),
                "items_count": len(order_data.get("items", [])),
                "promotion_id": order_data.get("promotion_id")  # PROM-####
            },
            metadata={
                "action": "create",
                "module": "orders",
                "order_type": order_data.get("order_type", "POS")
            }
        )
    
    def log_order_status_change(self, user_data, order_data, old_status, new_status):
        """Log order status change"""
        return self._create_audit_log(
            event_type="order_status_change",
            user_data=user_data,
            target_data={
                "type": "order",
                "id": order_data.get("order_id", "Unknown"),  # ORDR-######
                "name": f"Order #{order_data.get('order_id', 'Unknown')}"
            },
            old_values={"status": old_status},
            new_values={"status": new_status},
            metadata={
                "action": "status_change",
                "module": "orders",
                "status_flow": f"{old_status} → {new_status}"
            }
        )
    
    # INVT-##### (5 digits - inventory movements)
    def log_inventory_movement(self, user_data, inventory_data, movement_type="adjustment"):
        """Log inventory movement - INVT-##### format"""
        return self._create_audit_log(
            event_type="inventory_movement",
            user_data=user_data,
            target_data={
                "type": "inventory",
                "id": inventory_data.get("inventory_id", "Unknown"),  # INVT-#####
                "name": f"Inventory #{inventory_data.get('inventory_id', 'Unknown')}"
            },
            new_values={
                "inventory_id": inventory_data.get("inventory_id"),  # INVT-#####
                "product_id": inventory_data.get("product_id"),  # PROD-#####
                "movement_type": movement_type,  # in, out, adjustment, damaged
                "quantity": inventory_data.get("quantity", 0),
                "reason": inventory_data.get("reason", "manual"),
                "reference_id": inventory_data.get("reference_id")  # SALE-###### or ORDR-######
            },
            metadata={
                "action": "movement",
                "module": "inventory",
                "movement_type": movement_type,
                "value_impact": inventory_data.get("quantity", 0) * inventory_data.get("unit_cost", 0)
            }
        )

    # ========================================
    # PRODUCT & CATALOG MANAGEMENT
    # ========================================
    
    # PROD-##### (5 digits - product catalog)
    def log_product_create(self, user_data, product_data):
        """Log product creation - PROD-##### format"""
        return self._create_audit_log(
            event_type="product_create",
            user_data=user_data,
            target_data={
                "type": "product",
                "id": product_data.get("product_id", "Unknown"),  # PROD-#####
                "name": product_data.get("product_name", product_data.get("name", "Unknown"))
            },
            new_values={
                "product_id": product_data.get("product_id"),  # PROD-#####
                "name": product_data.get("product_name", product_data.get("name")),
                "category_id": product_data.get("category_id"),  # CTGY-###
                "supplier_id": product_data.get("supplier_id"),  # SUPP-###
                "price": product_data.get("price"),
                "cost": product_data.get("cost"),
                "stock_quantity": product_data.get("stock_quantity", 0),
                "sku": product_data.get("sku"),
                "description": product_data.get("description")
            },
            metadata={
                "action": "create",
                "module": "products",
                "profit_margin": product_data.get("price", 0) - product_data.get("cost", 0)
            }
        )
    
    # CTGY-### (3 digits - fewer categories)
    def log_category_create(self, user_data, category_data):
        """Log category creation - CTGY-### format"""
        return self._create_audit_log(
            event_type="category_create",
            user_data=user_data,
            target_data={
                "type": "category",
                "id": category_data.get("category_id", "Unknown"),  # CTGY-###
                "name": category_data.get("category_name", category_data.get("name", "Unknown"))
            },
            new_values={
                "category_id": category_data.get("category_id"),  # CTGY-###
                "name": category_data.get("category_name", category_data.get("name")),
                "description": category_data.get("description"),
                "parent_category": category_data.get("parent_category"),  # CTGY-###
                "subcategories": category_data.get("subcategories", [])
            },
            metadata={
                "action": "create",
                "module": "categories",
                "subcategory_count": len(category_data.get("subcategories", []))
            }
        )
    
    # SUPP-### (3 digits - limited suppliers)
    def log_supplier_create(self, user_data, supplier_data):
        """Log supplier creation - SUPP-### format"""
        return self._create_audit_log(
            event_type="supplier_create",
            user_data=user_data,
            target_data={
                "type": "supplier",
                "id": supplier_data.get("supplier_id", "Unknown"),  # SUPP-###
                "name": supplier_data.get("supplier_name", supplier_data.get("name", "Unknown"))
            },
            new_values={
                "supplier_id": supplier_data.get("supplier_id"),  # SUPP-###
                "name": supplier_data.get("supplier_name", supplier_data.get("name")),
                "contact_person": supplier_data.get("contact_person"),
                "email": supplier_data.get("email"),
                "phone": supplier_data.get("phone"),
                "address": supplier_data.get("address"),
                "payment_terms": supplier_data.get("payment_terms")
            },
            metadata={"action": "create", "module": "suppliers"}
        )

    # ========================================
    # PROMOTIONS & DISCOUNTS
    # ========================================
    
    # PROM-#### (4 digits - covers all promotional activities)
    def log_promotion_create(self, user_data, promotion_data):
        """Log promotion creation - PROM-#### format"""
        return self._create_audit_log(
            event_type="promotion_create",
            user_data=user_data,
            target_data={
                "type": "promotion",
                "id": promotion_data.get("promotion_id", "Unknown"),  # PROM-####
                "name": promotion_data.get("name", "Unknown Promotion")
            },
            new_values={
                "promotion_id": promotion_data.get("promotion_id"),  # PROM-####
                "name": promotion_data.get("name"),
                "type": promotion_data.get("type"),  # percentage, fixed_amount, buy_x_get_y
                "discount_value": promotion_data.get("discount_value"),
                "target_type": promotion_data.get("target_type"),  # products, categories, all
                "target_ids": promotion_data.get("target_ids", []),  # PROD-##### or CTGY-###
                "start_date": str(promotion_data.get("start_date", "")),
                "end_date": str(promotion_data.get("end_date", "")),
                "usage_limit": promotion_data.get("usage_limit")
            },
            metadata={"action": "create", "module": "promotions"}
        )
    
    def log_promotion_application(self, user_data, promotion_data, order_data, discount_amount):
        """Log promotion application to order/sale"""
        return self._create_audit_log(
            event_type="promotion_application",
            user_data=user_data,
            target_data={
                "type": "promotion",
                "id": promotion_data.get("promotion_id", "Unknown"),  # PROM-####
                "name": promotion_data.get("name", "Unknown Promotion")
            },
            metadata={
                "action": "apply",
                "module": "promotions",
                "order_id": order_data.get("order_id"),  # ORDR-###### or SALE-######
                "customer_id": order_data.get("customer_id"),  # CUST-#####
                "discount_amount": discount_amount,
                "order_total": order_data.get("total_amount", 0)
            }
        )

    # ========================================
    # USER MANAGEMENT
    # ========================================
    
    # USER-#### (4 digits - staff accounts)
    def log_user_create(self, admin_user, new_user_data):
        """Log user creation - USER-#### format"""
        return self._create_audit_log(
            event_type="user_create",
            user_data=admin_user,
            target_data={
                "type": "user",
                "id": new_user_data.get("user_id", "Unknown"),  # USER-####
                "name": new_user_data.get("username", new_user_data.get("email", "Unknown"))
            },
            new_values={
                "user_id": new_user_data.get("user_id"),  # USER-####
                "username": new_user_data.get("username"),
                "email": new_user_data.get("email"),
                "role": new_user_data.get("role"),
                "status": new_user_data.get("status", "active"),
                "branch_id": new_user_data.get("branch_id")
            },
            metadata={"action": "create", "module": "users"}
        )
    
    # CUST-##### (5 digits - customer base)
    def log_customer_create(self, user_data, customer_data):
        """Log customer creation - CUST-##### format"""
        return self._create_audit_log(
            event_type="customer_create",
            user_data=user_data,
            target_data={
                "type": "customer",
                "id": customer_data.get("customer_id", "Unknown"),  # CUST-#####
                "name": customer_data.get("full_name", customer_data.get("username", "Unknown"))
            },
            new_values={
                "customer_id": customer_data.get("customer_id"),  # CUST-#####
                "username": customer_data.get("username"),
                "full_name": customer_data.get("full_name"),
                "email": customer_data.get("email"),
                "phone": customer_data.get("phone"),
                "loyalty_points": customer_data.get("loyalty_points", 0),
                "membership_level": customer_data.get("membership_level", "standard")
            },
            metadata={"action": "create", "module": "customers"}
        )

    # ========================================
    # SYSTEM & SESSIONS
    # ========================================
    
    # SESS-##### (5 digits - user sessions)
    def log_session_create(self, user_data, session_data):
        """Log session creation - SESS-##### format"""
        return self._create_audit_log(
            event_type="session_create",
            user_data=user_data,
            target_data={
                "type": "session",
                "id": session_data.get("session_id", "Unknown"),  # SESS-#####
                "name": f"Session #{session_data.get('session_id', 'Unknown')}"
            },
            new_values={
                "session_id": session_data.get("session_id"),  # SESS-#####
                "user_id": session_data.get("user_id"),  # USER-####
                "login_time": str(session_data.get("login_time", "")),
                "ip_address": session_data.get("ip_address"),
                "user_agent": session_data.get("user_agent"),
                "branch_id": session_data.get("branch_id")
            },
            metadata={"action": "create", "module": "sessions"}
        )
    
    def log_session_end(self, user_data, session_data, session_duration):
        """Log session termination"""
        return self._create_audit_log(
            event_type="session_end",
            user_data=user_data,
            target_data={
                "type": "session",
                "id": session_data.get("session_id", "Unknown"),  # SESS-#####
                "name": f"Session #{session_data.get('session_id', 'Unknown')}"
            },
            old_values={
                "status": "active",
                "logout_time": None
            },
            new_values={
                "status": "ended",
                "logout_time": str(datetime.utcnow()),
                "session_duration": session_duration
            },
            metadata={
                "action": "end",
                "module": "sessions",
                "duration_minutes": round(session_duration / 60, 2)
            }
        )

    # ========================================
    # BULK OPERATIONS & SYSTEM EVENTS
    # ========================================
    
    def log_bulk_operation(self, user_data, operation_type, target_type, success_count, failure_count, target_ids=None):
        """Log bulk operations across any entity type"""
        return self._create_audit_log(
            event_type="bulk_operation",
            user_data=user_data,
            target_data={
                "type": target_type,
                "id": "bulk_operation",
                "name": f"Bulk {operation_type.title()} - {target_type.title()}"
            },
            metadata={
                "action": "bulk_operation",
                "module": target_type,
                "operation_type": operation_type,  # delete, update, import
                "success_count": success_count,
                "failure_count": failure_count,
                "total_count": success_count + failure_count,
                "success_rate": round((success_count / (success_count + failure_count)) * 100, 2) if (success_count + failure_count) > 0 else 0,
                "target_ids": target_ids or []
            }
        )

    # ========================================
    # QUERY & REPORTING METHODS
    # ========================================
    
    def get_audit_logs_by_target(self, target_type, target_id, limit=50):
        """Get audit logs for specific entity"""
        try:
            logs = list(
                self.collection.find({
                    "target_type": target_type,
                    "target_id": target_id
                })
                .sort("timestamp", -1)
                .limit(limit)
            )
            
            return {
                'success': True,
                'data': [self.convert_object_id(log) for log in logs],
                'count': len(logs)
            }
        except Exception as e:
            return {'success': False, 'error': str(e), 'data': []}
    
    def get_audit_logs_by_user(self, user_id, limit=100):
        """Get audit logs for specific user"""
        try:
            logs = list(
                self.collection.find({"user_id": user_id})
                .sort("timestamp", -1)
                .limit(limit)
            )
            
            return {
                'success': True,
                'data': [self.convert_object_id(log) for log in logs],
                'count': len(logs)
            }
        except Exception as e:
            return {'success': False, 'error': str(e), 'data': []}
    
    def get_audit_statistics(self):
        """Get audit log statistics"""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': '$event_type',
                        'count': {'$sum': 1},
                        'latest': {'$max': '$timestamp'}
                    }
                },
                {
                    '$sort': {'count': -1}
                }
            ]
            
            stats = list(self.collection.aggregate(pipeline))
            total_logs = sum(stat['count'] for stat in stats)
            
            return {
                'success': True,
                'total_logs': total_logs,
                'by_event_type': stats,
                'total_audit_id': self.generate_audit_id()  # Shows next ID
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
    def log_customer_update(self, user_data, customer_id, old_customer_data, new_customer_data):
        """Log customer update - CUST-##### format"""
        
        # Find what fields actually changed
        changed_fields = {}
        old_values = {}
        new_values = {}
        
        for key, new_value in new_customer_data.items():
            if key in old_customer_data:
                old_value = old_customer_data[key]
                if old_value != new_value:
                    old_values[key] = old_value
                    new_values[key] = new_value
                    changed_fields[key] = {"old": old_value, "new": new_value}
        
        return self._create_audit_log(
            event_type="customer_update",
            user_data=user_data,
            target_data={
                "type": "customer",
                "id": customer_id,  # CUST-#####
                "name": old_customer_data.get("full_name", old_customer_data.get("username", "Unknown"))
            },
            old_values=old_values,
            new_values=new_values,
            metadata={
                "action": "update",
                "module": "customers",
                "fields_changed": list(changed_fields.keys()),
                "change_count": len(changed_fields)
            }
        )