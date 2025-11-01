from django.shortcuts import render
from .models import Bank


def add_bank(request):
    return render(request, 'banking/add_bank.html')

def bank_list(request):
    banks = Bank.objects.all()
    return render(request, 'banking/bank_list.html', {'banks': banks})
