from django.urls import path
from . import views

app_name = 'banking'

urlpatterns = [
    
     path('add/', views.add_bank, name='add'),
    path('list/', views.bank_list, name='list'),
    path('update/<int:pk>/', views.add_bank, name='update'), 
    path('view/<int:pk>/', views.add_bank, name='view'), 
]
