from django.db import models
from django.utils import timezone
# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=200)
    father_name = models.CharField(max_length=200, null=True, blank=True)
    cnic = models.CharField(max_length=200, null=True, blank=True)
    mobile = models.CharField(max_length=200, null=True, blank=True)
    resident = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)

    date = models.DateField(default=timezone.now, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    # name = models.CharField(max_length=200)
    # father_name = models.CharField(max_length=200, null=True, blank=True)
    # phone = models.CharField(max_length=20, blank=True)
    # address = models.TextField(blank=True)
    # balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    

    def __str__(self):
        return self.name
    
    
class Ledger(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="ledgers")
    date = models.DateField()
    detail = models.CharField(max_length=255)
    debit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.customer.name} - {self.date}"
