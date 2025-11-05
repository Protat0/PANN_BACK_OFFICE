"""
OAuth Service for Google and Facebook Authentication
Handles OAuth flow, user creation/lookup, and token generation
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
import requests
import logging
from bson import ObjectId
import bcrypt

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings

from ..database import db_manager
from .auth_services import AuthService

logger = logging.getLogger(__name__)


class OAuthService:
    """Service for handling OAuth authentication"""
    
    def __init__(self):
        self.db = db_manager.get_database()
        self.user_collection = self.db.users
        self.customer_collection = self.db.customers
        self.auth_service = AuthService()
        
        # OAuth configuration from settings
        self.google_client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
        self.google_client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', '')
        self.google_redirect_uri = getattr(settings, 'GOOGLE_REDIRECT_URI', '')
        
        self.facebook_app_id = getattr(settings, 'FACEBOOK_APP_ID', '')
        self.facebook_app_secret = getattr(settings, 'FACEBOOK_APP_SECRET', '')
        self.facebook_redirect_uri = getattr(settings, 'FACEBOOK_REDIRECT_URI', '')
        
        self.frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    
    def get_google_auth_url(self) -> str:
        """Generate Google OAuth authorization URL"""
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": self.google_client_id,
            "redirect_uri": self.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent"
        }
        
        # Build query string
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
        return f"{base_url}?{query_string}"
    
    def get_facebook_auth_url(self) -> str:
        """Generate Facebook OAuth authorization URL"""
        base_url = "https://www.facebook.com/v18.0/dialog/oauth"
        params = {
            "client_id": self.facebook_app_id,
            "redirect_uri": self.facebook_redirect_uri,
            "scope": "email,public_profile",
            "response_type": "code"
        }
        
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
        return f"{base_url}?{query_string}"
    
    def verify_google_token(self, code: str) -> Optional[Dict]:
        """
        Exchange authorization code for access token and verify with Google
        Returns user info dict or None if verification fails
        """
        try:
            # Exchange code for access token
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                "code": code,
                "client_id": self.google_client_id,
                "client_secret": self.google_client_secret,
                "redirect_uri": self.google_redirect_uri,
                "grant_type": "authorization_code"
            }
            
            token_response = requests.post(token_url, data=token_data)
            token_response.raise_for_status()
            token_json = token_response.json()
            
            id_token_value = token_json.get('id_token')
            
            # Verify the ID token
            idinfo = id_token.verify_oauth2_token(
                id_token_value, 
                google_requests.Request(), 
                self.google_client_id
            )
            
            # Extract user information
            user_info = {
                'oauth_id': idinfo.get('sub'),
                'email': idinfo.get('email'),
                'email_verified': idinfo.get('email_verified'),
                'full_name': idinfo.get('name'),
                'first_name': idinfo.get('given_name'),
                'last_name': idinfo.get('family_name'),
                'picture': idinfo.get('picture'),
                'provider': 'google'
            }
            
            logger.info(f"✅ Google OAuth verified for: {user_info['email']}")
            return user_info
            
        except Exception as e:
            logger.error(f"❌ Google token verification failed: {str(e)}")
            return None
    
    def verify_facebook_token(self, code: str) -> Optional[Dict]:
        """
        Exchange authorization code for access token and get user info from Facebook
        Returns user info dict or None if verification fails
        """
        try:
            # Exchange code for access token
            token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            token_params = {
                "client_id": self.facebook_app_id,
                "client_secret": self.facebook_app_secret,
                "redirect_uri": self.facebook_redirect_uri,
                "code": code
            }
            
            token_response = requests.get(token_url, params=token_params)
            token_response.raise_for_status()
            token_json = token_response.json()
            
            access_token = token_json.get('access_token')
            
            # Get user info
            user_info_url = "https://graph.facebook.com/v18.0/me"
            user_info_params = {
                "fields": "id,email,name,first_name,last_name,picture",
                "access_token": access_token
            }
            
            user_response = requests.get(user_info_url, params=user_info_params)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Extract user information
            user_info = {
                'oauth_id': user_data.get('id'),
                'email': user_data.get('email'),
                'email_verified': True,  # Facebook verifies emails
                'full_name': user_data.get('name'),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'picture': user_data.get('picture', {}).get('data', {}).get('url'),
                'provider': 'facebook'
            }
            
            logger.info(f"✅ Facebook OAuth verified for: {user_info['email']}")
            return user_info
            
        except Exception as e:
            logger.error(f"❌ Facebook token verification failed: {str(e)}")
            return None
    
    def find_or_create_user(self, oauth_user_info: Dict, user_type: str = 'customer') -> Dict:
        """
        Find existing user or create new user from OAuth info
        
        Args:
            oauth_user_info: User info from OAuth provider
            user_type: 'customer' or 'user' (admin/employee)
        
        Returns:
            User/Customer dict with JWT tokens
        """
        provider = oauth_user_info['provider']
        oauth_id = oauth_user_info['oauth_id']
        email = oauth_user_info.get('email', '').lower()
        
        if not email:
            raise ValueError("Email is required for OAuth authentication")
        
        # Choose collection based on user type
        collection = self.customer_collection if user_type == 'customer' else self.user_collection
        
        # Try to find user by OAuth provider and ID
        existing_user = collection.find_one({
            'oauth_provider': provider,
            'oauth_id': oauth_id
        })
        
        if existing_user:
            logger.info(f"✅ Found existing {user_type} with {provider} OAuth: {email}")
            return self._generate_oauth_response(existing_user, user_type)
        
        # Try to find user by email
        existing_user_by_email = collection.find_one({'email': email})
        
        if existing_user_by_email:
            # User exists with same email - link OAuth account
            logger.info(f"🔗 Linking {provider} OAuth to existing {user_type}: {email}")
            
            update_data = {
                'oauth_provider': provider,
                'oauth_id': oauth_id,
                'oauth_picture': oauth_user_info.get('picture'),
                'last_updated': datetime.utcnow()
            }
            
            collection.update_one(
                {'_id': existing_user_by_email['_id']},
                {'$set': update_data}
            )
            
            updated_user = collection.find_one({'_id': existing_user_by_email['_id']})
            return self._generate_oauth_response(updated_user, user_type)
        
        # Create new user
        logger.info(f"➕ Creating new {user_type} from {provider} OAuth: {email}")
        
        # Generate username from email
        username = email.split('@')[0]
        base_username = username
        counter = 1
        
        # Ensure username is unique
        while collection.find_one({'username': username}):
            username = f"{base_username}{counter}"
            counter += 1
        
        # Prepare user data
        new_user = {
            '_id': str(ObjectId()),
            'username': username,
            'email': email,
            'password': '',  # No password for OAuth users
            'full_name': oauth_user_info.get('full_name', ''),
            'oauth_provider': provider,
            'oauth_id': oauth_id,
            'oauth_picture': oauth_user_info.get('picture'),
            'status': 'active',
            'date_created': datetime.utcnow(),
            'last_updated': datetime.utcnow(),
            'last_login': datetime.utcnow(),
            'source': provider
        }
        
        # Add role for admin/employee users
        if user_type == 'user':
            new_user['role'] = 'customer'  # Default role, can be changed by admin
        
        # Add customer-specific fields
        if user_type == 'customer':
            new_user.update({
                'customer_id': new_user['_id'],
                'phone': '',
                'delivery_address': {},
                'loyalty_points': 0,
                'last_purchase': None
            })
        
        # Insert into database
        collection.insert_one(new_user)
        
        logger.info(f"✅ Created new {user_type}: {email} (ID: {new_user['_id']})")
        
        return self._generate_oauth_response(new_user, user_type)
    
    def _generate_oauth_response(self, user: Dict, user_type: str) -> Dict:
        """Generate OAuth login response with JWT tokens"""
        
        user_id = str(user['_id'])
        
        # Update last login
        collection = self.customer_collection if user_type == 'customer' else self.user_collection
        collection.update_one(
            {'_id': user['_id']},
            {'$set': {'last_login': datetime.utcnow()}}
        )
        
        # Create JWT tokens using existing AuthService
        token_data = {
            'sub': user_id,
            'email': user['email'],
            'role': user.get('role', 'customer'),
            'oauth_provider': user.get('oauth_provider', ''),
            'type': user_type
        }
        
        # For customers, add customer_id to token
        if user_type == 'customer':
            token_data['customer_id'] = user_id
        
        access_token = self.auth_service.create_access_token(token_data)
        refresh_token = self.auth_service.create_refresh_token(token_data)
        
        # Prepare response
        response = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'user': {
                'id': user_id,
                'email': user['email'],
                'username': user['username'],
                'full_name': user.get('full_name', ''),
                'oauth_provider': user.get('oauth_provider', ''),
                'oauth_picture': user.get('oauth_picture', ''),
                'status': user.get('status', 'active')
            }
        }
        
        # Add customer-specific data
        if user_type == 'customer':
            response['user'].update({
                'loyalty_points': user.get('loyalty_points', 0),
                'phone': user.get('phone', ''),
                'delivery_address': user.get('delivery_address', {})
            })
        else:
            response['user']['role'] = user.get('role', 'customer')
        
        return response
    
    def disconnect_oauth(self, user_id: str, user_type: str = 'customer') -> bool:
        """
        Disconnect OAuth provider from user account
        Only works if user has a password set (for fallback login)
        """
        try:
            collection = self.customer_collection if user_type == 'customer' else self.user_collection
            user = collection.find_one({'_id': user_id})
            
            if not user:
                return False
            
            # Check if user has password set
            if not user.get('password'):
                raise ValueError("Cannot disconnect OAuth. Please set a password first.")
            
            # Remove OAuth data
            update_result = collection.update_one(
                {'_id': user_id},
                {
                    '$unset': {
                        'oauth_provider': '',
                        'oauth_id': '',
                        'oauth_picture': ''
                    },
                    '$set': {
                        'last_updated': datetime.utcnow()
                    }
                }
            )
            
            return update_result.modified_count > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to disconnect OAuth: {str(e)}")
            raise e


