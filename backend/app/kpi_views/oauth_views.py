"""
OAuth Views for Google and Facebook Authentication
Handles OAuth login flow and callbacks
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import redirect
from django.conf import settings
import logging
from urllib.parse import urlencode

from ..services.oauth_service import OAuthService
from ..services.session_services import SessionLogService

logger = logging.getLogger(__name__)


class GoogleLoginView(APIView):
    """
    Initiate Google OAuth flow
    GET /api/v1/auth/google/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Redirect to Google OAuth consent screen"""
        try:
            oauth_service = OAuthService()
            auth_url = oauth_service.get_google_auth_url()
            
            logger.info("🔀 Redirecting to Google OAuth")
            return redirect(auth_url)
            
        except Exception as e:
            logger.error(f"❌ Google login error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to initiate Google login'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleCallbackView(APIView):
    """
    Google OAuth callback handler
    GET /api/v1/auth/google/callback/?code=xxx
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Handle Google OAuth callback"""
        try:
            # Get authorization code from query params
            code = request.GET.get('code')
            error = request.GET.get('error')
            
            if error:
                logger.error(f"❌ Google OAuth error: {error}")
                return self._redirect_to_frontend_with_error('Google login failed')
            
            if not code:
                logger.error("❌ No authorization code provided")
                return self._redirect_to_frontend_with_error('No authorization code')
            
            # Verify token and get user info
            oauth_service = OAuthService()
            user_info = oauth_service.verify_google_token(code)
            
            if not user_info:
                logger.error("❌ Google token verification failed")
                return self._redirect_to_frontend_with_error('Token verification failed')
            
            # Determine user type (customer by default, can be customized)
            user_type = request.GET.get('type', 'customer')
            
            # Find or create user
            auth_response = oauth_service.find_or_create_user(user_info, user_type)
            
            # Log session
            try:
                session_service = SessionLogService()
                session_data = {
                    'user_id': auth_response['user']['id'],
                    'username': auth_response['user']['username'],
                    'email': auth_response['user']['email'],
                    'ip_address': self._get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'login_method': 'google_oauth'
                }
                session_service.log_login(session_data)
            except Exception as session_error:
                logger.warning(f"⚠️ Session logging failed: {str(session_error)}")
            
            # Redirect to frontend with tokens
            return self._redirect_to_frontend_with_tokens(
                auth_response['access_token'],
                auth_response['refresh_token']
            )
            
        except Exception as e:
            logger.error(f"❌ Google callback error: {str(e)}")
            return self._redirect_to_frontend_with_error(str(e))
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _redirect_to_frontend_with_tokens(self, access_token, refresh_token):
        """Redirect to frontend with auth tokens"""
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        params = urlencode({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'success': 'true'
        })
        return redirect(f"{frontend_url}/auth/callback?{params}")
    
    def _redirect_to_frontend_with_error(self, error_message):
        """Redirect to frontend with error message"""
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        params = urlencode({
            'error': error_message,
            'success': 'false'
        })
        return redirect(f"{frontend_url}/auth/callback?{params}")


class FacebookLoginView(APIView):
    """
    Initiate Facebook OAuth flow
    GET /api/v1/auth/facebook/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Redirect to Facebook OAuth consent screen"""
        try:
            oauth_service = OAuthService()
            auth_url = oauth_service.get_facebook_auth_url()
            
            logger.info("🔀 Redirecting to Facebook OAuth")
            return redirect(auth_url)
            
        except Exception as e:
            logger.error(f"❌ Facebook login error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to initiate Facebook login'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FacebookCallbackView(APIView):
    """
    Facebook OAuth callback handler
    GET /api/v1/auth/facebook/callback/?code=xxx
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Handle Facebook OAuth callback"""
        try:
            # Get authorization code from query params
            code = request.GET.get('code')
            error = request.GET.get('error')
            
            if error:
                logger.error(f"❌ Facebook OAuth error: {error}")
                return self._redirect_to_frontend_with_error('Facebook login failed')
            
            if not code:
                logger.error("❌ No authorization code provided")
                return self._redirect_to_frontend_with_error('No authorization code')
            
            # Verify token and get user info
            oauth_service = OAuthService()
            user_info = oauth_service.verify_facebook_token(code)
            
            if not user_info:
                logger.error("❌ Facebook token verification failed")
                return self._redirect_to_frontend_with_error('Token verification failed')
            
            # Determine user type (customer by default, can be customized)
            user_type = request.GET.get('type', 'customer')
            
            # Find or create user
            auth_response = oauth_service.find_or_create_user(user_info, user_type)
            
            # Log session
            try:
                session_service = SessionLogService()
                session_data = {
                    'user_id': auth_response['user']['id'],
                    'username': auth_response['user']['username'],
                    'email': auth_response['user']['email'],
                    'ip_address': self._get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'login_method': 'facebook_oauth'
                }
                session_service.log_login(session_data)
            except Exception as session_error:
                logger.warning(f"⚠️ Session logging failed: {str(session_error)}")
            
            # Redirect to frontend with tokens
            return self._redirect_to_frontend_with_tokens(
                auth_response['access_token'],
                auth_response['refresh_token']
            )
            
        except Exception as e:
            logger.error(f"❌ Facebook callback error: {str(e)}")
            return self._redirect_to_frontend_with_error(str(e))
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _redirect_to_frontend_with_tokens(self, access_token, refresh_token):
        """Redirect to frontend with auth tokens"""
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        params = urlencode({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'success': 'true'
        })
        return redirect(f"{frontend_url}/auth/callback?{params}")
    
    def _redirect_to_frontend_with_error(self, error_message):
        """Redirect to frontend with error message"""
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        params = urlencode({
            'error': error_message,
            'success': 'false'
        })
        return redirect(f"{frontend_url}/auth/callback?{params}")


class OAuthDisconnectView(APIView):
    """
    Disconnect OAuth provider from user account
    POST /api/v1/auth/oauth/disconnect/
    Requires authentication
    """
    
    def post(self, request):
        """Disconnect OAuth from current user"""
        try:
            # Get current user from JWT token
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return Response({
                    'success': False,
                    'error': 'Authorization required'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            token = auth_header.split(' ')[1]
            
            # Verify token and get user
            from ..services.auth_services import AuthService
            auth_service = AuthService()
            user_info = auth_service.get_current_user(token)
            
            if not user_info:
                return Response({
                    'success': False,
                    'error': 'Invalid token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Disconnect OAuth
            user_type = request.data.get('user_type', 'customer')
            oauth_service = OAuthService()
            
            success = oauth_service.disconnect_oauth(
                user_info['user_id'],
                user_type
            )
            
            if not success:
                return Response({
                    'success': False,
                    'error': 'Failed to disconnect OAuth'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'success': True,
                'message': 'OAuth provider disconnected successfully'
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"❌ OAuth disconnect error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to disconnect OAuth'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

