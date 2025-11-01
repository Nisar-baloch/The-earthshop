from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone

class LedgerEntry(models.Model):
    ENTITY_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('company', 'Company'),
    ]
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPE_CHOICES)
    entity_name = models.CharField(max_length=200)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # money in
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0) # money out
    payment_method = models.CharField(
        max_length=20,
        choices=[('cash', 'Cash'), ('bank', 'Bank'), ('credit', 'Credit')],
        default='cash'
    )

    def balance(self):
        return self.debit - self.credit

    def __str__(self):
        return f"{self.entity_type} - {self.entity_name} ({self.date})"
