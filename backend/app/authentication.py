from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from ..services.auth_services import AuthService
from django.conf import settings
import jwt
import logging

logger = logging.getLogger(__name__)

class JWTAuthentication(BaseAuthentication):
    """
    Custom JWT authentication for Django REST Framework
    Validates JWT tokens (both admin and customer) and sets request.user for IsAuthenticated permission
    """
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        Handles both admin tokens (with user_id/sub) and customer tokens (with customer_id).
        """
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return None  # No authentication attempted
        
        token = auth_header.split(' ', 1)[1]
        
        try:
            # First, try to decode the token to see if it's a customer token or admin token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            # Check if it's a customer token (has customer_id)
            if 'customer_id' in payload:
                customer_id = payload.get('customer_id')
                email = payload.get('email', '')
                username = payload.get('username', '')
                
                # Create a simple user object for customers
                user = type('User', (), {
                    'id': customer_id,
                    'customer_id': customer_id,  # Also store as customer_id for compatibility
                    'username': username or email,
                    'email': email,
                    'is_authenticated': True,
                    'is_active': True,
                })()
                
                logger.info(f"✅ Customer JWT authenticated: {customer_id}")
                return (user, token)
            
            # Otherwise, try admin authentication via AuthService
            auth_service = AuthService()
            user_data = auth_service.get_current_user(token)
            
            if user_data and user_data.get('user_id'):
                # Create a simple user object for admin users
                user = type('User', (), {
                    'id': user_data.get('user_id'),
                    'username': user_data.get('username', ''),
                    'email': user_data.get('email', ''),
                    'is_authenticated': True,
                    'is_active': True,
                })()
                
                logger.info(f"✅ Admin JWT authenticated: {user_data.get('user_id')}")
                return (user, token)
            
            logger.warning("JWT token validation failed: invalid user data")
            return None  # Authentication failed, but don't raise exception
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"JWT authentication error: {e}")
            return None  # Authentication failed, but don't raise exception
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response.
        """
        return 'Bearer'

