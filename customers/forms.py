from django import forms
from django.core.validators import RegexValidator
from .models import Customer, Ledger
from .models import Ledger

# Optional phone number validator
phone_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message='Enter a valid phone number (7–15 digits, optional +).'
)

class CustomerForm(forms.ModelForm):
    alternate_mobile = forms.CharField(
        required=False,
        validators=[phone_validator],
        widget=forms.TextInput(
            attrs={
                'class': 'input input-md input-bordered w-full',
                'placeholder': 'Alternate mobile number'
            }
        )
    )

    class Meta:
        model = Customer
        fields = [
            'name',
            'father_name',
            'city',
            'cnic',
            'alternate_mobile',
            'resident',
            'address',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input input-md input-bordered w-full',
                'placeholder': 'Customer name'
            }),
            'father_name': forms.TextInput(attrs={
                'class': 'input input-md input-bordered w-full',
                'placeholder': 'Father name'
            }),
            'city': forms.TextInput(attrs={
                'class': 'input input-md input-bordered w-full',
                'placeholder': 'City'
            }),
            'cnic': forms.TextInput(attrs={
                'class': 'input input-md input-bordered w-full',
                'placeholder': 'cnic'
            }),
            'resident': forms.TextInput(attrs={
                'class': 'input input-md input-bordered w-full',
                'placeholder': 'Resident (Owner/Tenant)'
            }),
            'address': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full h-28',
                'placeholder': 'Complete address'
            }),
        }


class LedgerForm(forms.ModelForm):
    class Meta:
        model = Ledger
        fields = ["date", "detail", "debit_amount", "credit_amount"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "input input-md"}),
            "detail": forms.TextInput(attrs={"class": "input input-md"}),
            "debit_amount": forms.NumberInput(attrs={"class": "input input-md"}),
            "credit_amount": forms.NumberInput(attrs={"class": "input input-md"}),
        }



class AddLedgerForm(forms.ModelForm):
    class Meta:
        model = Ledger
        fields = ['date', 'debit_amount', 'detail']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'input input-md input-bordered w-full'}),
            'debit_amount': forms.NumberInput(attrs={'class': 'input input-md input-bordered w-full', 'step': '0.01', 'min': '0'}),
            'detail': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full h-24', 'placeholder': 'Optional details'}),
        }

class PayLedgerForm(forms.ModelForm):
    class Meta:
        model = Ledger
        fields = ['date', 'credit_amount', 'detail']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'input input-md input-bordered w-full'}),
            'credit_amount': forms.NumberInput(attrs={'class': 'input input-md input-bordered w-full', 'step': '0.01', 'min': '0'}),
            'detail': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full h-24', 'placeholder': 'Optional details'}),
        }