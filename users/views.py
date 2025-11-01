from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import logout

def index(request):
    return render(request, 'users/index.html')

def logout_view(request):
    logout(request)
    return redirect('/')
