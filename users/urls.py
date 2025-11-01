from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.index, name='list'),
    path('logout/', views.logout_view, name='logout'),
]
