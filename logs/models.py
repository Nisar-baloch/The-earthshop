from django.db import models
from django.utils import timezone

class StockLog(models.Model):
    LOG_TYPE_CHOICES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
    ]
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    log_type = models.CharField(max_length=10, choices=LOG_TYPE_CHOICES)
    quantity = models.IntegerField()
    date = models.DateField(default=timezone.now)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} - {self.log_type} ({self.date})"

class DailyLog(models.Model):
    date = models.DateField(default=timezone.now)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Daily Log - {self.date}"
