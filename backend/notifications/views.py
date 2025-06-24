# notifications/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .services import notification_service

@api_view(['POST'])
def create_notification(request):
    """Create a new notification"""
    try:
        data = request.data
        
        # Required fields
        title = data.get('title')
        message = data.get('message')
        
        if not title or not message:
            return Response({
                'success': False,
                'message': 'title and message are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Optional fields
        recipient_id = data.get('recipient_id')
        recipient_username = data.get('recipient_username')
        priority = data.get('priority', 'medium')
        notification_type = data.get('notification_type', 'system')
        metadata = data.get('metadata', {})
        
        # Validate recipient (now optional)
        if not recipient_id and not recipient_username:
            # Allow notifications without recipients
            pass
        
        notification = notification_service.create_notification(
            title=title,
            message=message,
            recipient_id=recipient_id,
            recipient_username=recipient_username,
            priority=priority,
            notification_type=notification_type,
            metadata=metadata
        )
        
        return Response({
            'success': True,
            'message': 'Notification created successfully',
            'data': notification
        }, status=status.HTTP_201_CREATED)
        
    except ValueError as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error creating notification: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def list_notifications(request):
    """List notifications with optional filters"""
    try:
        recipient_id = request.query_params.get('recipient_id')
        notification_type = request.query_params.get('type')
        is_read = request.query_params.get('is_read')
        limit = int(request.query_params.get('limit', 50))
        
        # Convert is_read string to boolean
        if is_read is not None:
            is_read = is_read.lower() in ['true', '1', 'yes']
        
        notifications = notification_service.get_notifications(
            recipient_id=recipient_id,
            notification_type=notification_type,
            is_read=is_read,
            limit=limit
        )
        
        return Response({
            'success': True,
            'count': len(notifications),
            'data': notifications
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error retrieving notifications: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_notification(request, notification_id):
    """Get a specific notification"""
    try:
        notification = notification_service.get_notification_by_id(notification_id)
        
        if not notification:
            return Response({
                'success': False,
                'message': 'Notification not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'data': notification
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error retrieving notification: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_inventory_alert(request):
    """Create an inventory alert notification"""
    try:
        recipient_id = request.data.get('recipient_id')
        product_id = request.data.get('product_id')
        current_stock = request.data.get('current_stock')
        product_name = request.data.get('product_name', 'Product')
        
        if not all([recipient_id, product_id, current_stock is not None]):
            return Response({
                'success': False,
                'message': 'recipient_id, product_id, and current_stock are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        notification = notification_service.create_inventory_alert(
            recipient_id=recipient_id,
            product_id=product_id,
            current_stock=current_stock,
            product_name=product_name
        )
        
        return Response({
            'success': True,
            'message': 'Inventory alert created successfully',
            'data': notification
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error creating inventory alert: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        success = notification_service.mark_as_read(notification_id)
        
        if not success:
            return Response({
                'success': False,
                'message': 'Notification not found or already read'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'message': 'Notification marked as read'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error marking notification as read: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def user_notifications(request, user_id):
    """Get all notifications for a specific user"""
    try:
        # Verify user exists
        user = get_object_or_404(User, id=user_id)
        
        is_read = request.query_params.get('is_read')
        if is_read is not None:
            is_read = is_read.lower() in ['true', '1', 'yes']
        
        notifications = notification_service.get_notifications(
            recipient_id=user_id,
            is_read=is_read
        )
        
        unread_count = notification_service.get_unread_count(user_id)
        
        return Response({
            'success': True,
            'user': user.username,
            'total_count': len(notifications),
            'unread_count': unread_count,
            'data': notifications
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error retrieving user notifications: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def recent_notifications(request):
    """Get recent notifications (last 24 hours or last 10 notifications)"""
    try:
        # Get last 10 recent notifications by default
        limit = int(request.query_params.get('limit', 10))
        
        # Optional: filter by time (last 24 hours)
        hours = request.query_params.get('hours')
        
        notifications = notification_service.get_recent_notifications(
            limit=limit,
            hours=int(hours) if hours else None
        )
        
        return Response({
            'success': True,
            'message': f'Retrieved {len(notifications)} recent notifications',
            'count': len(notifications),
            'data': notifications
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error retrieving recent notifications: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def all_notifications(request):
    """Get all notifications (paginated)"""
    try:
        # Pagination parameters
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 50))
        
        # Calculate skip for pagination
        skip = (page - 1) * limit
        
        notifications, total_count = notification_service.get_all_notifications(
            skip=skip,
            limit=limit
        )
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit  # Ceiling division
        has_next = page < total_pages
        has_prev = page > 1
        
        return Response({
            'success': True,
            'message': f'Retrieved {len(notifications)} notifications (page {page} of {total_pages})',
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_count': total_count,
                'per_page': limit,
                'has_next': has_next,
                'has_previous': has_prev
            },
            'data': notifications
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error retrieving all notifications: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_notification(request, notification_id):
    """Delete a notification"""
    try:
        success = notification_service.delete_notification(notification_id)
        
        if not success:
            return Response({
                'success': False,
                'message': 'Notification not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'message': 'Notification deleted successfully'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error deleting notification: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)