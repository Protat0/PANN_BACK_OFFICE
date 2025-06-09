from django.shortcuts import render

# Create your views here.
# notifications/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.core.paginator import Paginator
import json

from .models import Notification, NotificationType, NotificationSettings
from .serializers import (
    NotificationSerializer, 
    NotificationSettingsSerializer,
    NotificationCreateSerializer,
    BulkNotificationActionSerializer
)
from .services import NotificationService

class NotificationViewSet(viewsets.ModelViewSet):
    """API ViewSet for notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get notifications for the current user"""
        user = self.request.user
        queryset = NotificationService.get_user_notifications(user)
        
        # Filter by unread status
        unread_only = self.request.query_params.get('unread_only', False)
        if unread_only and unread_only.lower() == 'true':
            queryset = queryset.filter(is_read=False)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by type
        notification_type = self.request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type__name=notification_type)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a specific notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read for the current user"""
        count = NotificationService.mark_notifications_as_read(request.user)
        return Response({'status': f'{count} notifications marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_selected_as_read(self, request):
        """Mark selected notifications as read"""
        notification_ids = request.data.get('notification_ids', [])
        if not notification_ids:
            return Response(
                {'error': 'No notification IDs provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        count = NotificationService.mark_notifications_as_read(
            request.user, notification_ids
        )
        return Response({'status': f'{count} notifications marked as read'})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get notification statistics for the current user"""
        stats = NotificationService.get_notification_stats(request.user)
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent notifications (last 10)"""
        notifications = NotificationService.get_user_notifications(
            request.user, limit=10
        )
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

@method_decorator(csrf_exempt, name='dispatch')
class NotificationSettingsViewSet(viewsets.ModelViewSet):
    """API ViewSet for notification settings"""
    serializer_class = NotificationSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NotificationSettings.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get or create notification settings for the current user"""
        settings, created = NotificationSettings.objects.get_or_create(
            user=self.request.user
        )
        return settings
    
    @action(detail=False, methods=['get'])
    def my_settings(self, request):
        """Get current user's notification settings"""
        settings = self.get_object()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def update_settings(self, request):
        """Update current user's notification settings"""
        settings = self.get_object()
        serializer = self.get_serializer(settings, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Function-based views for traditional Django templates (if needed)
@login_required
def notification_list_view(request):
    """Traditional Django view for notification list"""
    notifications = NotificationService.get_user_notifications(request.user)
    
    # Pagination
    paginator = Paginator(notifications, 20)  # Show 20 notifications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'stats': NotificationService.get_notification_stats(request.user),
    }
    
    return JsonResponse({
        'notifications': [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'priority': n.priority,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat(),
                'notification_type': n.notification_type.name,
            } for n in page_obj
        ],
        'stats': context['stats'],
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'total_pages': paginator.num_pages,
    })

@csrf_exempt
@login_required
def create_notification_ajax(request):
    """AJAX endpoint to create notifications (for admin use)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        notification = NotificationService.create_notification(
            title=data.get('title'),
            message=data.get('message'),
            notification_type=data.get('notification_type'),
            priority=data.get('priority', 'medium'),
            recipient=None if data.get('is_global') else request.user,
            is_global=data.get('is_global', False),
            data=data.get('data', {}),
            source=data.get('source', 'manual'),
        )
        
        if notification:
            return JsonResponse({
                'status': 'success',
                'notification_id': notification.id,
                'message': 'Notification created successfully'
            })
        else:
            return JsonResponse({'error': 'Failed to create notification'}, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)