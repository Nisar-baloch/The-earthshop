from django.db import models
from django.utils import timezone

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    payment_method = models.CharField(
        max_length=20,
        choices=[('cash', 'Cash'), ('bank', 'Bank')],
        default='cash'
    )

    def __str__(self):
        return f"{self.description} - {self.amount}"
