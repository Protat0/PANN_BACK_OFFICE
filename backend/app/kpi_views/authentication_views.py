from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from ..services.auth_services import AuthService
from ..services.session_services import SessionLogService 
import logging

# ================ AUTHENTICATION VIEWS ================

class LoginView(APIView):
    def post(self, request):
        """User login"""
        try:
            auth_service = AuthService()
            email = request.data.get('email')
            password = request.data.get('password')
            
            if not email or not password:
                return Response(
                    {"error": "Email and password are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = auth_service.login(email, password)
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

class LogoutView(APIView):
    def post(self, request):
        print("\n" + "="*50)
        print("LOGOUT VIEW CALLED - LOOK HERE!")
        print("="*50)
        """User logout with session logging"""
        try:
            auth_service = AuthService()
            session_service = SessionLogService()  # ✅ ADD THIS
            
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return Response(
                    {"error": "Missing or invalid authorization header"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            token = authorization.split(" ")[1]
            
            # ✅ NEW: Get user info from token BEFORE logout
            try:
                # Get current user from token to get user_id
                current_user = auth_service.get_current_user(token)
                print(f"🔍 LOGOUT: Current user from token: {current_user}")
                
                if current_user and current_user.get('user_id'):
                    user_id = str(current_user.get('user_id'))
                    print(f"🔍 LOGOUT: Extracted user_id: {user_id}")
                    
                    # ✅ NEW: Log session logout BEFORE auth logout
                    try:
                        print(f"🔍 LOGOUT: About to call session_service.log_logout({user_id})")
                        session_result = session_service.log_logout(user_id)
                        print(f"✅ LOGOUT: Session logout result: {session_result}")
                    except Exception as session_error:
                        print(f"❌ LOGOUT: Session logout failed: {session_error}")
                        # Continue with auth logout even if session logout fails
                else:
                    print(f"⚠️ LOGOUT: Could not extract user_id from token")
                    
            except Exception as user_error:
                print(f"❌ LOGOUT: Could not get current user: {user_error}")
                # Continue with auth logout even if we can't get user info
            
            # Do the original auth logout
            result = auth_service.logout(token)
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"❌ LOGOUT: Auth logout failed: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RefreshTokenView(APIView):
    def post(self, request):
        """Refresh access token"""
        try:
            auth_service = AuthService()
            refresh_token = request.data.get('refresh_token')
            
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = auth_service.refresh_access_token(refresh_token)
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

class CurrentUserView(APIView):
    def get(self, request):
        """Get current authenticated user"""
        try:
            auth_service = AuthService()
            
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return Response(
                    {"error": "Missing or invalid authorization header"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            token = authorization.split(" ")[1]
            user = auth_service.get_current_user(token)
            
            if user:
                return Response(user, status=status.HTTP_200_OK)
            
            return Response(
                {"error": "Invalid token"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VerifyTokenView(APIView):
    def post(self, request):
        """Verify if token is valid"""
        try:
            auth_service = AuthService()
            
            authorization = request.headers.get("Authorization")
            if authorization and authorization.startswith("Bearer "):
                token = authorization.split(" ")[1]
            else:
                token = request.data.get('token')
            
            if not token:
                return Response(
                    {"error": "Token is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            payload = auth_service.verify_token(token)
            
            if payload:
                return Response({
                    "valid": True,
                    "user_id": payload.get("sub"),
                    "email": payload.get("email"),
                    "role": payload.get("role")
                }, status=status.HTTP_200_OK)
            
            return Response(
                {"valid": False, "error": "Invalid token"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )