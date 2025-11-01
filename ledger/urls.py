from django.urls import path
from . import views

app_name = 'ledger'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>/ledger/', views.ledger, name='list'),
]
