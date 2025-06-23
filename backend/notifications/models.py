# notifications/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Notification(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    NOTIFICATION_TYPE_CHOICES = [
        ('inventory', 'Inventory'),
        ('order', 'Order'),
        ('payment', 'Payment'),
        ('system', 'System'),
        ('promotion', 'Promotion'),
        ('alert', 'Alert'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    
    # Metadata stored as JSON field
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
            models.Index(fields=['priority']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save(update_fields=['is_read', 'updated_at'])
    
    def mark_as_unread(self):
        """Mark notification as unread"""
        self.is_read = False
        self.save(update_fields=['is_read', 'updated_at'])
    
    @property
    def is_high_priority(self):
        """Check if notification is high priority"""
        return self.priority in ['high', 'urgent']
    
    @classmethod
    def create_inventory_alert(cls, recipient, product_id, current_stock, product_name=None):
        """Helper method to create inventory alerts"""
        title = f"Low Stock Alert"
        message = f"{product_name or 'Product'} is running low"
        
        return cls.objects.create(
            title=title,
            message=message,
            priority='high',
            recipient=recipient,
            notification_type='inventory',
            metadata={
                'product_id': product_id,
                'current_stock': current_stock,
            }
        )


# Optional: Create a manager for common queries
class NotificationManager(models.Manager):
    def unread_for_user(self, user):
        """Get unread notifications for a user"""
        return self.filter(recipient=user, is_read=False)
    
    def high_priority_for_user(self, user):
        """Get high priority notifications for a user"""
        return self.filter(recipient=user, priority__in=['high', 'urgent'])
    
    def by_type_for_user(self, user, notification_type):
        """Get notifications by type for a user"""
        return self.filter(recipient=user, notification_type=notification_type)

# Add the manager to the model (add this line to the Notification class)
# objects = NotificationManager()