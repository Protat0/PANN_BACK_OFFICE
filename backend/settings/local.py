from .base import *
from decouple import config

# Development settings
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# CORS settings for development (your frontend runs on 5173)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
    "http://localhost:3000",  # Alternative port
    "http://127.0.0.1:3000",
    "http://localhost:8080",  # Vue CLI dev server (ramyeonsite)
    "http://127.0.0.1:8080",
]

# Allow all origins in development for easier testing
CORS_ALLOW_ALL_ORIGINS = True

# Database configuration for development
USE_MONGODB = config('USE_MONGODB', default=False, cast=bool)

if USE_MONGODB:
    # MongoDB for development (if you want to test with MongoDB locally)
    MONGODB_URI = config('MONGODB_URI', default='mongodb://localhost:27017')
    MONGODB_DATABASE = config('MONGODB_DATABASE', default='pos_system')
    
    DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': MONGODB_DATABASE,
            'CLIENT': {
                'host': MONGODB_URI,
            }
        }
    }
    
    # MongoDB connection settings for your custom operations
    MONGODB_SETTINGS = {
        'host': MONGODB_URI,
        'database': MONGODB_DATABASE
    }
else:
    # SQLite for development (faster, easier to reset)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Backup MongoDB settings (for your existing MongoDB integration)
MONGODB_LOCAL_SETTINGS = {
    'host': config('MONGODB_LOCAL_URI', default='mongodb://localhost:27017'),
    'database': config('MONGODB_LOCAL_DATABASE', default='pos_system')
}

# Development-specific middleware (add any debug middleware here)
if DEBUG:
    # Add debug toolbar if you want (uncomment if you install it)
    # INSTALLED_APPS += ['debug_toolbar']
    # MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    pass

# Email backend for development (console output)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Development logging
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Disable some security features in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Override LOGGING to silence MongoDB noise
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
        'logger': {'level': 'WARNING'},  # This silences MongoDB logs
        'django': {'level': 'INFO'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
