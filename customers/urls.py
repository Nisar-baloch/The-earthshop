from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
   
     path('', views.customer_list, name='list'),
    path('add/', views.add_customer, name='add'),
    path('<int:pk>/ledger/', views.customer_ledger, name='ledger'),
    path("<int:pk>/update/", views.customer_update, name="update"), 
    path('<int:pk>/ledger/add/', views.ledger_add_ajax, name='ledger_add'),
    path('<int:pk>/ledger/pay/', views.ledger_pay_ajax, name='ledger_pay'),
]
