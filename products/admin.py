
# Register your models here.
from django.contrib import admin
from .models import Category, Product, StockIn, StockOut

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category','quantity', 'stock', 'date')
    list_filter = ('category',)
    search_fields = ('name', 'company')



class StockInAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'stock_quantity', 'buying_price_item', 'total_buying_amount', 'date', 'created_at')
    list_filter = ('date', 'product')
    search_fields = ('product__name',)

@admin.register(StockOut)
class StockOutAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'stock_out_quantity', 'invoice', 'date')
    list_filter = ('date', 'product')
    search_fields = ('product__name',)