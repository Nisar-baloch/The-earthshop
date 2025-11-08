# sales/forms.py
from django import forms
from .models import Invoice, InvoiceItem, InvoiceInstallment


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'customer', 'payment_type', 'bank_details',
            'discount', 'shipping', 'paid_amount', 'cash_payment', 'cash_returned', 'date'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'input input-bordered'}),
            'discount': forms.NumberInput(attrs={'step': '0.01', 'class': 'input input-bordered'}),
            'shipping': forms.NumberInput(attrs={'step': '0.01', 'class': 'input input-bordered'}),
            'paid_amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'input input-bordered'}),
            'cash_payment': forms.NumberInput(attrs={'step': '0.01', 'class': 'input input-bordered'}),
            'cash_returned': forms.NumberInput(attrs={'step': '0.01', 'class': 'input input-bordered'}),
        }


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['item', 'quantity', 'price']
        widgets = {
            'item': forms.Select(attrs={'class': 'select select-bordered'}),
            'quantity': forms.NumberInput(attrs={'step': '0.01', 'class': 'input input-bordered'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'class': 'input input-bordered'}),
        }


InvoiceItemFormSet = forms.inlineformset_factory(
    Invoice, InvoiceItem, form=InvoiceItemForm,
    fields=['item', 'quantity', 'price'], extra=1, can_delete=True
)


class InvoiceInstallmentForm(forms.ModelForm):
    class Meta:
        model = InvoiceInstallment
        fields = ['paid_amount', 'description', 'date']
        widgets = {
            'paid_amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'input input-bordered'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'input input-bordered'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'textarea textarea-bordered'}),
        }













# from django import forms
# from .models import Invoice, InvoiceItem, Installment


# class InvoiceForm(forms.ModelForm):
#     class Meta:
#         model = Invoice
#         fields = ['customer_name', 'invoice_date', 'total_amount', 'paid_amount', 'status']
#         widgets = {
#             'customer_name': forms.TextInput(attrs={
#                 'class': 'input input-bordered w-full',
#                 'placeholder': 'Enter customer name'
#             }),
#             'invoice_date': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'input input-bordered w-full'
#             }),
#             'total_amount': forms.NumberInput(attrs={
#                 'class': 'input input-bordered w-full',
#                 'placeholder': 'Total amount'
#             }),
#             'paid_amount': forms.NumberInput(attrs={
#                 'class': 'input input-bordered w-full',
#                 'placeholder': 'Paid amount'
#             }),
#             'status': forms.Select(attrs={
#                 'class': 'select select-bordered w-full'
#             }),
#         }


# class InvoiceItemForm(forms.ModelForm):
#     class Meta:
#         model = InvoiceItem
#         fields = ['product', 'quantity', 'price', 'total']
#         widgets = {
#             'product': forms.Select(attrs={
#                 'class': 'select select-bordered w-full'
#             }),
#             'quantity': forms.NumberInput(attrs={
#                 'class': 'input input-bordered w-full',
#                 'placeholder': 'Quantity'
#             }),
#             'price': forms.NumberInput(attrs={
#                 'class': 'input input-bordered w-full',
#                 'placeholder': 'Unit price'
#             }),
#             'total': forms.NumberInput(attrs={
#                 'class': 'input input-bordered w-full',
#                 'readonly': 'readonly'
#             }),
#         }


# class InstallmentForm(forms.ModelForm):
#     class Meta:
#         model = Installment
#         fields = ['invoice', 'amount', 'date', 'status']
#         widgets = {
#             'invoice': forms.Select(attrs={
#                 'class': 'select select-bordered w-full'
#             }),
#             'amount': forms.NumberInput(attrs={
#                 'class': 'input input-bordered w-full',
#                 'placeholder': 'Installment amount'
#             }),
#             'date': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'input input-bordered w-full'
#             }),
#             'status': forms.Select(attrs={
#                 'class': 'select select-bordered w-full'
#             }),
#         }
