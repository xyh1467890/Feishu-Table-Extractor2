from django.urls import path
from . import views

urlpatterns = [
    path('fetch/', views.fetch_bitable, name='fetch_bitable'),
    path('health/', views.health_check, name='health_check'),
]
