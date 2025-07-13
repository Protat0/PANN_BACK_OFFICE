# notifications/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    recipient_username = serializers.CharField(write_only=True, required=False)
    recipient_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'priority', 'recipient', 
            'recipient_username', 'recipient_id', 'is_read', 
            'created_at', 'updated_at', 'notification_type', 'metadata'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'recipient': {'required': False}  # Make recipient not required
        }
    
    def validate(self, data):
        """Validate that either recipient, recipient_id, or recipient_username is provided"""
        recipient = data.get('recipient')
        recipient_id = data.get('recipient_id')
        recipient_username = data.get('recipient_username')
        
        if not any([recipient, recipient_id, recipient_username]):
            raise serializers.ValidationError(
                "Either recipient, recipient_id, or recipient_username must be provided"
            )
        
        return data
    
    def create(self, validated_data):
        """Handle recipient lookup and creation"""
        recipient_username = validated_data.pop('recipient_username', None)
        recipient_id = validated_data.pop('recipient_id', None)
        
        # If recipient is not directly provided, look it up
        if not validated_data.get('recipient'):
            if recipient_username:
                try:
                    recipient = User.objects.get(username=recipient_username)
                    validated_data['recipient'] = recipient
                except User.DoesNotExist:
                    raise serializers.ValidationError(
                        f"User with username '{recipient_username}' does not exist"
                    )
            elif recipient_id:
                try:
                    recipient = User.objects.get(id=recipient_id)
                    validated_data['recipient'] = recipient
                except User.DoesNotExist:
                    raise serializers.ValidationError(
                        f"User with id '{recipient_id}' does not exist"
                    )
        
        return super().create(validated_data)

class NotificationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing notifications"""
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'priority', 'recipient_username',
            'is_read', 'created_at', 'notification_type'
        ]