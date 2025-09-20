from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from ..services.session_services import SessionLogService, SessionDisplayService
from ..services.customer_service import CustomerService
from ..services.product_service import ProductService
from ..services.user_service import UserService
from ..decorators.authenticationDecorator import require_authentication, require_admin
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# ================ CORE SESSION VIEWS ================

class SessionLogsView(APIView):
    """Get session logs with filtering options"""
    
    def __init__(self):
        self.session_service = SessionLogService()
    
    @require_authentication
    def get(self, request):
        """Get session logs with filtering"""
        try:
            limit = int(request.query_params.get('limit', 100))
            status_filter = request.query_params.get('status', None)
            user_filter = request.query_params.get('user', None)
            
            # Use display service for formatted output
            display_service = SessionDisplayService()
            result = display_service.get_session_logs(
                limit=limit, 
                status_filter=status_filter,
                user_filter=user_filter
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in SessionLogsView: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SessionDetailView(APIView):
    """Get specific session details"""
    
    def __init__(self):
        self.session_service = SessionLogService()
    
    @require_authentication
    def get(self, request, session_id):
        """Get specific session by session_id (SESS-#####)"""
        try:
            session = self.session_service.get_session_by_id(session_id)
            
            if not session:
                return Response({
                    'success': False,
                    'error': f'Session {session_id} not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check permissions - users can only view their own sessions
            current_user = request.current_user
            if (current_user.get('user_id') != session.get('user_id') and 
                current_user.get('role') != 'admin'):
                return Response({
                    'success': False,
                    'error': 'Permission denied'
                }, status=status.HTTP_403_FORBIDDEN)
            
            return Response({
                'success': True,
                'data': session
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in SessionDetailView: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActiveSessionsView(APIView):
    """Get all currently active sessions"""
    
    def __init__(self):
        self.session_service = SessionLogService()
    
    @require_admin
    def get(self, request):
        """Get all active sessions - admin only"""
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
            limit = int(request.query_params.get('limit', 50))
            
            # Permission check
            current_user = request.current_user
            if (current_user.get('user_id') != user_id and 
                current_user.get('role') != 'admin'):
                return Response({
                    'success': False,
                    'error': 'Permission denied. You can only view your own sessions.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            sessions = self.session_service.get_user_sessions(user_id, limit=limit)
            return Response({
                'success': True,
                'data': sessions,
                'count': len(sessions),
                'user_id': user_id
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

# ================ CLEANUP AND ADMIN VIEWS ================

class SessionCleanupView(APIView):
    """Manual session cleanup with export"""
    
    def __init__(self):
        self.session_service = SessionLogService()
    
    @require_admin
    def post(self, request):
        """Manual cleanup with date range and CSV export"""
        try:
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            export_path = request.data.get('export_path')
            dry_run = request.data.get('dry_run', False)
            
            # Validate dates if provided
            if start_date:
                try:
                    datetime.fromisoformat(start_date)
                except ValueError:
                    return Response({
                        'success': False,
                        'error': 'Invalid start_date format. Use ISO format (YYYY-MM-DD)'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            if end_date:
                try:
                    datetime.fromisoformat(end_date)
                except ValueError:
                    return Response({
                        'success': False,
                        'error': 'Invalid end_date format. Use ISO format (YYYY-MM-DD)'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Perform cleanup with export
            result = self.session_service.manual_cleanup_with_export(
                start_date=start_date,
                end_date=end_date,
                export_path=export_path,
                dry_run=dry_run
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in SessionCleanupView: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CleanupStatusView(APIView):
    """Get cleanup status and preview"""
    
    def __init__(self):
        self.session_service = SessionLogService()
    
    @require_admin
    def get(self, request):
        """Get cleanup status and what would be cleaned"""
        try:
            status_data = self.session_service.get_cleanup_status()
            preview_data = self.session_service.get_cleanup_preview()
            
            return Response({
                'success': True,
                'status': status_data,
                'preview': preview_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in CleanupStatusView: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AutoCleanupControlView(APIView):
    """Control automated cleanup system"""
    
    def __init__(self):
        self.session_service = SessionLogService()
    
    @require_admin
    def post(self, request):
        """Start automated cleanup"""
        try:
            action = request.data.get('action', 'start')
            cleanup_interval_hours = int(request.data.get('cleanup_interval_hours', 720))  # Default monthly
            months_old = int(request.data.get('months_old', 6))
            
            if action == 'start':
                result = self.session_service.start_automated_cleanup(
                    cleanup_interval_hours=cleanup_interval_hours,
                    months_old=months_old
                )
            elif action == 'stop':
                result = self.session_service.stop_automated_cleanup()
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid action. Use "start" or "stop"'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': 'Invalid parameter values'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error in AutoCleanupControlView: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SessionExportView(APIView):
    """Export session data to CSV"""
    
    def __init__(self):
        self.display_service = SessionDisplayService()
    
    @require_admin
    def post(self, request):
        """Export session logs to CSV"""
        try:
            export_format = request.data.get('format', 'csv')
            date_filter = request.data.get('date_filter')
            status_filter = request.data.get('status_filter')
            
            # Validate date filter if provided
            if date_filter:
                try:
                    if 'start_date' in date_filter:
                        datetime.fromisoformat(date_filter['start_date'])
                    if 'end_date' in date_filter:
                        datetime.fromisoformat(date_filter['end_date'])
                except ValueError:
                    return Response({
                        'success': False,
                        'error': 'Invalid date format in date_filter'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            result = self.display_service.export_session_logs(
                export_format=export_format,
                date_filter=date_filter,
                status_filter=status_filter
            )
            
            if result['success']:
                # Return CSV as file download
                if export_format == 'csv':
                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = f'attachment; filename="session_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
                    
                    # Write CSV data
                    import csv
                    import io
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=[
                        'session_id', 'user_id', 'username', 'login_time', 
                        'logout_time', 'duration', 'status', 'branch_id', 
                        'ip_address', 'logout_reason'
                    ])
                    writer.writeheader()
                    for row in result['data']:
                        writer.writerow(row)
                    
                    response.write(output.getvalue())
                    return response
                else:
                    return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"Error in SessionExportView: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ================ ADMIN CONTROL VIEWS ================

class ForceLogoutView(APIView):
    """Force logout specific users"""
    
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
                    'duration': result.get('duration', 0),
                    'session_id': result.get('session_id')
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

class BulkSessionControlView(APIView):
    """Bulk session operations"""
    
    def __init__(self):
        self.session_service = SessionLogService()
    
    @require_admin
    def post(self, request):
        """Bulk expire sessions for multiple users"""
        try:
            action = request.data.get('action', 'expire')
            user_ids = request.data.get('user_ids', [])
            
            if not user_ids or not isinstance(user_ids, list):
                return Response({
                    'success': False,
                    'error': 'user_ids must be a non-empty list'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if action == 'expire':
                result = self.session_service.bulk_expire_user_sessions(user_ids)
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid action. Only "expire" is supported'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error in BulkSessionControlView: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ================ DISPLAY AND LOGGING VIEWS ================

class SessionDisplayView(APIView):
    """Get formatted session logs for display"""
    
    def __init__(self):
        self.display_service = SessionDisplayService()
    
    @require_authentication
    def get(self, request):
        """Get formatted session logs"""
        try:
            limit = int(request.query_params.get('limit', 100))
            status_filter = request.query_params.get('status', None)
            user_filter = request.query_params.get('user', None)
            
            result = self.display_service.get_session_logs(
                limit=limit, 
                status_filter=status_filter,
                user_filter=user_filter
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
        self.display_service = SessionDisplayService()
    
    @require_authentication
    def get(self, request):
        """Get combined session and audit logs"""
        try:
            limit = min(int(request.query_params.get('limit', 100)), 500)
            log_type = request.query_params.get('type', 'all')
            
            if log_type not in ['all', 'session', 'audit']:
                return Response({
                    'success': False,
                    'error': 'Invalid log type. Must be: all, session, or audit'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            result = self.display_service.get_combined_logs(limit=limit, log_type=log_type)
            return Response(result, status=status.HTTP_200_OK)
            
        except ValueError as e:
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

# ================ SYSTEM STATUS VIEW ================

class SystemStatusView(APIView):
    """Get comprehensive system status"""
    
    def __init__(self):
        self.user_service = UserService()
        self.customer_service = CustomerService()
        self.product_service = ProductService()
        self.session_service = SessionLogService()
    
    @require_authentication
    def get(self, request):
        """Get system status with statistics"""
        try:
            session_stats = self.session_service.get_session_statistics()
            cleanup_status = self.session_service.get_cleanup_status()
            
            # Get counts efficiently
            users = self.user_service.get_all_users()
            customers = self.customer_service.get_all_customers()
            products = self.product_service.get_all_products()
            
            return Response({
                "system": "PANN User Management System",
                "status": "operational",
                "version": "2.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "statistics": {
                    "total_users": len(users),
                    "total_customers": len(customers), 
                    "total_products": len(products),
                    "active_sessions": session_stats.get('active_sessions', 0),
                    "today_sessions": session_stats.get('today_sessions', 0),
                    "avg_session_duration": session_stats.get('avg_session_duration', 0)
                },
                "cleanup_status": {
                    "automated_cleanup_running": cleanup_status.get('automated_cleanup_running', False),
                    "sessions_older_than_6_months": cleanup_status.get('sessions_older_than_6_months', 0),
                    "cleanup_schedule": cleanup_status.get('cleanup_schedule', 'Not scheduled')
                },
                "endpoints": {
                    "session_logs": "/api/v1/session-logs/",
                    "active_sessions": "/api/v1/sessions/active/",
                    "session_cleanup": "/api/v1/sessions/cleanup/",
                    "cleanup_status": "/api/v1/sessions/cleanup/status/",
                    "session_export": "/api/v1/sessions/export/",
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