from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.index, name='list'),
    path('add/', views.add_expense, name='add'),
]
