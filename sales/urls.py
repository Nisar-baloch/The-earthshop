# sales/urls.py
from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('create/', views.create_invoice, name='create_invoice'),
    path('list/', views.invoice_list, name='invoice_list'),
    path('detail/<int:pk>/', views.invoice_detail, name='invoice_detail'),

    # installments
    path('installments/<int:invoice_id>/', views.installment_list, name='installment_list'),
    path('installments/<int:invoice_id>/add/', views.installment_add, name='installment_add'),
]


