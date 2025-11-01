# banking/forms.py
from django import forms
from django.apps import apps
from .models import BankForm 

# Lazy get Bank model to avoid import-time circular dependency
def get_Bank_model():
    return apps.get_model('banking', 'Bank')

class BankForm(forms.ModelForm):
    class Meta:
        model = get_Bank_model()
        fields = '__all__'


# Factory for BankDetail form to avoid import-time errors
# def BankDetailFormFactory():
#     BankDetail = apps.get_model('banking', 'BankDetail')  # resolves at runtime
#     class BankDetailForm(forms.ModelForm):
#         class Meta:
#             model = BankDetail
#             fields = '__all__'
#     return BankDetailForm
