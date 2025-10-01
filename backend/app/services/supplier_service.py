import re
from datetime import datetime
from ..database import db_manager
from ..models import Supplier
from notifications.services import NotificationService
import logging
from .audit_service import AuditLogService

logger = logging.getLogger(__name__)

class SupplierService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.supplier_collection = self.db.suppliers
        self.audit_service = AuditLogService()
        self.notification_service = NotificationService()
    
    def generate_supplier_id(self):
        """Generate sequential SUPP-### ID"""
        try:
            # Get the highest existing supplier ID number
            pipeline = [
                {'$match': {'_id': {'$regex': r'^SUPP-\d{3}$'}}},
                {'$project': {
                    'id_number': {
                        '$toInt': {
                            '$substr': ['$_id', 5, -1]  # Extract number after "SUPP-"
                        }
                    }
                }},
                {'$sort': {'id_number': -1}},
                {'$limit': 1}
            ]
            
            result = list(self.supplier_collection.aggregate(pipeline))
            next_number = (result[0]['id_number'] + 1) if result else 1
            
            return f"SUPP-{next_number:03d}"
        
        except Exception:
            # Fallback: count all suppliers + 1
            count = self.supplier_collection.count_documents({}) + 1
            return f"SUPP-{count:03d}"
    
    def add_sync_log(self, source='cloud', status='synced', details=None):
        """Helper method to create sync log entries"""
        return {
            'last_updated': datetime.utcnow(),
            'source': source,
            'status': status,
            'details': details or {}
        }
    
    def validate_supplier_data(self, supplier_data):
        """Validate supplier data before creation/update"""
        required_fields = ['supplier_name']
        
        for field in required_fields:
            if not supplier_data.get(field):
                raise ValueError(f"Required field '{field}' is missing or empty")
        
        # Validate email format if provided
        if supplier_data.get('email'):
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, supplier_data['email']):
                raise ValueError("Invalid email format")
        
        # Validate phone number if provided (basic validation)
        if supplier_data.get('phone_number'):
            phone = supplier_data['phone_number'].strip()
            if len(phone) < 10:
                raise ValueError("Phone number must be at least 10 digits")
    
    def _send_supplier_notification(self, action_type, supplier_name, supplier_id=None):
        """Centralized notification helper for supplier actions"""
        try:
            titles = {
                'created': "New Supplier Added",
                'updated': "Supplier Updated", 
                'contact_updated': "Supplier Contact Updated",
                'soft_deleted': "Supplier Deleted",
                'hard_deleted': "Supplier Permanently Deleted",
                'restored': "Supplier Restored",
                'purchase_order_added': "Purchase Order Added",
                'purchase_order_updated': "Purchase Order Updated",
                'purchase_order_soft_deleted': "Purchase Order Deleted",
                'purchase_order_hard_deleted': "Purchase Order Permanently Deleted",
                'purchase_order_restored': "Purchase Order Restored"
            }
            
            messages = {
                'created': f"Supplier '{supplier_name}' has been added to the system",
                'updated': f"Supplier '{supplier_name}' has been updated",
                'contact_updated': f"Contact information for '{supplier_name}' has been updated",
                'soft_deleted': f"Supplier '{supplier_name}' has been moved to trash",
                'hard_deleted': f"Supplier '{supplier_name}' has been permanently removed",
                'restored': f"Supplier '{supplier_name}' has been restored from trash",
                'purchase_order_added': f"New purchase order added for supplier '{supplier_name}'",
                'purchase_order_updated': f"Purchase order updated for supplier '{supplier_name}'",
                'purchase_order_soft_deleted': f"Purchase order deleted for supplier '{supplier_name}' (can be restored)",
                'purchase_order_hard_deleted': f"Purchase order permanently removed for supplier '{supplier_name}'",
                'purchase_order_restored': f"Purchase order restored for supplier '{supplier_name}'"
            }
            
            if action_type in titles:
                priority = "high" if 'hard_deleted' in action_type else ("medium" if 'deleted' in action_type else "low")
                
                self.notification_service.create_notification(
                    title=titles[action_type],
                    message=messages[action_type],
                    priority=priority,
                    notification_type="system",
                    metadata={
                        "supplier_id": str(supplier_id) if supplier_id else "",
                        "supplier_name": supplier_name,
                        "action_type": f"supplier_{action_type}"
                    }
                )
        except Exception as e:
            logger.error(f"Failed to send supplier notification: {e}")
    
    def _log_audit(self, action, supplier_id, supplier_name, user_id='system', details=None):
        """Helper method to log audit trail"""
        try:
            self.audit_service.log_action(
                action=action,
                resource_type='supplier',
                resource_id=supplier_id,
                user_id=user_id,
                changes=None,  # You can pass changes here if needed
                metadata={
                    'supplier_name': supplier_name,
                    **(details or {})
                }
            )
        except Exception as e:
            logger.error(f"Failed to log audit action: {e}")

    def create_supplier(self, supplier_data, user_id='system'):
        """Create a new supplier"""
        try:
            # Validate supplier data
            self.validate_supplier_data(supplier_data)
            
            # Generate supplier ID
            if not supplier_data.get('_id'):
                supplier_data['_id'] = self.generate_supplier_id()
            
            # Check for duplicate supplier name
            existing_supplier = self.supplier_collection.find_one({
                'supplier_name': {'$regex': f'^{re.escape(supplier_data["supplier_name"])}$', '$options': 'i'},
                'isDeleted': {'$ne': True}
            })
            if existing_supplier:
                raise ValueError(f"Supplier with name '{supplier_data['supplier_name']}' already exists")
            
            # Set default values
            current_time = datetime.utcnow()
            supplier_data.update({
                'isDeleted': False,
                'created_at': current_time,
                'updated_at': current_time,
                'created_by': user_id,
                'purchase_orders': [],  # Initialize empty purchase orders array
                'sync_logs': [
                    self.add_sync_log(source='cloud', status='pending', details={'action': 'created'})
                ]
            })
            
            # Insert supplier
            result = self.supplier_collection.insert_one(supplier_data)
            
            # Log audit trail
            self._log_audit(
                action='supplier_created',
                supplier_id=supplier_data['_id'],
                supplier_name=supplier_data['supplier_name'],
                user_id=user_id
            )
            
            # Send notification
            self._send_supplier_notification('created', supplier_data['supplier_name'], supplier_data['_id'])
            
            # Return created supplier
            return self.supplier_collection.find_one({'_id': supplier_data['_id']})
        
        except Exception as e:
            raise Exception(f"Error creating supplier: {str(e)}")
        
    def add_purchase_order(self, supplier_id, order_data, user_id='system'):
        """Add a purchase order to a supplier"""
        try:
            if not supplier_id or not isinstance(supplier_id, str):
                raise ValueError("Invalid supplier ID")
            
            # Check if supplier exists
            supplier = self.get_supplier_by_id(supplier_id, include_deleted=False)
            if not supplier:
                raise Exception(f"Supplier with ID {supplier_id} not found or is deleted")
            
            # Validate required order fields
            required_fields = ['order_id', 'items']
            for field in required_fields:
                if not order_data.get(field):
                    raise ValueError(f"Required field '{field}' is missing from order data")
            
            # Validate items array
            if not isinstance(order_data['items'], list) or len(order_data['items']) == 0:
                raise ValueError("Order must contain at least one item")
            
            # Validate each item
            for i, item in enumerate(order_data['items']):
                if not item.get('product_id'):
                    raise ValueError(f"Item {i+1} is missing product_id")
                if not item.get('quantity') or item['quantity'] <= 0:
                    raise ValueError(f"Item {i+1} must have a positive quantity")
                if not item.get('unit_price') or item['unit_price'] <= 0:
                    raise ValueError(f"Item {i+1} must have a positive unit price")
            
            # Calculate total cost if not provided
            if 'total_cost' not in order_data:
                total_cost = sum(item['quantity'] * item['unit_price'] for item in order_data['items'])
                order_data['total_cost'] = total_cost
            
            # Set default order values
            current_time = datetime.utcnow()
            order_data.update({
                'status': order_data.get('status', 'pending'),
                'order_date': order_data.get('order_date', current_time),
                'created_at': current_time,
                'updated_at': current_time,
                'created_by': user_id,
                'isDeleted': False
            })
            
            # Add purchase order to supplier
            result = self.supplier_collection.update_one(
                {'_id': supplier_id, 'isDeleted': {'$ne': True}},
                {
                    '$push': {'purchase_orders': order_data},
                    '$set': {'updated_at': current_time}
                }
            )
            
            if result.modified_count > 0:
                # Log audit trail
                self._log_audit(
                    action='purchase_order_added',
                    supplier_id=supplier_id,
                    supplier_name=supplier['supplier_name'],
                    user_id=user_id,
                    details={'order_id': order_data['order_id']}
                )
                
                # Send notification
                self._send_supplier_notification('purchase_order_added', supplier['supplier_name'], supplier_id)
                
                # Return updated supplier
                return self.supplier_collection.find_one({'_id': supplier_id})
            
            return None
        
        except Exception as e:
            raise Exception(f"Error adding purchase order: {str(e)}")
    
    def update_purchase_order(self, supplier_id, order_id, update_data, user_id='system'):
        """Update a specific purchase order for a supplier"""
        try:
            if not supplier_id or not isinstance(supplier_id, str):
                raise ValueError("Invalid supplier ID")
            
            if not order_id:
                raise ValueError("Order ID is required")
            
            # Check if supplier exists
            supplier = self.get_supplier_by_id(supplier_id, include_deleted=False)
            if not supplier:
                raise Exception(f"Supplier with ID {supplier_id} not found or is deleted")
            
            # Find the order in the purchase_orders array
            order_found = False
            for order in supplier.get('purchase_orders', []):
                if order.get('order_id') == order_id and not order.get('isDeleted', False):
                    order_found = True
                    break
            
            if not order_found:
                raise Exception(f"Purchase order with ID {order_id} not found for supplier {supplier_id}")
            
            # Prepare update data
            current_time = datetime.utcnow()
            update_data['updated_at'] = current_time
            update_data['updated_by'] = user_id
            
            # Recalculate total if items are updated
            if 'items' in update_data:
                if isinstance(update_data['items'], list):
                    total_cost = sum(item.get('quantity', 0) * item.get('unit_price', 0) for item in update_data['items'])
                    update_data['total_cost'] = total_cost
            
            # Update the specific purchase order
            update_fields = {}
            for key, value in update_data.items():
                update_fields[f'purchase_orders.$.{key}'] = value
            
            result = self.supplier_collection.update_one(
                {
                    '_id': supplier_id, 
                    'purchase_orders.order_id': order_id,
                    'isDeleted': {'$ne': True}
                },
                {
                    '$set': {
                        **update_fields,
                        'updated_at': current_time
                    }
                }
            )
            
            if result.modified_count > 0:
                # Log audit trail
                self._log_audit(
                    action='purchase_order_updated',
                    supplier_id=supplier_id,
                    supplier_name=supplier['supplier_name'],
                    user_id=user_id,
                    details={'order_id': order_id}
                )
                
                # Send notification
                self._send_supplier_notification('purchase_order_updated', supplier['supplier_name'], supplier_id)
                
                # Return updated supplier
                return self.supplier_collection.find_one({'_id': supplier_id})
            
            return None
        
        except Exception as e:
            raise Exception(f"Error updating purchase order: {str(e)}")
    
    def get_purchase_orders(self, supplier_id, status=None, include_deleted=False):
        """
        Get purchase orders for a specific supplier
        
        Args:
            supplier_id: Supplier's string ID
            status: Filter by order status (optional)
            include_deleted: Include soft-deleted orders (default: False)
        
        Returns:
            List of purchase orders
        """
        try:
            if not supplier_id or not isinstance(supplier_id, str):
                raise ValueError("Invalid supplier ID")
            
            supplier = self.get_supplier_by_id(supplier_id, include_deleted=False)
            if not supplier:
                return []
            
            orders = supplier.get('purchase_orders', [])
            
            # Filter by deletion status
            if not include_deleted:
                orders = [order for order in orders if not order.get('isDeleted', False)]
            
            # Filter by status if provided
            if status:
                orders = [order for order in orders if order.get('status') == status]
            
            # Sort by order date (newest first)
            orders.sort(key=lambda x: x.get('order_date', datetime.min), reverse=True)
            
            return orders
        
        except Exception as e:
            raise Exception(f"Error getting purchase orders: {str(e)}")
    
    def get_purchase_order_by_id(self, supplier_id, order_id):
        """Get a specific purchase order by ID"""
        try:
            orders = self.get_purchase_orders(supplier_id, include_deleted=False)
            
            for order in orders:
                if order.get('order_id') == order_id:
                    return order
            
            return None
        
        except Exception as e:
            raise Exception(f"Error getting purchase order: {str(e)}")
    
    def get_suppliers(self, filters=None, include_deleted=False, page=1, per_page=50):
        """Get suppliers with optional filters and pagination"""
        try:
            query = {}
            
            # By default, exclude deleted suppliers
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
            
            if filters:
                # Search filter
                if filters.get('search'):
                    search_regex = {'$regex': filters['search'], '$options': 'i'}
                    query['$or'] = [
                        {'supplier_name': search_regex},
                        {'contact_person': search_regex},
                        {'email': search_regex},
                        {'_id': search_regex}
                    ]
                
                # Status filter (for future use if needed)
                if filters.get('status'):
                    query['status'] = filters['status']
            
            # Calculate pagination
            skip = (page - 1) * per_page
            
            # Get total count for pagination info
            total_count = self.supplier_collection.count_documents(query)
            
            # Get suppliers with pagination
            suppliers = list(
                self.supplier_collection.find(query)
                .sort('supplier_name', 1)
                .skip(skip)
                .limit(per_page)
            )
            
            return {
                'suppliers': suppliers,
                'pagination': {
                    'current_page': page,
                    'per_page': per_page,
                    'total_count': total_count,
                    'total_pages': (total_count + per_page - 1) // per_page
                }
            }
        
        except Exception as e:
            raise Exception(f"Error getting suppliers: {str(e)}")
    
    def get_supplier_by_id(self, supplier_id, include_deleted=False):
        """Get supplier by ID"""
        try:
            if not supplier_id or not isinstance(supplier_id, str):
                return None
            
            query = {'_id': supplier_id}
            
            if not include_deleted:
                query['isDeleted'] = {'$ne': True}
            
            return self.supplier_collection.find_one(query)
        
        except Exception as e:
            raise Exception(f"Error getting supplier: {str(e)}")
    
    def update_supplier(self, supplier_id, supplier_data, user_id='system'):
        """Update supplier"""
        try:
            if not supplier_id or not isinstance(supplier_id, str):
                raise ValueError("Invalid supplier ID")
            
            # Check if supplier exists and is not deleted
            existing_supplier = self.get_supplier_by_id(supplier_id, include_deleted=False)
            if not existing_supplier:
                raise Exception(f"Supplier with ID {supplier_id} not found or is deleted")
            
            # Validate updated data
            self.validate_supplier_data(supplier_data)
            
            # Check for duplicate name (excluding current supplier)
            if 'supplier_name' in supplier_data:
                existing_name = self.supplier_collection.find_one({
                    'supplier_name': {'$regex': f'^{re.escape(supplier_data["supplier_name"])}$', '$options': 'i'},
                    '_id': {'$ne': supplier_id},
                    'isDeleted': {'$ne': True}
                })
                if existing_name:
                    raise ValueError(f"Supplier with name '{supplier_data['supplier_name']}' already exists")
            
            # Add updated timestamp and user
            supplier_data['updated_at'] = datetime.utcnow()
            supplier_data['updated_by'] = user_id
            
            # Update supplier
            result = self.supplier_collection.update_one(
                {'_id': supplier_id, 'isDeleted': {'$ne': True}},
                {'$set': supplier_data}
            )
            
            if result.modified_count > 0:
                updated_supplier = self.supplier_collection.find_one({'_id': supplier_id})
                
                # Log audit trail
                self._log_audit(
                    action='supplier_updated',
                    supplier_id=supplier_id,
                    supplier_name=updated_supplier['supplier_name'],
                    user_id=user_id
                )
                
                # Send notification
                self._send_supplier_notification('updated', updated_supplier['supplier_name'], supplier_id)
                
                return updated_supplier
            
            return None
        
        except Exception as e:
            raise Exception(f"Error updating supplier: {str(e)}")
    
    def delete_supplier(self, supplier_id, hard_delete=False, user_id='system'):
        """Soft delete or hard delete a supplier"""
        try:
            if not supplier_id or not isinstance(supplier_id, str):
                return False
            
            # Get supplier details before deletion
            supplier_to_delete = self.supplier_collection.find_one({'_id': supplier_id})
            if not supplier_to_delete:
                return False
            
            if hard_delete:
                # Hard delete - permanently remove
                result = self.supplier_collection.delete_one({'_id': supplier_id})
                
                if result.deleted_count > 0:
                    # Log audit trail
                    self._log_audit(
                        action='supplier_hard_deleted',
                        supplier_id=supplier_id,
                        supplier_name=supplier_to_delete['supplier_name'],
                        user_id=user_id
                    )
                    
                    # Send notification
                    self._send_supplier_notification('hard_deleted', supplier_to_delete['supplier_name'], supplier_id)
                    
                    return True
                return False
            else:
                # Soft delete
                current_time = datetime.utcnow()
                deletion_log = {
                    'deleted_at': current_time,
                    'deleted_by': user_id,
                    'reason': 'Manual deletion'
                }
                
                result = self.supplier_collection.update_one(
                    {'_id': supplier_id, 'isDeleted': {'$ne': True}},
                    {
                        '$set': {
                            'isDeleted': True,
                            'updated_at': current_time,
                            'deletion_log': deletion_log
                        }
                    }
                )
                
                if result.modified_count > 0:
                    # Log audit trail
                    self._log_audit(
                        action='supplier_soft_deleted',
                        supplier_id=supplier_id,
                        supplier_name=supplier_to_delete['supplier_name'],
                        user_id=user_id
                    )
                    
                    # Send notification
                    self._send_supplier_notification('soft_deleted', supplier_to_delete['supplier_name'], supplier_id)
                    
                    return True
                
                return False
        
        except Exception as e:
            raise Exception(f"Error deleting supplier: {str(e)}")
    
    def restore_supplier(self, supplier_id, user_id='system'):
        """Restore a soft-deleted supplier"""
        try:
            if not supplier_id or not isinstance(supplier_id, str):
                return False
            
            current_time = datetime.utcnow()
            restoration_log = {
                'restored_at': current_time,
                'restored_by': user_id,
                'reason': 'Manual restoration'
            }
            
            result = self.supplier_collection.update_one(
                {'_id': supplier_id, 'isDeleted': True},
                {
                    '$set': {
                        'isDeleted': False,
                        'updated_at': current_time,
                        'restoration_log': restoration_log
                    },
                    '$unset': {
                        'deletion_log': 1
                    }
                }
            )
            
            if result.modified_count > 0:
                restored_supplier = self.supplier_collection.find_one({'_id': supplier_id})
                
                # Log audit trail
                self._log_audit(
                    action='supplier_restored',
                    supplier_id=supplier_id,
                    supplier_name=restored_supplier['supplier_name'],
                    user_id=user_id
                )
                
                # Send notification
                self._send_supplier_notification('restored', restored_supplier['supplier_name'], supplier_id)
                
                return True
            
            return False
        
        except Exception as e:
            raise Exception(f"Error restoring supplier: {str(e)}")
    
    def get_deleted_suppliers(self, page=1, per_page=50):
        """Get all soft-deleted suppliers"""
        try:
            query = {'isDeleted': True}
            skip = (page - 1) * per_page
            
            total_count = self.supplier_collection.count_documents(query)
            
            suppliers = list(
                self.supplier_collection.find(query)
                .sort('deletion_log.deleted_at', -1)
                .skip(skip)
                .limit(per_page)
            )
            
            return {
                'suppliers': suppliers,
                'pagination': {
                    'current_page': page,
                    'per_page': per_page,
                    'total_count': total_count,
                    'total_pages': (total_count + per_page - 1) // per_page
                }
            }
        
        except Exception as e:
            raise Exception(f"Error getting deleted suppliers: {str(e)}")
        
    def delete_purchase_order(self, supplier_id, order_id, hard_delete=False, user_id='system'):
        """Soft delete or hard delete a purchase order"""
        try:
            if not supplier_id or not isinstance(supplier_id, str):
                raise ValueError("Invalid supplier ID")
            
            if not order_id:
                raise ValueError("Order ID is required")
            
            # Get supplier
            supplier = self.get_supplier_by_id(supplier_id, include_deleted=False)
            if not supplier:
                raise Exception(f"Supplier with ID {supplier_id} not found or is deleted")
            
            # Find the order in the purchase_orders array
            order_to_delete = None
            for order in supplier.get('purchase_orders', []):
                if order.get('order_id') == order_id and not order.get('isDeleted', False):
                    order_to_delete = order
                    break
            
            if not order_to_delete:
                raise Exception(f"Active purchase order with ID {order_id} not found for supplier {supplier_id}")
            
            current_time = datetime.utcnow()
            
            if hard_delete:
                # Hard delete - permanently remove from array
                result = self.supplier_collection.update_one(
                    {'_id': supplier_id, 'isDeleted': {'$ne': True}},
                    {
                        '$pull': {'purchase_orders': {'order_id': order_id}},
                        '$set': {'updated_at': current_time}
                    }
                )
                
                if result.modified_count > 0:
                    # Log audit trail
                    self._log_audit(
                        action='purchase_order_hard_deleted',
                        supplier_id=supplier_id,
                        supplier_name=supplier['supplier_name'],
                        user_id=user_id,
                        details={'order_id': order_id}
                    )
                    
                    # Send notification
                    self._send_supplier_notification('purchase_order_hard_deleted', supplier['supplier_name'], supplier_id)
                    return True
                return False
            
            else:
                # Soft delete - mark as deleted with timestamp
                deletion_log = {
                    'deleted_at': current_time,
                    'deleted_by': user_id,
                    'reason': 'Manual deletion'
                }
                
                result = self.supplier_collection.update_one(
                    {
                        '_id': supplier_id, 
                        'purchase_orders.order_id': order_id,
                        'isDeleted': {'$ne': True}
                    },
                    {
                        '$set': {
                            'purchase_orders.$.isDeleted': True,
                            'purchase_orders.$.deletion_log': deletion_log,
                            'purchase_orders.$.updated_at': current_time,
                            'updated_at': current_time
                        }
                    }
                )
                
                if result.modified_count > 0:
                    # Log audit trail
                    self._log_audit(
                        action='purchase_order_soft_deleted',
                        supplier_id=supplier_id,
                        supplier_name=supplier['supplier_name'],
                        user_id=user_id,
                        details={'order_id': order_id}
                    )
                    
                    # Send notification
                    self._send_supplier_notification('purchase_order_soft_deleted', supplier['supplier_name'], supplier_id)
                    return True
                return False
        
        except Exception as e:
            raise Exception(f"Error deleting purchase order: {str(e)}")

    def restore_purchase_order(self, supplier_id, order_id, user_id='system'):
        """Restore a soft-deleted purchase order"""
        try:
            if not supplier_id or not isinstance(supplier_id, str):
                raise ValueError("Invalid supplier ID")
            
            if not order_id:
                raise ValueError("Order ID is required")
            
            # Get supplier
            supplier = self.get_supplier_by_id(supplier_id, include_deleted=False)
            if not supplier:
                raise Exception(f"Supplier with ID {supplier_id} not found or is deleted")
            
            # Find the deleted order
            order_found = False
            for order in supplier.get('purchase_orders', []):
                if order.get('order_id') == order_id and order.get('isDeleted', False):
                    order_found = True
                    break
            
            if not order_found:
                raise Exception(f"Deleted purchase order with ID {order_id} not found for supplier {supplier_id}")
            
            current_time = datetime.utcnow()
            restoration_log = {
                'restored_at': current_time,
                'restored_by': user_id,
                'reason': 'Manual restoration'
            }
            
            result = self.supplier_collection.update_one(
                {
                    '_id': supplier_id,
                    'purchase_orders.order_id': order_id,
                    'purchase_orders.isDeleted': True,
                    'isDeleted': {'$ne': True}
                },
                {
                    '$set': {
                        'purchase_orders.$.isDeleted': False,
                        'purchase_orders.$.restoration_log': restoration_log,
                        'purchase_orders.$.updated_at': current_time,
                        'updated_at': current_time
                    },
                    '$unset': {
                        'purchase_orders.$.deletion_log': 1
                    }
                }
            )
            
            if result.modified_count > 0:
                # Log audit trail
                self._log_audit(
                    action='purchase_order_restored',
                    supplier_id=supplier_id,
                    supplier_name=supplier['supplier_name'],
                    user_id=user_id,
                    details={'order_id': order_id}
                )
                
                # Send notification
                self._send_supplier_notification('purchase_order_restored', supplier['supplier_name'], supplier_id)
                return True
            
            return False
        
        except Exception as e:
            raise Exception(f"Error restoring purchase order: {str(e)}")

    def get_deleted_purchase_orders(self, supplier_id):
        """Get all soft-deleted purchase orders for a supplier"""
        try:
            if not supplier_id or not isinstance(supplier_id, str):
                raise ValueError("Invalid supplier ID")
            
            # Get supplier
            supplier = self.get_supplier_by_id(supplier_id, include_deleted=False)
            if not supplier:
                return []
            
            # Filter for deleted orders
            deleted_orders = [
                order for order in supplier.get('purchase_orders', [])
                if order.get('isDeleted', False)
            ]
            
            # Sort by deletion date (newest first)
            deleted_orders.sort(
                key=lambda x: x.get('deletion_log', {}).get('deleted_at', datetime.min), 
                reverse=True
            )
            
            return deleted_orders
        
        except Exception as e:
            raise Exception(f"Error getting deleted purchase orders: {str(e)}")