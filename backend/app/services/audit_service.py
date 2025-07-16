# ========================================
# NEW FILE: audit_service.py
# Add this as a separate file alongside your existing session_service.py
# ========================================

from datetime import datetime
from bson import ObjectId
from ..database import db_manager

class AuditLogService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.collection = self.db.audit_logs  # NEW collection for audit logs
    
    def convert_object_id(self, document):
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    def _create_audit_log(self, event_type, user_data, target_data=None, old_values=None, new_values=None, metadata=None):
        """Create a standardized audit log entry"""
        try:
            audit_data = {
                "event_type": event_type,
                "user_id": ObjectId(user_data["user_id"]) if isinstance(user_data.get("user_id"), str) else user_data.get("user_id"),
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
                    "target_id": target_data.get("id"),
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
            return {"audit_id": str(result.inserted_id)}
            
        except Exception as e:
            raise Exception(f"Error creating audit log: {str(e)}")
    
    # ========================================
    # CUSTOMER AUDIT METHODS
    # ========================================
    
    def log_customer_create(self, user_data, customer_data):
        """Log customer creation"""
        return self._create_audit_log(
            event_type="customer_create",
            user_data=user_data,
            target_data={
                "type": "customer",
                "id": str(customer_data.get("_id", customer_data.get("customer_id", ""))),
                "name": customer_data.get("full_name", customer_data.get("username", "Unknown"))
            },
            new_values={
                "username": customer_data.get("username"),
                "full_name": customer_data.get("full_name"),
                "email": customer_data.get("email"),
                "phone": customer_data.get("phone"),
                "loyalty_points": customer_data.get("loyalty_points", 0)
            },
            metadata={"action": "create"}
        )
    
    def log_customer_update(self, user_data, customer_id, old_values, new_values):
        """Log customer update"""
        return self._create_audit_log(
            event_type="customer_update",
            user_data=user_data,
            target_data={
                "type": "customer",
                "id": str(customer_id),
                "name": old_values.get("full_name", old_values.get("username", "Unknown"))
            },
            old_values=old_values,
            new_values=new_values,
            metadata={"action": "update"}
        )
    
    def log_customer_delete(self, user_data, customer_data):
        """Log customer deletion"""
        return self._create_audit_log(
            event_type="customer_delete",
            user_data=user_data,
            target_data={
                "type": "customer",
                "id": str(customer_data.get("_id", customer_data.get("customer_id", ""))),
                "name": customer_data.get("full_name", customer_data.get("username", "Unknown"))
            },
            old_values=customer_data,
            metadata={"action": "delete"}
        )
    
    def log_customer_bulk_delete(self, user_data, deleted_count, deleted_ids):
        """Log bulk customer deletion"""
        return self._create_audit_log(
            event_type="customer_bulk_delete",
            user_data=user_data,
            target_data={
                "type": "customer",
                "id": "bulk_operation",
                "name": f"{deleted_count} customers"
            },
            metadata={
                "action": "bulk_delete",
                "count": deleted_count,
                "deleted_ids": deleted_ids
            }
        )
    
    # ========================================
    # CATEGORY AUDIT METHODS
    # ========================================
    
    def log_category_create(self, user_data, category_data):
        """Log category creation"""
        return self._create_audit_log(
            event_type="category_create",
            user_data=user_data,
            target_data={
                "type": "category",
                "id": str(category_data.get("_id", category_data.get("category_id", ""))),
                "name": category_data.get("category_name", category_data.get("name", "Unknown"))
            },
            new_values={
                "name": category_data.get("category_name", category_data.get("name")),
                "description": category_data.get("description"),
                "subcategories": category_data.get("subcategories", [])
            },
            metadata={"action": "create"}
        )
    
    def log_category_update(self, user_data, category_id, old_values, new_values):
        """Log category update"""
        return self._create_audit_log(
            event_type="category_update",
            user_data=user_data,
            target_data={
                "type": "category",
                "id": str(category_id),
                "name": old_values.get("category_name", old_values.get("name", "Unknown"))
            },
            old_values=old_values,
            new_values=new_values,
            metadata={"action": "update"}
        )
    
    def log_category_delete(self, user_data, category_data):
        """Log category deletion"""
        return self._create_audit_log(
            event_type="category_delete",
            user_data=user_data,
            target_data={
                "type": "category",
                "id": str(category_data.get("_id", category_data.get("category_id", ""))),
                "name": category_data.get("category_name", category_data.get("name", "Unknown"))
            },
            old_values=category_data,
            metadata={"action": "delete"}
        )
    
    # ========================================
    # PRODUCT AUDIT METHODS
    # ========================================
    
    def log_product_create(self, user_data, product_data):
        """Log product creation"""
        return self._create_audit_log(
            event_type="product_create",
            user_data=user_data,
            target_data={
                "type": "product",
                "id": str(product_data.get("_id", product_data.get("product_id", ""))),
                "name": product_data.get("product_name", product_data.get("name", "Unknown"))
            },
            new_values={
                "name": product_data.get("product_name", product_data.get("name")),
                "category": product_data.get("category"),
                "price": product_data.get("price"),
                "stock_quantity": product_data.get("stock_quantity", 0),
                "description": product_data.get("description")
            },
            metadata={"action": "create"}
        )
    
    def log_product_update(self, user_data, product_id, old_values, new_values):
        """Log product update"""
        return self._create_audit_log(
            event_type="product_update",
            user_data=user_data,
            target_data={
                "type": "product",
                "id": str(product_id),
                "name": old_values.get("product_name", old_values.get("name", "Unknown"))
            },
            old_values=old_values,
            new_values=new_values,
            metadata={"action": "update"}
        )
    
    def log_product_delete(self, user_data, product_data):
        """Log product deletion"""
        return self._create_audit_log(
            event_type="product_delete",
            user_data=user_data,
            target_data={
                "type": "product",
                "id": str(product_data.get("_id", product_data.get("product_id", ""))),
                "name": product_data.get("product_name", product_data.get("name", "Unknown"))
            },
            old_values=product_data,
            metadata={"action": "delete"}
        )
    
    def log_product_stock_update(self, user_data, product_id, product_name, old_stock, new_stock, reason="manual"):
        """Log product stock update"""
        return self._create_audit_log(
            event_type="product_stock_update",
            user_data=user_data,
            target_data={
                "type": "product",
                "id": str(product_id),
                "name": product_name
            },
            old_values={"stock_quantity": old_stock},
            new_values={"stock_quantity": new_stock},
            metadata={
                "action": "stock_update",
                "difference": new_stock - old_stock,
                "reason": reason
            }
        )
    
    # ========================================
    # USER AUDIT METHODS
    # ========================================
    
    def log_user_create(self, admin_user, new_user_data):
        """Log user creation"""
        return self._create_audit_log(
            event_type="user_create",
            user_data=admin_user,
            target_data={
                "type": "user",
                "id": str(new_user_data.get("_id", new_user_data.get("user_id", ""))),
                "name": new_user_data.get("username", new_user_data.get("email", "Unknown"))
            },
            new_values={
                "username": new_user_data.get("username"),
                "email": new_user_data.get("email"),
                "role": new_user_data.get("role"),
                "status": new_user_data.get("status", "active")
            },
            metadata={"action": "create"}
        )
    
    def log_user_update(self, admin_user, user_id, old_values, new_values):
        """Log user update"""
        return self._create_audit_log(
            event_type="user_update",
            user_data=admin_user,
            target_data={
                "type": "user",
                "id": str(user_id),
                "name": old_values.get("username", old_values.get("email", "Unknown"))
            },
            old_values=old_values,
            new_values=new_values,
            metadata={"action": "update"}
        )
    
    def log_user_delete(self, admin_user, deleted_user_data):
        """Log user deletion"""
        return self._create_audit_log(
            event_type="user_delete",
            user_data=admin_user,
            target_data={
                "type": "user",
                "id": str(deleted_user_data.get("_id", deleted_user_data.get("user_id", ""))),
                "name": deleted_user_data.get("username", deleted_user_data.get("email", "Unknown"))
            },
            old_values=deleted_user_data,
            metadata={"action": "delete"}
        )
    
    # ========================================
    # SYSTEM AUDIT METHODS
    # ========================================
    
    def log_data_export(self, user_data, export_type, record_count=0, filename=None):
        """Log data export"""
        return self._create_audit_log(
            event_type="data_export",
            user_data=user_data,
            target_data={
                "type": "system",
                "id": f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "name": f"{export_type.title()} Export"
            },
            metadata={
                "action": "export",
                "export_type": export_type,
                "record_count": record_count,
                "filename": filename,
                "format": "CSV"
            }
        )
    
    def log_data_import(self, user_data, import_type, success_count=0, failure_count=0, filename=None):
        """Log data import"""
        return self._create_audit_log(
            event_type="data_import",
            user_data=user_data,
            target_data={
                "type": "system",
                "id": f"import_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "name": f"{import_type.title()} Import"
            },
            metadata={
                "action": "import",
                "import_type": import_type,
                "success_count": success_count,
                "failure_count": failure_count,
                "total_count": success_count + failure_count,
                "filename": filename,
                "success_rate": round((success_count / (success_count + failure_count)) * 100, 2) if (success_count + failure_count) > 0 else 0
            }
        )
    
    def log_login_failed(self, username, ip_address=None, reason="invalid_credentials"):
        """Log failed login attempts"""
        return self._create_audit_log(
            event_type="login_failed",
            user_data={
                "username": username,
                "ip_address": ip_address,
                "user_id": None,
                "branch_id": None
            },
            target_data={
                "type": "authentication",
                "id": "login_attempt",
                "name": f"Failed login for {username}"
            },
            metadata={
                "action": "login_failed",
                "reason": reason,
                "attempted_username": username
            }
        )

# ========================================
# ENHANCED DISPLAY SERVICE
# ========================================

class AuditLogDisplay:
    def __init__(self):
        self.db = db_manager.get_database()
        self.audit_collection = self.db.audit_logs
        self.session_collection = self.db.session_logs  # Your existing collection
    
    def convert_object_id(self, document):
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    def get_audit_logs(self, limit=100, event_type=None):
        """Get comprehensive audit logs"""
        try:
            filter_query = {}
            if event_type:
                filter_query["event_type"] = event_type
            
            audit_logs = list(
                self.audit_collection.find(filter_query)
                .sort("timestamp", -1)
                .limit(limit)
            )
            
            formatted_logs = []
            for i, log in enumerate(audit_logs):
                log = self.convert_object_id(log)
                print(f"🔍 Audit log {i}: raw_username='{log.get('username')}', raw_user_id='{log.get('user_id')}'")
                
                formatted_log = {
                    "log_id": f"AUD-{i+1:04d}",
                    "user_id": log.get('username', 'Unknown'),  # ✅ Same as session logs
                    "ref_id": log.get('_id', '')[:12],
                    "event_type": log.get('event_type', 'Unknown').replace('_', ' ').title(),
                    "amount_qty": self._format_audit_amount(log),
                    "status": log.get('status', 'Unknown').title(),
                    "timestamp": str(log.get('timestamp', '')),
                    "remarks": self._format_audit_remarks(log),
                    "log_source": "audit"
                }
                formatted_logs.append(formatted_log)
            
            return {
                'success': True,
                'data': formatted_logs,
                'total_count': len(formatted_logs)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
    
    def get_combined_logs(self, limit=100):
        """Get logs with continuous numbering by type (never resets)"""
        try:
            # ✅ STEP 1: Fetch session logs
            session_cursor = self.collection.find().sort("login_time", -1)
            session_logs = list(session_cursor)
            
            # ✅ STEP 2: Fetch audit logs
            audit_logs = []
            try:
                audit_collection = self.db.audit_logs
                audit_cursor = audit_collection.find().sort("timestamp", -1)
                audit_logs = list(audit_cursor)
                print(f"✅ Fetched {len(audit_logs)} audit logs")
            except Exception as e:
                print(f"⚠️ No audit logs available: {e}")
                audit_logs = []
            
            # ✅ STEP 3: Create all logs with sorting keys
            all_logs = []
            
            # Add session logs
            for log in session_logs:
                log = self.convert_object_id(log)
                formatted_log = {
                    "user_id": log.get('username', 'Unknown'),
                    "ref_id": log.get('_id', '')[:12],
                    "event_type": "Session",
                    "amount_qty": f"{log.get('session_duration', 0)}s",
                    "status": log.get('status', 'Unknown').title(),
                    "timestamp": str(log.get('login_time', '')),
                    "remarks": f"Branch {log.get('branch_id', 'N/A')}",
                    "log_source": "session",
                    "sort_time": self._parse_timestamp(str(log.get('login_time', '')))
                }
                all_logs.append(formatted_log)
            
            # Add audit logs
            for log in audit_logs:
                log = self.convert_object_id(log)
                formatted_log = {
                    "user_id": log.get('username', 'Unknown'),
                    "ref_id": log.get('_id', '')[:12],
                    "event_type": log.get('event_type', 'Unknown').replace('_', ' ').title(),
                    "amount_qty": self._format_audit_amount(log),
                    "status": log.get('status', 'Unknown').title(),
                    "timestamp": str(log.get('timestamp', '')),
                    "remarks": self._format_audit_remarks(log),
                    "log_source": "audit",
                    "sort_time": self._parse_timestamp(str(log.get('timestamp', '')))
                }
                all_logs.append(formatted_log)
            
            # ✅ STEP 4: Sort all logs by timestamp (newest first)
            all_logs.sort(key=lambda x: x.get('sort_time', datetime.min), reverse=True)
            
            # ✅ STEP 5: Count totals first, then number backwards
            session_count = sum(1 for log in all_logs if log['log_source'] == 'session')
            audit_count = sum(1 for log in all_logs if log['log_source'] == 'audit')
            
            session_counter = session_count
            audit_counter = audit_count
            
            formatted_logs = []
            for log in all_logs[:limit]:
                log.pop('sort_time', None)
                
                if log['log_source'] == 'session':
                    log['log_id'] = f"SES-{session_counter:04d}"
                    session_counter -= 1
                else:
                    log['log_id'] = f"AUD-{audit_counter:04d}"
                    audit_counter -= 1
                
                formatted_logs.append(log)
            
            return {
                'success': True,
                'data': formatted_logs,
                'total_count': len(all_logs),
                'session_count': len(session_logs),
                'audit_count': len(audit_logs)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
    
    def _format_amount_qty(self, log):
        """Format amount/quantity based on event type"""
        event_type = log.get('event_type', '')
        
        if 'stock_update' in event_type:
            diff = log.get('metadata', {}).get('difference', 0)
            return f"{'+' if diff > 0 else ''}{diff} units"
        elif 'delete' in event_type:
            if log.get('metadata', {}).get('count'):
                count = log['metadata']['count']
                return f"{count} records"
            return "1 record"
        elif 'create' in event_type:
            return "1 record"
        elif 'export' in event_type:
            count = log.get('metadata', {}).get('record_count', 0)
            return f"{count} records"
        elif 'import' in event_type:
            success = log.get('metadata', {}).get('success_count', 0)
            total = log.get('metadata', {}).get('total_count', 0)
            return f"{success}/{total} records"
        
        return "N/A"
    
    def _format_remarks(self, log):
        """Format remarks based on event type"""
        target_type = log.get('target_type', 'System')
        target_name = log.get('target_name', 'N/A')
        
        if target_type and target_name and target_name != 'N/A':
            return f"{target_type.title()}: {target_name}"
        
        if log.get('event_type') == 'login_failed':
            reason = log.get('metadata', {}).get('reason', 'Unknown')
            return f"Failed: {reason}"
        
        return f"Branch {log.get('branch_id', 'N/A')}"

# ========================================
# HOW TO USE IN YOUR EXISTING SERVICES
# ========================================

"""
# In your existing customer service file, just add these imports and calls:

from .audit_service import AuditLogService

class CustomerService:
    def __init__(self):
        self.audit_service = AuditLogService()  # ADD THIS LINE
        # ... your existing init code
    
    def create_customer(self, customer_data, current_user):
        try:
            # Your existing customer creation code
            result = self.collection.insert_one(customer_data)
            customer_id = str(result.inserted_id)
            
            # ADD THESE 2 LINES
            customer_data["customer_id"] = customer_id
            self.audit_service.log_customer_create(current_user, customer_data)
            
            return {"success": True, "customer_id": customer_id}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_customer(self, customer_id, new_data, current_user):
        try:
            # ADD THIS LINE - get old data first
            old_customer = self.collection.find_one({"_id": ObjectId(customer_id)})
            
            # Your existing update code
            result = self.collection.update_one(
                {"_id": ObjectId(customer_id)},
                {"$set": new_data}
            )
            
            # ADD THIS LINE
            self.audit_service.log_customer_update(current_user, customer_id, old_customer, new_data)
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
"""