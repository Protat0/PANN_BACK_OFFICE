# notifications/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Notification, NotificationType, NotificationSettings

class NotificationTypeSerializer(serializers.ModelSerializer):
    """Serializer for notification types"""
    class Meta:
        model = NotificationType
        fields = ['id', 'name', 'description', 'is_active']

class UserSerializer(serializers.ModelSerializer):
    """Simple user serializer for notifications"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    notification_type = NotificationTypeSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'priority', 
            'priority_display', 'recipient', 'is_global', 'data', 'source',
            'is_read', 'is_active', 'read_at', 'created_at', 'expires_at',
            'time_ago'
        ]
        read_only_fields = [
            'id', 'notification_type', 'recipient', 'created_at', 'read_at'
        ]
    
    def get_time_ago(self, obj):
        """Get human-readable time since notification was created"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications"""
    notification_type_name = serializers.CharField(write_only=True)
    recipient_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'notification_type_name', 'priority',
            'recipient_id', 'is_global', 'data', 'source', 'expires_at'
        ]
    
    def create(self, validated_data):
        notification_type_name = validated_data.pop('notification_type_name')
        recipient_id = validated_data.pop('recipient_id', None)
        
        # Get or create notification type
        notification_type, created = NotificationType.objects.get_or_create(
            name=notification_type_name,
            defaults={'description': f'Auto-created: {notification_type_name}'}
        )
        
        # Get recipient if provided
        recipient = None
        if recipient_id:
            try:
                recipient = User.objects.get(id=recipient_id)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid recipient ID")
        
        validated_data['notification_type'] = notification_type
        validated_data['recipient'] = recipient
        
        return Notification.objects.create(**validated_data)

class NotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for notification settings"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = NotificationSettings
        fields = [
            'id', 'user', 'email_notifications', 'email_stock_alerts',
            'email_system_logs', 'email_error_alerts', 'push_notifications',
            'push_stock_alerts', 'push_system_logs', 'push_error_alerts',
            'digest_frequency', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics"""
    total = serializers.IntegerField()
    unread = serializers.IntegerField()
    high_priority = serializers.IntegerField()
    today = serializers.IntegerField()

class BulkNotificationActionSerializer(serializers.Serializer):
    """Serializer for bulk notification actions"""
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    action = serializers.ChoiceField(choices=['mark_read', 'delete'])
    
    def validate_notification_ids(self, value):
        """Validate that all notification IDs exist"""
        existing_ids = Notification.objects.filter(id__in=value).values_list('id', flat=True)
        missing_ids = set(value) - set(existing_ids)
        
        if missing_ids:
            raise serializers.ValidationError(
                f"Notifications with IDs {list(missing_ids)} do not exist"
            )
        
        return value