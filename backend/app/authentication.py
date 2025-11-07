from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from ..services.auth_services import AuthService
import logging

logger = logging.getLogger(__name__)

class JWTAuthentication(BaseAuthentication):
    """
    Custom JWT authentication for Django REST Framework
    Validates JWT tokens and sets request.user for IsAuthenticated permission
    """
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return None  # No authentication attempted
        
        token = auth_header.split(' ', 1)[1]
        
        try:
            auth_service = AuthService()
            user_data = auth_service.get_current_user(token)
            
            if not user_data or not user_data.get('user_id'):
                logger.warning("JWT token validation failed: invalid user data")
                return None  # Authentication failed, but don't raise exception
            
            # Create a simple user object that DRF can use
            # We'll use a simple object that has the necessary attributes
            user = type('User', (), {
                'id': user_data.get('user_id'),
                'username': user_data.get('username', ''),
                'email': user_data.get('email', ''),
                'is_authenticated': True,
                'is_active': True,
            })()
            
            return (user, token)
            
        except Exception as e:
            logger.error(f"JWT authentication error: {e}")
            return None  # Authentication failed, but don't raise exception
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response.
        """
        return 'Bearer'

