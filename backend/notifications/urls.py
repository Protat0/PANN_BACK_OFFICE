# notifications/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router for DRF ViewSets
router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'notification-settings', views.NotificationSettingsViewSet, basename='notification-settings')

app_name = 'notifications'

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Traditional Django views (if needed for admin interface)
    path('list/', views.notification_list_view, name='notification_list'),
    path('create/', views.create_notification_ajax, name='create_notification'),
]