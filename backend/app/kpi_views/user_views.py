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

class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "message": "User Management API is running!",
            "status": "active",
            "version": "1.0.0"
        }, status=status.HTTP_200_OK)

class UserListView(APIView):
    def get(self, request):
        """Get all users"""
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
        """Create new user with validation"""
        try:
            serializer = UserCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"error": "Validation failed", "details": serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user_service = UserService()
            validated_data = serializer.validated_data
            new_user = user_service.create_user(validated_data)
            return Response(new_user, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class UserDetailView(APIView):
    def get(self, request, user_id):
        """Get user by ID"""
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
        """Update user"""
        try:
            user_service = UserService()
            user_data = request.data
            updated_user = user_service.update_user(user_id, user_data)
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
        """Delete user"""
        try:
            user_service = UserService()
            deleted = user_service.delete_user(user_id)
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
        """Get user by email"""
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
        """Get user by username"""
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