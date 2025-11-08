from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
   
    # Categories
    path('add-category/', views.add_category, name='add_category'),
   

    # Products
    path('list/', views.product_list, name='product_list'),
    path('add-product/', views.add_product, name='add_product'),
    path('update/<int:pk>/', views.update_product, name='update_product'),
    path('delete/<int:pk>/', views.delete_product, name='delete_product'),
        # Global stockin/out pages
    path('add-stock/', views.add_stock, name='add_stock'),
    path('stockin/', views.stockin_list, name='stockin_list'),
    path('stockin/<int:pk>/', views.stockin_detail, name='stockin_detail'),

   path('product/<int:product_id>/stockout/add/', views.add_stock_out, name='add_stock_out'),

    path('stockout/', views.stockout_list, name='stockout_list'),
    path('stockout/<int:pk>/', views.stockout_detail, name='stockout_detail'),

    # Product-specific stock lists
    path('product/<int:product_id>/stockin/', views.product_stockins, name='product_stockins'),
path('product/<int:product_id>/stockout/', views.product_stockouts, name='product_stockouts'),
path('product/<int:product_id>/stockout/add/', views.add_stock_out, name='add_stock_out'),

]
