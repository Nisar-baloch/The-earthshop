from django import forms
from .models import Invoice, InvoiceItem, Installment


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer_name', 'invoice_date', 'total_amount', 'paid_amount', 'status']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Enter customer name'
            }),
            'invoice_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'input input-bordered w-full'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Total amount'
            }),
            'paid_amount': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Paid amount'
            }),
            'status': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
        }


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity', 'price', 'total']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Quantity'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Unit price'
            }),
            'total': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'readonly': 'readonly'
            }),
        }


class InstallmentForm(forms.ModelForm):
    class Meta:
        model = Installment
        fields = ['invoice', 'amount', 'date', 'status']
        widgets = {
            'invoice': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Installment amount'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'input input-bordered w-full'
            }),
            'status': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
        }
