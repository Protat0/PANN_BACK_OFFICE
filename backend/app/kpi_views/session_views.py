from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..services.session_services import SessionLogService, SessionDisplayService
from ..services.customer_service import CustomerService
from ..services.product_service import ProductService
from ..services.user_service import UserService
from ..decorators.authenticationDecorator import require_authentication, require_admin
import logging

logger = logging.getLogger(__name__)

# ================ SESSION MANAGEMENT VIEWS ================

class SessionLogsView(APIView):
    """Get session logs with filtering options"""
    
    def __init__(self):
        self.session_service = SessionLogService()
    
    @require_authentication
    def get(self, request):
        """Get all session logs with optional filtering"""
        try:
            # Get query parameters
            limit = int(request.query_params.get('limit', 100))
            status_filter = request.query_params.get('status', None)
            
            # Use the optimized service method
            sessions = self.session_service.get_active_sessions() if status_filter == 'active' else []
            
            # If no specific filter, get all sessions with conversion
            if not status_filter:
                sessions = list(self.session_service.collection.find().limit(limit))
                sessions = [self.session_service.convert_object_id(session) for session in sessions]
            
            return Response({
                'success': True,
                'data': sessions,
                'count': len(sessions)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in SessionLogsView: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SystemStatusView(APIView):
    """Get comprehensive system status and statistics"""
    
    def __init__(self):
        self.user_service = UserService()
        self.customer_service = CustomerService()
        self.product_service = ProductService()
        self.session_service = SessionLogService()
    
    @require_authentication
    def get(self, request):
        """Get system status with optimized statistics"""
        try:
            # Use optimized service methods instead of raw database calls
            session_stats = self.session_service.get_session_statistics()
            
            # Get other statistics efficiently
            users = self.user_service.get_all_users()
            customers = self.customer_service.get_all_customers()
            products = self.product_service.get_all_products()
            
            return Response({
                "system": "PANN User Management System",
                "status": "operational",
                "version": "1.0.0",
                "statistics": {
                    "total_users": len(users),
                    "total_customers": len(customers),
                    "total_products": len(products),
                    "active_sessions": session_stats.get('active_sessions', 0),
                    "today_sessions": session_stats.get('today_sessions', 0),
                    "avg_session_duration": session_stats.get('avg_session_duration', 0)
                },
                "endpoints": {
                    "health": "/api/v1/health/",
                    "users": "/api/v1/users/",
                    "customers": "/api/v1/customers/",
                    "products": "/api/v1/products/",
                    "auth_login": "/api/v1/auth/login/",
                    "auth_logout": "/api/v1/auth/logout/",
                    "session_logs": "/api/v1/session-logs/",
                    "combined_logs": "/api/v1/logs/combined/"
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in SystemStatusView: {e}")
            return Response({
                "system": "PANN User Management System",
                "status": "error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActiveSessionsView(APIView):
    """Get all currently active sessions"""
    
    def __init__(self):
        self.session_service = SessionLogService()
    
    @require_admin  # Only admins should see active sessions
    def get(self, request):
        """Get all active sessions"""
        try:
            sessions = self.session_service.get_active_sessions()
            return Response({
                'success': True,
                'data': sessions,
                'count': len(sessions)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in ActiveSessionsView: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserSessionsView(APIView):
    """Get session history for a specific user"""
    
    def __init__(self):
        self.session_service = SessionLogService()
    
    @require_authentication
    def get(self, request, user_id):
        """Get sessions for specific user"""
        try:
            # Get query parameters
            limit = int(request.query_params.get('limit', 50))
            
            # Check if user is requesting their own sessions or is admin
            current_user = request.current_user
            if current_user.get('user_id') != user_id and current_user.get('role') != 'admin':
                return Response({
                    'success': False,
                    'error': 'Permission denied. You can only view your own sessions.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            sessions = self.session_service.get_user_sessions(user_id, limit=limit)
            return Response({
                'success': True,
                'data': sessions,
                'count': len(sessions)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in UserSessionsView: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SessionStatisticsView(APIView):
    """Get session statistics and analytics"""
    
    def __init__(self):
        self.session_service = SessionLogService()
    
    @require_authentication
    def get(self, request):
        """Get session statistics"""
        try:
            stats = self.session_service.get_session_statistics()
            return Response({
                'success': True,
                'data': stats
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in SessionStatisticsView: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'data': {
                    "active_sessions": 0,
                    "today_sessions": 0,
                    "avg_session_duration": 0
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SessionDisplayView(APIView):
    """Get formatted session logs for display"""
    
    def __init__(self):
        self.display_service = SessionDisplayService()  # Updated class name
    
    @require_authentication
    def get(self, request):
        """Get formatted session logs"""
        try:
            # Get query parameters
            limit = int(request.query_params.get('limit', 100))
            status_filter = request.query_params.get('status', None)
            
            result = self.display_service.get_session_logs(
                limit=limit, 
                status_filter=status_filter
            )
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in SessionDisplayView: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CombinedLogsView(APIView):
    """Get both session and audit logs combined"""
    
    def __init__(self):
        self.display_service = SessionDisplayService()  # Updated class name
    
    @require_authentication
    def get(self, request):
        """Get combined session and audit logs"""
        try:
            # Get query parameters with validation
            limit = min(int(request.query_params.get('limit', 100)), 500)  # Max 500
            log_type = request.query_params.get('type', 'all')
            
            # Validate log_type
            if log_type not in ['all', 'session', 'audit']:
                return Response({
                    'success': False,
                    'error': 'Invalid log type. Must be: all, session, or audit'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Getting {log_type} logs (limit: {limit}) for user {request.current_user.get('username')}")
            
            # Use the optimized service method
            result = self.display_service.get_combined_logs(limit=limit, log_type=log_type)
            
            logger.info(f"Returning {len(result.get('data', []))} logs")
            return Response(result, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.warning(f"Invalid parameter in CombinedLogsView: {e}")
            return Response({
                'success': False,
                'error': 'Invalid parameters provided'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error in CombinedLogsView: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SessionCleanupView(APIView):
    """Admin endpoint for cleaning up old sessions"""
    
    def __init__(self):
        self.session_service = SessionLogService()
    
    @require_admin
    def post(self, request):
        """Clean up old sessions"""
        try:
            # Get days parameter with default
            days_old = int(request.data.get('days_old', 30))
            
            # Validate days parameter
            if days_old < 1 or days_old > 365:
                return Response({
                    'success': False,
                    'error': 'days_old must be between 1 and 365'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            deleted_count = self.session_service.cleanup_old_sessions(days_old=days_old)
            
            return Response({
                'success': True,
                'message': f'Cleaned up {deleted_count} old sessions',
                'deleted_count': deleted_count
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': 'Invalid days_old parameter'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error in SessionCleanupView: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ForceLogoutView(APIView):
    """Admin endpoint to force logout a user"""
    
    def __init__(self):
        self.session_service = SessionLogService()
    
    @require_admin
    def post(self, request, user_id):
        """Force logout a specific user"""
        try:
            result = self.session_service.log_logout(user_id, reason="admin_forced")
            
            if result.get('success'):
                return Response({
                    'success': True,
                    'message': f'User {user_id} logged out successfully',
                    'duration': result.get('duration', 0)
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': result.get('message', 'Failed to logout user')
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            logger.error(f"Error in ForceLogoutView: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

