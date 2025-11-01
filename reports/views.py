from django.shortcuts import render

def index(request):
    return render(request, 'reports/index.html')

def monthly_report(request):
    return render(request, 'reports/monthly.html')
