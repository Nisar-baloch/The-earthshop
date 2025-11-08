
from django import forms
from .models import Category, Product, StockIn, StockOut

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'name', 'stock', 'quantity',
            'buying_price',  'date'
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'name': forms.TextInput(attrs={'class': 'input input-bordered', 'placeholder': 'Product name'}),
            'stock': forms.NumberInput(attrs={'class': 'input input-bordered', 'min': '0'}),
            'quantity': forms.NumberInput(attrs={'class': 'input input-bordered', 'min': '0'}),
            'buying_price': forms.NumberInput(attrs={'class': 'input input-bordered', 'step': '0.01', 'min': '0'}),
            
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'input input-bordered'}),
        }

class StockInForm(forms.ModelForm):
    class Meta:
        model = StockIn
        fields = [
            'product',
            'buying_price_item',
            'buying_percent',
            'stock_quantity',
            # new selling fields:
            'selling_price_item',
            # totals stored in model will be auto-filled on save
            'date'
        ]
        widgets = {
            'product': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'buying_price_item': forms.NumberInput(attrs={'class': 'input input-bordered', 'step': '0.01'}),
            'buying_percent': forms.NumberInput(attrs={'class': 'input input-bordered', 'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'input input-bordered', 'step': '0.01'}),
            'selling_price_item': forms.NumberInput(attrs={'class': 'input input-bordered', 'step': '0.01'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class':'input input-bordered'}),
        }


class StockOutForm(forms.ModelForm):
    class Meta:
        model = StockOut
        fields = ['stock_out_quantity', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'input input-bordered w-full'}),
            'stock_out_quantity': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'min': '1'}),
        }