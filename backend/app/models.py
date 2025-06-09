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