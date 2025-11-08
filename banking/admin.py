
from django.contrib import admin
from .models import BankAccount, BankTransaction # Assuming this model is BankAccount

@admin.register(BankAccount)
class BankAdmin(admin.ModelAdmin):
    # FIX: 'account_number' is now assumed to be a field on the BankAccount model
    list_display = ('name', 'account_number', 'current_balance', 'is_active')
    search_fields = ('name', 'account_number')
    readonly_fields = ('created_at',)
    
@admin.register(BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'transaction_type', 'amount', 'date')
    list_filter = ('transaction_type', 'date', 'account')
    date_hierarchy = 'date'






# from django.contrib import admin
# from .models import Bank

# @admin.register(Bank)
# class BankAdmin(admin.ModelAdmin):
#     list_display = ('name', 'account_number', 'branch')
