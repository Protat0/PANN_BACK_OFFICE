from pymongo import MongoClient
from django.conf import settings
from bson import ObjectId

class DatabaseService:
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_NAME]
    
    def get_collection(self, collection_name):
        return self.db[collection_name]
    
    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    def convert_object_ids(self, documents):
        """Convert ObjectIds to strings for a list of documents"""
        return [self.convert_object_id(doc) for doc in documents]