from django.shortcuts import render

def index(request):
    return render(request, 'logs/index.html')

def daily_logs(request):
    return render(request, 'logs/daily.html')

def monthly_logs(request):
    return render(request, 'logs/monthly.html')
