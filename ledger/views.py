from django.shortcuts import render

def index(request):
    return render(request, 'ledger/index.html')



def ledger(request):
    return render(request, 'ledger/ledger_list.html')