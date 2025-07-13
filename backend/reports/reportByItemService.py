from datetime import datetime
from bson import ObjectId
from django.contrib.auth.models import User
from app.database import db_manager
import uuid

class ReportByItemService:
   def __init__(self):
      self.db = db_manager.get_database()
      self.user_collection= self.db.users
      self.product_collection= self.db.products
      
   def convert_object_id(self, document):
      """Convert ObjectId to string for JSON serialization"""
      if document and '_id' in document:
         document['_id'] = str(document['_id'])
   
   def get_top_items(self):
      topItems = product_collection