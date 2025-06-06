from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True

# MongoDB with pymongo (more reliable than djongo)
import pymongo

# For now, use SQLite for Django ORM and pymongo for custom MongoDB operations
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# MongoDB connection (we'll use this manually)
MONGODB_SETTINGS = {
    'host': 'mongodb://localhost:27017',
    'database': 'pos_system_dev'
}
    
