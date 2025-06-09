# notifications/services.py
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import models
from .models import Notification, NotificationType, NotificationSettings
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Service class for handling notifications"""
    
    @staticmethod
    def create_notification(
        title, 
        message, 
        notification_type, 
        priority='medium',
        recipient=None,
        is_global=False,
        data=None,
        source='',
        expires_at=None
    ):
        """Create a new notification"""
        try:
            # Get or create notification type
            if isinstance(notification_type, str):
                notif_type, created = NotificationType.objects.get_or_create(
                    name=notification_type,
                    defaults={'description': f'Auto-created type: {notification_type}'}
                )
            else:
                notif_type = notification_type
            
            notification = Notification.objects.create(
                title=title,
                message=message,
                notification_type=notif_type,
                priority=priority,
                recipient=recipient,
                is_global=is_global,
                data=data or {},
                source=source,
                expires_at=expires_at
            )
            
            # Send immediate notifications if required
            NotificationService._process_immediate_notifications(notification)
            
            return notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return None
    
    @staticmethod
    def create_stock_alert(product_name, current_stock, threshold, user=None):
        """Create stock-specific alert"""
        title = f"Low Stock Alert: {product_name}"
        message = f"Stock for {product_name} is running low. Current: {current_stock}, Threshold: {threshold}"
        
        data = {
            'product_name': product_name,
            'current_stock': current_stock,
            'threshold': threshold,
            'alert_type': 'low_stock'
        }
        
        return NotificationService.create_notification(
            title=title,
            message=message,
            notification_type=NotificationType.STOCK_ALERT,
            priority='high' if current_stock == 0 else 'medium',
            recipient=user,
            is_global=user is None,
            data=data,
            source='inventory_system'
        )
    
    @staticmethod
    def create_system_log_alert(log_level, log_message, source_module):
        """Create system log alert"""
        priority_map = {
            'ERROR': 'high',
            'CRITICAL': 'critical',
            'WARNING': 'medium',
            'INFO': 'low'
        }
        
        title = f"System {log_level}: {source_module}"
        
        return NotificationService.create_notification(
            title=title,
            message=log_message,
            notification_type=NotificationType.SYSTEM_LOG,
            priority=priority_map.get(log_level, 'medium'),
            is_global=True,
            data={'log_level': log_level, 'module': source_module},
            source=source_module
        )
    
    @staticmethod
    def get_user_notifications(user, unread_only=False, limit=None):
        """Get notifications for a specific user"""
        queryset = Notification.objects.filter(
            models.Q(recipient=user) | models.Q(is_global=True)
        )
        
        if unread_only:
            queryset = queryset.filter(is_read=False)
        
        if limit:
            queryset = queryset[:limit]
            
        return queryset
    
    @staticmethod
    def _process_immediate_notifications(notification):
        """Process immediate notifications (email/SMS)"""
        try:
            # Get user settings if notification has a specific recipient
            if notification.recipient:
                settings, created = NotificationSettings.objects.get_or_create(
                    user=notification.recipient
                )
                
                # Send email if enabled
                if settings.email_notifications and NotificationService._should_send_email(notification, settings):
                    NotificationService._send_email_notification(notification)
                
                # Send SMS if enabled and high priority
                if notification.priority in ['high', 'critical']:
                    NotificationService._send_sms_notification(notification)
            
            # For global notifications, send to all admin users
            elif notification.is_global and notification.priority in ['high', 'critical']:
                from django.contrib.auth.models import User
                admin_users = User.objects.filter(is_staff=True)
                for admin in admin_users:
                    NotificationService._send_email_notification(notification, admin)
                    
        except Exception as e:
            logger.error(f"Error processing immediate notifications: {e}")
    
    @staticmethod
    def _should_send_email(notification, settings):
        """Determine if email should be sent based on notification type and user settings"""
        type_mapping = {
            NotificationType.STOCK_ALERT: settings.email_stock_alerts,
            NotificationType.SYSTEM_LOG: settings.email_system_logs,
            NotificationType.ERROR_ALERT: settings.email_error_alerts,
        }
        return type_mapping.get(notification.notification_type.name, settings.email_notifications)
    
    @staticmethod
    def _send_email_notification(notification, user=None):
        """Send email notification using SendGrid"""
        try:
            recipient = user or notification.recipient
            if not recipient or not recipient.email:
                return
            
            subject = f"[PANN Alert] {notification.title}"
            message = f"""
            {notification.message}
            
            Priority: {notification.get_priority_display()}
            Time: {notification.created_at.strftime('%Y-%m-%d %H:%M:%S')}
            Source: {notification.source or 'System'}
            
            ---
            PANN - Ramyeon Food Corner
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@ramyeonfoodcorner.com'),
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            
            logger.info(f"Email sent successfully to {recipient.email}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    @staticmethod
    def _send_sms_notification(notification):
        """Send SMS notification using Twilio (placeholder for future implementation)"""
        try:
            # Placeholder for Twilio SMS integration
            # This will be implemented when you set up Twilio
            logger.info(f"SMS notification queued: {notification.title}")
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {e}")
    
    @staticmethod
    def mark_notifications_as_read(user, notification_ids=None):
        """Mark notifications as read for a user"""
        try:
            queryset = Notification.objects.filter(
                models.Q(recipient=user) | models.Q(is_global=True),
                is_read=False
            )
            
            if notification_ids:
                queryset = queryset.filter(id__in=notification_ids)
            
            count = queryset.update(
                is_read=True,
                read_at=timezone.now()
            )
            
            return count
            
        except Exception as e:
            logger.error(f"Error marking notifications as read: {e}")
            return 0
    
    @staticmethod
    def get_notification_stats(user=None):
        """Get notification statistics"""
        try:
            if user:
                queryset = Notification.objects.filter(
                    models.Q(recipient=user) | models.Q(is_global=True)
                )
            else:
                queryset = Notification.objects.all()
            
            return {
                'total': queryset.count(),
                'unread': queryset.filter(is_read=False).count(),
                'high_priority': queryset.filter(priority__in=['high', 'critical']).count(),
                'today': queryset.filter(
                    created_at__date=timezone.now().date()
                ).count(),
            }
            
        except Exception as e:
            logger.error(f"Error getting notification stats: {e}")
            return {'total': 0, 'unread': 0, 'high_priority': 0, 'today': 0}