from rest_framework.response import Response
from rest_framework import status
from ..services.auth_services import AuthService
from bson import ObjectId
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def get_authenticated_user_from_jwt(request):
    """Helper function to get authenticated user from JWT token"""
    try:
        authorization = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return None
        
        token = authorization.split(" ", 1)[1]
         
        auth_service = AuthService()
        user_data = auth_service.get_current_user(token)
        
        if not user_data or not user_data.get('user_id'):
            return None
        
        user_id = user_data.get('user_id')
        user_doc = auth_service.user_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user_doc:
            return None
        
        username = user_doc.get('username', '').strip()
        display_username = username or user_doc.get('email', 'unknown')

        return {
            "user_id": user_id,
            "username": display_username,
            "email": user_doc.get('email'),
            "branch_id": 1,
            "role": user_doc.get('role', 'admin')
        }

    except Exception as e:
        logger.error(f"JWT authentication error: {e}")
        return None

# ================================================================
# AUTHENTICATION DECORATORS
# ================================================================

def require_authentication(view_func):
    """Decorator to require basic authentication"""
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        current_user = get_authenticated_user_from_jwt(request)
        if not current_user:
            return Response(
                {"error": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        request.current_user = current_user
        return view_func(self, request, *args, **kwargs)
    return wrapper

def require_admin(view_func):
    """Decorator to require admin authentication"""
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        current_user = get_authenticated_user_from_jwt(request)
        if not current_user:
            return Response(
                {"error": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        if current_user.get('role', '').lower() != 'admin':
            return Response(
                {"error": "Admin permissions required"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        request.current_user = current_user
        return view_func(self, request, *args, **kwargs)
    return wrapper

def require_permission(*allowed_roles):
    """Decorator to require specific role(s)"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            current_user = get_authenticated_user_from_jwt(request)
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            user_role = current_user.get('role', '').lower()
            allowed = [role.lower() for role in allowed_roles]
            
            if user_role not in allowed:
                return Response(
                    {"error": f"Requires one of: {', '.join(allowed_roles)}"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            request.current_user = current_user
            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator