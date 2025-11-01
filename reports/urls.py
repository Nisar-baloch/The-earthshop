from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.index, name='list'),
    path('monthly/', views.monthly_report, name='monthly'),
]
