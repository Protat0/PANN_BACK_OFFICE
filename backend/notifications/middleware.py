# notifications/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
import logging

logger = logging.getLogger(__name__)

class NotificationMiddleware(MiddlewareMixin):
    """
    Middleware to add notification count to request context for Vue.js
    """
    
    def process_request(self, request):
        # Add notification stats to request for authenticated users
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            try:
                from .services import NotificationService
                request.notification_stats = NotificationService.get_notification_stats(request.user)
            except Exception as e:
                logger.error(f"Error getting notification stats: {e}")
                request.notification_stats = {'total': 0, 'unread': 0, 'high_priority': 0, 'today': 0}
        else:
            request.notification_stats = {'total': 0, 'unread': 0, 'high_priority': 0, 'today': 0}