from django.contrib import admin
from .models import MonthlyReport

@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ('month', 'year', 'total_sales', 'total_expenses', 'profit_loss', 'generated_at')

# Register your models here.
