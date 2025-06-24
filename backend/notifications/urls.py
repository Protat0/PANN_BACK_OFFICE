# notifications/urls.py
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
     # Recent and All notifications
    path('recent/', views.recent_notifications, name='recent'),
    path('all/', views.all_notifications, name='all'),

    # Basic CRUD operations
    path('create/', views.create_notification, name='create'),
    path('list/', views.list_notifications, name='list'),
    path('<str:notification_id>/', views.get_notification, name='detail'),
    path('<str:notification_id>/delete/', views.delete_notification, name='delete'),
    
    # Specific notification actions
    path('inventory-alert/', views.create_inventory_alert, name='inventory_alert'),
    path('<str:notification_id>/mark-read/', views.mark_notification_read, name='mark_read'),
    
    # User-specific notifications
    path('user/<int:user_id>/', views.user_notifications, name='user_notifications'),
]