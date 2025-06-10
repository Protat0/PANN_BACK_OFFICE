# settings/base.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-dev-secret-key')

# Applications
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
]

LOCAL_APPS = [
    'api',
    'notifications', 
    # 'inventory',  # You'll add these as your POS grows
    # 'sales',
    # 'customers',
    # 'reports',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'posbackend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50
}

# CORS settings for Vue.js frontend
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Vue.js dev server
    "http://127.0.0.1:3000",
    "http://localhost:8080",  # Alternative Vue.js port
    "http://127.0.0.1:8080",
    # Add your production frontend URL here
    # "https://admin.ramyeonfoodcorner.com",
]

CORS_ALLOW_CREDENTIALS = True

# Email Configuration for SendGrid (Notifications)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@ramyeonfoodcorner.com')

# SMS Configuration for Twilio (Notifications)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

# MongoDB Configuration (for your custom auth system)
MONGODB_SETTINGS = {
    'DATABASE_URL': os.environ.get('MONGODB_URL', 'mongodb://localhost:27017/'),
    'DATABASE_NAME': os.environ.get('MONGODB_NAME', 'pann_database'),
    'COLLECTIONS': {
        'users': 'users',
        'sessions': 'session_logs',
        'products': 'products',
        'orders': 'orders',
        'inventory': 'inventory',
    }
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'  # Philippines timezone for Ramyeon Food Corner
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ====================================================================
# LOGGING CONFIGURATION
# ====================================================================

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
        'security': {
            'format': '[SECURITY] {asctime} {levelname} {message}',
            'style': '{',
        },
        'notification': {
            'format': '[NOTIFICATION] {asctime} {levelname} {module} {message}',
            'style': '{',
        },
        'auth': {
            'format': '[AUTH] {asctime} {levelname} {message} | IP: {extra[ip]:-} | User: {extra[user]:-}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        # Console handler for development
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        
        # General application log file
        'file_general': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'pann_general.log',
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        
        # Security-specific log file (for your admin login attempts)
        'file_security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'pann_security.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 10,
            'formatter': 'security',
        },
        
        # Authentication log file (for your MongoDB auth system)
        'file_auth': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'pann_auth.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 10,
            'formatter': 'auth',
        },
        
        # Notification system log file
        'file_notifications': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'pann_notifications.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'notification',
        },
        
        # Error log file
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'pann_errors.log',
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        
        # Email handler for critical errors
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file_general'],
    },
    'loggers': {
        # Django's built-in loggers
        'django': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file_errors', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file_security'],
            'level': 'WARNING',
            'propagate': False,
        },
        
        # Your custom authentication system
        'pann.auth': {
            'handlers': ['console', 'file_auth', 'file_security'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Notification system
        'notifications': {
            'handlers': ['console', 'file_notifications'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Security events (failed logins, unauthorized access)
        'pann.security': {
            'handlers': ['file_security', 'file_auth'],
            'level': 'WARNING',
            'propagate': False,
        },
        
        # POS system operations
        'pann.pos': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Inventory operations
        'pann.inventory': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ====================================================================
# NOTIFICATION SYSTEM SETTINGS
# ====================================================================

# Notification delivery settings
NOTIFICATION_SETTINGS = {
    'EMAIL_DELIVERY': {
        'ENABLED': True,
        'RETRY_ATTEMPTS': 3,
        'RETRY_DELAY': 300,  # 5 minutes
    },
    'SMS_DELIVERY': {
        'ENABLED': bool(os.environ.get('TWILIO_ACCOUNT_SID')),
        'RETRY_ATTEMPTS': 2,
        'RETRY_DELAY': 180,  # 3 minutes
    },
    'STOCK_ALERTS': {
        'ENABLED': True,
        'DEFAULT_LOW_STOCK_THRESHOLD': 10,
        'CHECK_INTERVAL': 300,  # 5 minutes
    },
    'CLEANUP': {
        'DELETE_READ_AFTER_DAYS': 30,
        'DELETE_UNREAD_AFTER_DAYS': 90,
    }
}

# ====================================================================
# SECURITY SETTINGS
# ====================================================================

# Admin access monitoring
ADMIN_ACCESS_SETTINGS = {
    'LOG_ALL_ATTEMPTS': True,
    'BLOCK_NON_ADMIN_LOGINS': True,
    'MAX_FAILED_ATTEMPTS': 5,
    'LOCKOUT_DURATION': 900,  # 15 minutes
    'ALERT_ON_FAILED_ATTEMPTS': True,
}

# Session settings for your custom auth
SESSION_SETTINGS = {
    'LOG_ALL_SESSIONS': True,
    'SESSION_TIMEOUT': 3600,  # 1 hour
    'TRACK_USER_ACTIVITY': True,
}

# ====================================================================
# DEVELOPMENT/PRODUCTION OVERRIDES
# ====================================================================

# This will be overridden in development.py and production.py
DEBUG = True

# Default database (you might not use this since you're using MongoDB)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}