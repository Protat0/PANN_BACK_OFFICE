from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = [
    'your-pos-api.onrender.com',  # Your Render URL
    'your-domain.com',
]

# Strict CORS for production
CORS_ALLOWED_ORIGINS = [
    "https://your-pos-frontend.netlify.app",
    "https://your-domain.com",
]

# MongoDB Atlas
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'pos_system_prod',
        'CLIENT': {
            'host': os.environ.get('MONGODB_URI'),
        }
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')