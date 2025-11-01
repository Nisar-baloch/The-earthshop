from django.urls import path
from . import views

app_name = 'logs'

urlpatterns = [
    path('', views.index, name='list'),
    path('daily/', views.daily_logs, name='daily'),
    path('monthly/', views.monthly_logs, name='monthly'),
]
