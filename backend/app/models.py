from django.db import models

# Create your models here.
from datetime import datetime
from typing import Optional, List
from bson import ObjectId

class User:
    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.username = kwargs.get('username', '')
        self.email = kwargs.get('email', '')
        self.password = kwargs.get('password', '')
        self.full_name = kwargs.get('full_name', '')
        self.role = kwargs.get('role', 'user')
        self.status = kwargs.get('status', 'active')
        self.date_created = kwargs.get('date_created', datetime.utcnow())
        self.last_updated = kwargs.get('last_updated', datetime.utcnow())
        self.last_login = kwargs.get('last_login')
        self.source = kwargs.get('source', 'system')

    def to_dict(self):
        return {
            '_id': self._id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'full_name': self.full_name,
            'role': self.role,
            'status': self.status,
            'date_created': self.date_created,
            'last_updated': self.last_updated,
            'last_login': self.last_login,
            'source': self.source
        }

class Customer:
    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.customer_id = kwargs.get('customer_id', str(self._id))
        self.full_name = kwargs.get('full_name', '')
        self.email = kwargs.get('email', '')
        self.phone = kwargs.get('phone', '')
        self.delivery_address = kwargs.get('delivery_address', {})
        self.loyalty_points = kwargs.get('loyalty_points', 0)
        self.last_purchase = kwargs.get('last_purchase')
        self.date_created = kwargs.get('date_created', datetime.utcnow())
        self.last_updated = kwargs.get('last_updated', datetime.utcnow())
        self.status = kwargs.get('status', 'active')
        self.source = kwargs.get('source', 'system')

    def to_dict(self):
        return {
            '_id': self._id,
            'customer_id': self.customer_id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'delivery_address': self.delivery_address,
            'loyalty_points': self.loyalty_points,
            'last_purchase': self.last_purchase,
            'date_created': self.date_created,
            'last_updated': self.last_updated,
            'status': self.status,
            'source': self.source
        }
    
class Product:
    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.product_name = kwargs.get('product_name', '')
        self.category_id = kwargs.get('category_id', None)
        self.supplier_id = kwargs.get('supplier_id', None)
        self.branch_id = kwargs.get('branch_id', None)
        self.unit = kwargs.get('unit', 'pcs')
        self.stock = kwargs.get('stock', 0)
        self.expiry_date = kwargs.get('expiry_date', None)
        self.low_stock_threshold = kwargs.get('low_stock_threshold', 10)
        self.cost_price = kwargs.get('cost_price', 0.0)
        self.selling_price = kwargs.get('selling_price', 0.0)
        self.date_received = kwargs.get('date_received', datetime.utcnow())
        self.status = kwargs.get('status', 'active')
        self.is_taxable = kwargs.get('is_taxable', True)
        self.SKU = kwargs.get('SKU', '')
        self.sync_logs = kwargs.get('sync_logs', [])

    def to_dict(self):
        return {
            '_id': self._id,
            'product_name': self.product_name,
            'category_id': self.category_id,
            'supplier_id': self.supplier_id,
            'branch_id': self.branch_id,
            'unit': self.unit,
            'stock': self.stock,
            'expiry_date': self.expiry_date,
            'low_stock_threshold': self.low_stock_threshold,
            'cost_price': self.cost_price,
            'selling_price': self.selling_price,
            'date_received': self.date_received,
            'status': self.status,
            'is_taxable': self.is_taxable,
            'SKU': self.SKU,
            'sync_logs': self.sync_logs
        }

class Category:
    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.category_name = kwargs.get('category_name', '')
        self.description = kwargs.get('description', '')
        self.status = kwargs.get('status', 'active')
        self.date_created = kwargs.get('date_created', datetime.utcnow())
        self.last_updated = kwargs.get('last_updated', datetime.utcnow())
        self.sub_categories = kwargs.get('sub_categories', [])

    def to_dict(self):
        return {
            '_id': self._id,
            'category_name': self.category_name,
            'description': self.description,
            'status': self.status,
            'date_created': self.date_created,
            'last_updated': self.last_updated,
            'sub_categories': self.sub_categories
        }

class Supplier:
    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.name = kwargs.get('name', '')
        self.contact_person = kwargs.get('contact_person', '')
        self.email = kwargs.get('email', '')
        self.phone = kwargs.get('phone', '')
        self.address = kwargs.get('address', '')
        self.status = kwargs.get('status', 'active')
        self.last_order_date = kwargs.get('last_order_date', None)
        self.date_created = kwargs.get('date_created', datetime.utcnow())
        self.last_updated = kwargs.get('last_updated', datetime.utcnow())

    def to_dict(self):
        return {
            '_id': self._id,
            'name': self.name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'status': self.status,
            'last_order_date': self.last_order_date,
            'date_created': self.date_created,
            'last_updated': self.last_updated
        }

from bson import ObjectId
from datetime import datetime

class SalesLog:

    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('gcash', 'GCash'),
        ('paymaya', 'PayMaya'),
        ('bank_transfer', 'Bank Transfer')
    ]
    
    SALES_TYPES = [
        ('dine_in', 'Dine In'),
        ('takeout', 'Takeout'),
        ('delivery', 'Delivery'),
        ('online', 'Online')
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded')
    ]

    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.customer_id = kwargs.get('customer_id', ObjectId())
        self.user_id = kwargs.get('user_id', ObjectId())
        self.transaction_date = kwargs.get('transaction_date', datetime.utcnow())
        self.total_amount = kwargs.get('total_amount', 0.0)
        self.status = kwargs.get('status', 'completed')
        self.payment_method = kwargs.get('payment_method', 'cash')
        self.sales_type = kwargs.get('sales_type', 'dine_in')
        self.tax_rate = kwargs.get('tax_rate', 0.0)
        self.tax_amount = kwargs.get('tax_amount', 0.0)
        self.is_taxable = kwargs.get('is_taxable', True)
        self.notes = kwargs.get('notes', '')
        self.sync_logs = kwargs.get('sync_logs', [])
        self.item_list = kwargs.get('item_list', [])

    def to_dict(self):
        """Convert to JSON-serializable dictionary for API responses"""
        return {
            '_id': str(self._id),
            'customer_id': str(self.customer_id),
            'user_id': str(self.user_id),
            'transaction_date': self.transaction_date.isoformat() if isinstance(self.transaction_date, datetime) else str(self.transaction_date),
            'total_amount': float(self.total_amount),
            'status': self.status,
            'payment_method': self.payment_method,
            'sales_type': self.sales_type,
            'tax_rate': float(self.tax_rate),
            'tax_amount': float(self.tax_amount),
            'is_taxable': bool(self.is_taxable),
            'notes': self.notes,
            'sync_logs': self.sync_logs,
            'item_list': self.item_list
        }
    
    def to_mongodb_dict(self):
        """Convert to dictionary for MongoDB storage (preserves ObjectIds)"""
        return {
            '_id': self._id,
            'customer_id': self.customer_id,
            'user_id': self.user_id,
            'transaction_date': self.transaction_date,
            'total_amount': self.total_amount,
            'status': self.status,
            'payment_method': self.payment_method,
            'sales_type': self.sales_type,
            'tax_rate': self.tax_rate,
            'tax_amount': self.tax_amount,
            'is_taxable': self.is_taxable,
            'notes': self.notes,
            'sync_logs': self.sync_logs,
            'item_list': self.item_list
        }
    
    def validate_payment_method(self):
        """Validate if payment method is allowed"""
        valid_methods = [method[0] for method in self.PAYMENT_METHODS]
        return self.payment_method in valid_methods
    
    def validate_sales_type(self):
        """Validate if sales type is allowed"""
        valid_types = [sales_type[0] for sales_type in self.SALES_TYPES]
        return self.sales_type in valid_types
    
    def validate_status(self):
        """Validate if status is allowed"""
        valid_statuses = [status[0] for status in self.STATUS_CHOICES]
        return self.status in valid_statuses
    
    def validate(self):
        """Validate the entire sales log object"""
        errors = []
        
        if not self.validate_payment_method():
            errors.append(f"Invalid payment method: {self.payment_method}")
        
        if not self.validate_sales_type():
            errors.append(f"Invalid sales type: {self.sales_type}")
        
        if not self.validate_status():
            errors.append(f"Invalid status: {self.status}")
        
        if self.total_amount < 0:
            errors.append("Total amount cannot be negative")
        
        if self.tax_rate < 0 or self.tax_rate > 1:
            errors.append("Tax rate must be between 0 and 1")
        
        if self.tax_amount < 0:
            errors.append("Tax amount cannot be negative")
        
        return errors
    
    def calculate_tax_amount(self):
        """Calculate tax amount based on total amount and tax rate"""
        if self.is_taxable and self.tax_rate > 0:
            # Calculate tax on the pre-tax amount
            pre_tax_amount = self.total_amount / (1 + self.tax_rate)
            self.tax_amount = self.total_amount - pre_tax_amount
        else:
            self.tax_amount = 0.0
        return self.tax_amount
    
    def get_subtotal(self):
        """Get subtotal (total amount minus tax)"""
        return self.total_amount - self.tax_amount
    
    def get_payment_method_display(self):
        """Get human-readable payment method"""
        for method in self.PAYMENT_METHODS:
            if method[0] == self.payment_method:
                return method[1]
        return self.payment_method
    
    def get_sales_type_display(self):
        """Get human-readable sales type"""
        for sales_type in self.SALES_TYPES:
            if sales_type[0] == self.sales_type:
                return sales_type[1]
        return self.sales_type
    
    def get_status_display(self):
        """Get human-readable status"""
        for status in self.STATUS_CHOICES:
            if status[0] == self.status:
                return status[1]
        return self.status
    
    def __str__(self):
        return f"Invoice {self._id} - ${self.total_amount} ({self.status})"
    
    def __repr__(self):
        return f"SalesLog(_id={self._id}, total_amount={self.total_amount}, status={self.status})"