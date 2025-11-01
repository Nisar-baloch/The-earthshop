# banking/models.py
from django.db import models
from django.db.models import Sum

# Create your models here.

class Bank(models.Model):
    name = models.CharField(max_length=200)
    branch = models.CharField(max_length=200, null=True, blank=True)
    # fixed: changed reference from 'banking_system.Bank' to 'banking.Bank' (your app name)
    # NOTE: if `account` should be another model (Account), replace 'banking.Bank' accordingly.
    account_number = models.ForeignKey('banking.Bank', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def bank_balance(self):
        # uses related_name from BankDetail (assumes BankDetail has FK to Bank with related_name='bank_detail')
        bank_details = self.bank_detail.all()  # ensure BankDetail model sets related_name='bank_detail'
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
    bank = models.ForeignKey('banking.Bank', related_name='bank_detail', on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
   

    def __str__(self):
        return self.name

    
    


# class Bank(models.Model):
#     name = models.CharField(max_length=200)
#     account_number = models.CharField(max_length=50)
#     opening_balance = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return self.name
