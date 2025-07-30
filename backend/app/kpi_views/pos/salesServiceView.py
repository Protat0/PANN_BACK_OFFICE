from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from ...services.pos.SalesService import SalesService
import logging

def get_authenticated_user_from_jwt(request):
    """Helper function to get authenticated user with proper username from JWT token"""
    try:
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return None
        
        token = authorization.split(" ")[1]
        
        from app.services.auth_services import AuthService
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
            "role": user_doc.get('role', 'dmina'),
            "ip_address": request.META.get('REMOTE_ADDR'),
            "user_agent": request.META.get('HTTP_USER_AGENT')
        }
        
    except Exception as e:
        print(f"JWT Auth helper error: {e}")
        return None
