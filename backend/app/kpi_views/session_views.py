from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from ..services.session_services import SessionLogService
from ..services.session_management_service import SessionManagementService
from ..services.customer_service import CustomerService
from ..services.product_service import ProductService
from ..services.user_service import UserService
import logging

# ================ SESSION MANAGEMENT VIEWS ================
        
class SessionLogsView(APIView):
    def get(self, request):
        """Get all session logs"""
        try:
            session_service = SessionLogService()
            sessions = list(session_service.collection.find())
            for session in sessions:
                if '_id' in session:
                    session['_id'] = str(session['_id'])
                if 'user_id' in session:
                    session['user_id'] = str(session['user_id'])
            
            return Response(sessions, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SystemStatusView(APIView):
    def get(self, request):
        """Get system status and counts"""
        try:
            user_service = UserService()
            customer_service = CustomerService()
            product_service = ProductService()
            session_service = SessionLogService()
            
            users = user_service.get_all_users()
            customers = customer_service.get_all_customers()
            products = product_service.get_all_products()
            sessions = list(session_service.collection.find())
            
            active_sessions = list(session_service.collection.find({"status": "active"}))
            
            return Response({
                "system": "PANN User Management System",
                "status": "operational",
                "version": "1.0.0",
                "statistics": {
                    "total_users": len(users),
                    "total_customers": len(customers),
                    "total_products": len(products),
                    "total_sessions": len(sessions),
                    "active_sessions": len(active_sessions)
                },
                "endpoints": {
                    "health": "/api/v1/health/",
                    "users": "/api/v1/users/",
                    "customers": "/api/v1/customers/",
                    "products": "/api/v1/products/",
                    "auth_login": "/api/v1/auth/login/",
                    "auth_logout": "/api/v1/auth/logout/",
                    "session_logs": "/api/v1/session-logs/"
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SessionManagementView(APIView):
    def get(self, request):
        """Get session management options"""
        return Response({
            "endpoints": {
                "active_sessions": "/api/v1/sessions/active/",
                "user_sessions": "/api/v1/sessions/user/{user_id}/",
                "force_logout": "/api/v1/sessions/force-logout/{user_id}/",
                "cleanup": "/api/v1/sessions/cleanup/",
                "statistics": "/api/v1/sessions/statistics/"
            }
        })

class ActiveSessionsView(APIView):
    def get(self, request):
        """Get all active sessions"""
        try:
            session_mgmt = SessionManagementService()
            sessions = session_mgmt.get_active_sessions()
            return Response(sessions, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserSessionsView(APIView):
    def get(self, request, user_id):
        """Get sessions for specific user"""
        try:
            session_mgmt = SessionManagementService()
            sessions = session_mgmt.get_user_sessions(user_id)
            return Response(sessions, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SessionStatisticsView(APIView):
    def get(self, request):
        """Get session statistics"""
        try:
            session_mgmt = SessionManagementService()
            stats = session_mgmt.get_session_statistics()
            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
