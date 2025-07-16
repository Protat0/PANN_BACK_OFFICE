from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from ..services.user_service import UserService
import logging

from ..serializers import (
    UserCreateSerializer, 
    UserUpdateSerializer, 
    CustomerCreateSerializer, 
    LoginSerializer
)

def get_authenticated_user_from_jwt(request):
    """Helper function to get authenticated user with proper username from JWT token"""
    try:
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return None
        
        token = authorization.split(" ")[1]
        
        from ..services.auth_services import AuthService
        from bson import ObjectId
        
        auth_service = AuthService()
        user_data = auth_service.get_current_user(token)
        
        if not user_data:
            return None
        
        user_id = user_data.get('user_id')
        user_doc = auth_service.user_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user_doc:
            return None
        
        actual_username = user_doc.get('username')
        if actual_username and actual_username.strip():
            display_username = actual_username
        else:
            display_username = user_doc.get('email', 'unknown')
        
        return {
            "user_id": user_id,
            "username": display_username,
            "email": user_doc.get('email'),
            "branch_id": 1,
            "role": user_doc.get('role', 'admin'),
            "ip_address": request.META.get('REMOTE_ADDR'),
            "user_agent": request.META.get('HTTP_USER_AGENT')
        }
        
    except Exception as e:
        print(f"JWT Auth helper error: {e}")
        return None

class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "message": "User Management API is running!",
            "status": "active",
            "version": "1.0.0"
        }, status=status.HTTP_200_OK)

class UserListView(APIView):
    def get(self, request):
        """Get all users - No changes needed"""
        try:
            user_service = UserService()
            users = user_service.get_all_users()
            return Response(users, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create new user - UPDATED with JWT auth"""
        try:
            # ✅ ADD: Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # ✅ ADD: Check if user is admin
            if current_user.get('role', '').lower() != 'admin':
                return Response(
                    {"error": "Admin permissions required"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = UserCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"error": "Validation failed", "details": serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user_service = UserService()
            validated_data = serializer.validated_data
            
            # ✅ UPDATED: Pass current_user to service
            new_user = user_service.create_user(validated_data, current_user)
            
            return Response(new_user, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
class UserDetailView(APIView):
    def get(self, request, user_id):
        """Get user by ID - No changes needed"""
        try:
            user_service = UserService()
            user = user_service.get_user_by_id(user_id)
            if user:
                return Response(user, status=status.HTTP_200_OK)
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, user_id):
        """Update user - UPDATED with JWT auth"""
        try:
            # ✅ ADD: Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # ✅ ADD: Check if user is admin
            if current_user.get('role', '').lower() != 'admin':
                return Response(
                    {"error": "Admin permissions required"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            user_service = UserService()
            user_data = request.data
            
            # ✅ UPDATED: Pass current_user to service
            updated_user = user_service.update_user(user_id, user_data, current_user)
            
            if updated_user:
                return Response(updated_user, status=status.HTTP_200_OK)
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(self, request, user_id):
        """Delete user - UPDATED with JWT auth"""
        try:
            # ✅ ADD: Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # ✅ ADD: Check if user is admin
            if current_user.get('role', '').lower() != 'admin':
                return Response(
                    {"error": "Admin permissions required"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            user_service = UserService()
            
            # ✅ UPDATED: Pass current_user to service
            deleted = user_service.delete_user(user_id, current_user)
            
            if deleted:
                return Response(
                    {"message": "User deleted successfully"}, 
                    status=status.HTTP_200_OK
                )
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class UserByEmailView(APIView):
    def get(self, request, email):
        """Get user by email - No changes needed"""
        try:
            user_service = UserService()
            user = user_service.get_user_by_email(email)
            if user:
                return Response(user, status=status.HTTP_200_OK)
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class UserByUsernameView(APIView):
    def get(self, request, username):
        """Get user by username - No changes needed"""
        try:
            user_service = UserService()
            user = user_service.get_user_by_username(username)
            if user:
                return Response(user, status=status.HTTP_200_OK)
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )   