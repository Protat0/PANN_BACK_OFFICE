from .base import *
from decouple import config
from pymongo import MongoClient

# Development settings
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# CORS settings for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
    "http://localhost:3000",  # Alternative port
    "http://127.0.0.1:3000",
]

# Allow all origins in development for easier testing
CORS_ALLOW_ALL_ORIGINS = True

# Always use SQLite for Django's built-in models (User, Session, etc.)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_django.sqlite3',
    }
}

# MongoDB configuration using PyMongo directly
MONGODB_URI = config('MONGODB_URI', default='mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority')
MONGODB_DATABASE = config('MONGODB_DATABASE', default='pos_system_dev')

# Create MongoDB connection
try:
    mongodb_client = MongoClient(MONGODB_URI)
    mongodb_database = mongodb_client[MONGODB_DATABASE]
    
    # Test the connection
    mongodb_client.admin.command('ismaster')
    print(f"✅ Successfully connected to MongoDB: {MONGODB_DATABASE}")
    
except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {e}")
    mongodb_client = None
    mongodb_database = None

# MongoDB settings for your application
MONGODB_SETTINGS = {
    'client': mongodb_client,
    'database': mongodb_database,
    'uri': MONGODB_URI,
    'database_name': MONGODB_DATABASE
}

# Development-specific settings
if DEBUG:
    pass

# Email backend for development (console output)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable some security features in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'pymongo': {'level': 'WARNING'},
        'django': {'level': 'INFO'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}