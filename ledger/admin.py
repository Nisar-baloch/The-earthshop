from django.contrib import admin
from .models import LedgerEntry

@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ('entity_type', 'entity_name', 'date', 'debit', 'credit', 'payment_method')
    list_filter = ('entity_type', 'payment_method')

# Register your models here.
