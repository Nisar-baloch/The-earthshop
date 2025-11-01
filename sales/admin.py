from django.contrib import admin
from .models import Invoice, InvoiceInstallment

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'payment_type', 'grand_total', 'paid_amount', 'remaining_payment', 'date')
    list_filter = ('payment_type', 'date')
    search_fields = ('customer__name', 'id')

@admin.register(InvoiceInstallment)
class InvoiceInstallmentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'paid_amount', 'date')
    list_filter = ('date',)
