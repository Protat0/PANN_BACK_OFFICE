# notifications/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Notification, NotificationType, NotificationSettings

@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['name']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'notification_type', 'priority', 'recipient_display', 
        'is_global', 'is_read', 'created_at', 'source'
    ]
    list_filter = [
        'notification_type', 'priority', 'is_global', 'is_read', 
        'created_at', 'source'
    ]
    search_fields = ['title', 'message', 'source']
    readonly_fields = ['created_at', 'read_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'message', 'notification_type', 'priority')
        }),
        ('Recipients', {
            'fields': ('recipient', 'is_global')
        }),
        ('Metadata', {
            'fields': ('source', 'data', 'expires_at')
        }),
        ('Status', {
            'fields': ('is_active', 'is_read', 'read_at', 'created_at')
        }),
    )
    
    def recipient_display(self, obj):
        """Display recipient information"""
        if obj.is_global:
            return format_html('<span style="color: green;">Global</span>')
        elif obj.recipient:
            return obj.recipient.username
        return 'No recipient'
    recipient_display.short_description = 'Recipient'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related(
            'notification_type', 'recipient'
        )
    
    actions = ['mark_as_read', 'mark_as_unread', 'delete_old_notifications']
    
    def mark_as_read(self, request, queryset):
        """Admin action to mark notifications as read"""
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = 'Mark selected notifications as read'
    
    def mark_as_unread(self, request, queryset):
        """Admin action to mark notifications as unread"""
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = 'Mark selected notifications as unread'
    
    def delete_old_notifications(self, request, queryset):
        """Admin action to delete old notifications"""
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=30)
        old_notifications = queryset.filter(created_at__lt=cutoff_date)
        count = old_notifications.count()
        old_notifications.delete()
        self.message_user(request, f'{count} old notifications deleted.')
    delete_old_notifications.short_description = 'Delete notifications older than 30 days'

@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'email_notifications', 'push_notifications', 
        'digest_frequency', 'updated_at'
    ]
    list_filter = [
        'email_notifications', 'push_notifications', 'digest_frequency',
        'email_stock_alerts', 'email_error_alerts'
    ]
    search_fields = ['user__username', 'user__email']
    ordering = ['user__username']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Notifications', {
            'fields': (
                'email_notifications', 'email_stock_alerts', 
                'email_system_logs', 'email_error_alerts'
            )
        }),
        ('Push Notifications', {
            'fields': (
                'push_notifications', 'push_stock_alerts',
                'push_system_logs', 'push_error_alerts'
            )
        }),
        ('Settings', {
            'fields': ('digest_frequency',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('user')