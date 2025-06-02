from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.pos_status, name='pos_status'),
]