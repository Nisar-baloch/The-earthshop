from django.contrib import admin
from .models import StockLog, DailyLog

@admin.register(StockLog)
class StockLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'log_type', 'quantity', 'date')

@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sales', 'total_expenses')

# Register your models here.
