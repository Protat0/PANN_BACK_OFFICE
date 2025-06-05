# notifications/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class NotificationType(models.Model):
    """Define different types of notifications"""
    STOCK_ALERT = 'stock_alert'
    SYSTEM_LOG = 'system_log'
    USER_ACTION = 'user_action'
    ERROR_ALERT = 'error_alert'
    
    TYPE_CHOICES = [
        (STOCK_ALERT, 'Stock Alert'),
        (SYSTEM_LOG, 'System Log'),
        (USER_ACTION, 'User Action'),
        (ERROR_ALERT, 'Error Alert'),
    ]
    
    name = models.CharField(max_length=50, choices=TYPE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.get_name_display()

class Notification(models.Model):
    """Main notification model"""
    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_CRITICAL = 'critical'
    
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
        (PRIORITY_CRITICAL, 'Critical'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    
    # Target users (can be specific users or all users)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_global = models.BooleanField(default=False)  # For system-wide notifications
    
    # Metadata
    data = models.JSONField(default=dict, blank=True)  # Store additional context
    source = models.CharField(max_length=100, blank=True)  # Source system/module
    
    # Status tracking
    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type', 'priority']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_priority_display()}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()

class NotificationSettings(models.Model):
    """User preferences for notifications"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Email notifications
    email_notifications = models.BooleanField(default=True)
    email_stock_alerts = models.BooleanField(default=True)
    email_system_logs = models.BooleanField(default=False)
    email_error_alerts = models.BooleanField(default=True)
    
    # In-app notifications
    push_notifications = models.BooleanField(default=True)
    push_stock_alerts = models.BooleanField(default=True)
    push_system_logs = models.BooleanField(default=True)
    push_error_alerts = models.BooleanField(default=True)
    
    # Frequency settings
    digest_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
        ],
        default='immediate'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Settings for {self.user.username}"