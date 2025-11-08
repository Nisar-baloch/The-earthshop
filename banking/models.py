from django.db import models
from django.utils import timezone
from django.db.models import Sum

# Create your models here.

class Bank(models.Model):
    name = models.CharField(max_length=200)
    branch = models.CharField(max_length=200, null=True, blank=True)
    account_number = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

    def bank_balance(self):
        # Uses related_name from BankDetail
        bank_details = self.bank_detail.all() 
        if bank_details:
            debit = bank_details.aggregate(Sum('debit'))
            credit = bank_details.aggregate(Sum('credit'))

            debit_amount = debit.get('debit__sum') or 0
            credit_amount = credit.get('credit__sum') or 0
        else:
            debit_amount = 0
            credit_amount = 0

        balance = credit_amount - debit_amount
        return balance


class BankDetail(models.Model):
    bank = models.ForeignKey(Bank, related_name='bank_detail', on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    name = models.CharField(max_length=100, default='Detail Entry') # Added name field for simplicity

    def __str__(self):
        return f"Detail for {self.bank.name}"

    
class BankAccount(models.Model):
    """Represents a bank account where business funds are held. Used in Sales/Expenses."""
    name = models.CharField(max_length=100, help_text="e.g., Cash Drawer, Commercial Bank Account")
    account_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True) # <<< FIX for admin.E035

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class BankTransaction(models.Model):
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=[('IN', 'Deposit'), ('OUT', 'Withdrawal')])
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type} {self.amount} on {self.date}"