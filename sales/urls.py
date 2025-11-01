
from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.InvoiceListView.as_view(), name='invoice_list'),
    path('create/', views.CreateInvoiceTemplateView.as_view(), name='create_invoice'),
    path('<int:pk>/detail/', views.InvoiceDetailTemplateView.as_view(), name='invoice_detail'),

    # Installment URLs
    path('<int:invoice_id>/installments/', views.InvoiceInstallmentListView.as_view(), name='installment_list'),
    path('<int:invoice_id>/installments/add/', views.InvoiceInstallmentFormView.as_view(), name='installment_add'),
    path('installments/<int:pk>/delete/', views.InvoiceInstallmentDeleteView.as_view(), name='installment_delete'),

]