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
        self.name = kwargs.get('name', '')
        self.description = kwargs.get('description', '')
        self.status = kwargs.get('status', 'active')
        self.date_created = kwargs.get('date_created', datetime.utcnow())
        self.last_updated = kwargs.get('last_updated', datetime.utcnow())

    def to_dict(self):
        return {
            '_id': self._id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'date_created': self.date_created,
            'last_updated': self.last_updated
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