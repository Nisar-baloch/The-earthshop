from django.db import models
from django.utils import timezone

class MonthlyReport(models.Model):
    month = models.IntegerField()  # 1-12
    year = models.IntegerField()
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profit_loss = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    generated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.month}/{self.year} - Profit: {self.profit_loss}"

# Create your models here.
