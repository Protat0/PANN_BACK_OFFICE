# app/database.py
import pymongo
from django.conf import settings
from decouple import config
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.cloud_client = None
        self.local_client = None
        self.current_client = None
        self.current_db = None
        
    def connect_to_cloud(self):
        """Connect to MongoDB Atlas"""
        try:
            uri = config('MONGODB_URI')
            database_name = config('MONGODB_DATABASE', default='pos_system')
            
            self.cloud_client = pymongo.MongoClient(uri)
            # Test connection
            self.cloud_client.admin.command('ping')
            self.current_client = self.cloud_client
            self.current_db = self.cloud_client[database_name]
            
            logger.info("Successfully connected to MongoDB Atlas")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB Atlas: {e}")
            return False
    
    def connect_to_local(self):
        """Fallback to local MongoDB"""
        try:
            uri = config('MONGODB_LOCAL_URI', default='mongodb://localhost:27017')
            database_name = config('MONGODB_LOCAL_DATABASE', default='pos_system')
            
            self.local_client = pymongo.MongoClient(uri)
            # Test connection
            self.local_client.admin.command('ping')
            self.current_client = self.local_client
            self.current_db = self.local_client[database_name]
            
            logger.info("Connected to local MongoDB")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to local MongoDB: {e}")
            return False
    
    def get_database(self):
        """Get current database connection with fallback"""
        if self.current_db is not None:  # ✅ Fixed: Compare with None
            return self.current_db
            
        # Try cloud first
        if self.connect_to_cloud():
            return self.current_db
            
        # Fallback to local
        if self.connect_to_local():
            return self.current_db
            
        raise Exception("Could not connect to any database")

# Singleton instance
db_manager = DatabaseManager()