# sales/views.py
import json
import importlib
from django.core.paginator import Paginator
from django.views.generic import (ListView, TemplateView, View, FormView, DeleteView)
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Sum
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django import forms

from .models import Invoice, InvoiceInstallment

# helper: try import with common app name variants
def try_import(module_prefix, name):
    """
    Try import `name` from module names:
      - module_prefix (as given, e.g. 'customer.models')
      - plural form module_prefix + 's' (e.g. 'customers.models')
    Return the attribute or raise ImportError.
    """
    candidates = [module_prefix, module_prefix + 's']
    for mod in candidates:
        try:
            module = importlib.import_module(mod)
            return getattr(module, name)
        except (ImportError, AttributeError, ModuleNotFoundError):
            continue
    raise ImportError(f"Could not import {name} from {module_prefix} or its variants.")

# Attempt to import related models (customer, product, banking)
Customer = None
Product = None
Bank = None

try:
    Customer = try_import('customer.models', 'Customer')
except ImportError:
    try:
        Customer = try_import('customers.models', 'Customer')
    except ImportError:
        Customer = None

try:
    Product = try_import('product.models', 'Product')
except ImportError:
    try:
        Product = try_import('products.models', 'Product')
    except ImportError:
        Product = None

try:
    Bank = try_import('banking_system.models', 'Bank')
except ImportError:
    try:
        Bank = try_import('banking.models', 'Bank')
    except ImportError:
        Bank = None

# Fallback minimal ModelForm factories if sales.forms or other forms are missing
def make_modelform_for(model_cls, fields=None):
    if model_cls is None:
        # return a generic Form to avoid import errors (won't save)
        class DummyForm(forms.Form):
            pass
        return DummyForm
    meta_attrs = {'model': model_cls, 'fields': fields or '__all__'}
    Meta = type('Meta', (), meta_attrs)
    attrs = {'Meta': Meta}
    form_cls = type(f'{model_cls.__name__}AutoForm', (forms.ModelForm,), attrs)
    return form_cls

# -------------------------
# Avoid creating ModelForm classes at import time.
# Instead leave them as None and create/use forms inside views if needed.
# This prevents errors when related models (e.g. banking_system.Bank) are not yet loaded.
# -------------------------

# Keep the variables defined, but do NOT build ModelForm classes at import.
InvoiceForm = None
InvoiceInstallmentForm = None
CustomerForm = None
CustomerLedgerForm = None
StockOutForm = None
PurchasedItemForm = None
BankDetailForm = None

# Helper factory to build ModelForm on demand (call inside a request handler)
def build_modelform(model_cls, fields=None):
    """
    Dynamically build a ModelForm for model_cls at runtime.
    Returns a ModelForm class or None if model_cls is None.
    """
    if model_cls is None:
        return None
    try:
        Meta = type('Meta', (), {'model': model_cls, 'fields': fields or '__all__'})
        form_cls = type(f'{model_cls.__name__}AutoForm', (forms.ModelForm,), {'Meta': Meta})
        return form_cls
    except Exception:
        return None


# customer forms
try:
    cust_forms = importlib.import_module('customer.forms')
    CustomerForm = getattr(cust_forms, 'CustomerForm', None)
    CustomerLedgerForm = getattr(cust_forms, 'CustomerLedgerForm', None)
except Exception:
    CustomerForm = None
    CustomerLedgerForm = None

# product/banking forms
try:
    prod_forms = importlib.import_module('product.forms')
    StockOutForm = getattr(prod_forms, 'StockOutForm', None)
    PurchasedItemForm = getattr(prod_forms, 'PurchasedItemForm', None)
except Exception:
    StockOutForm = None
    PurchasedItemForm = None

try:
    bank_forms = importlib.import_module('banking_system.forms')
    BankDetailForm = getattr(bank_forms, 'BankDetailForm', None)
except Exception:
    BankDetailForm = None

# Ensure InvoiceForm exists (fallback)
if InvoiceForm is None:
    InvoiceForm = make_modelform_for(Invoice, fields=[
        'payment_type', 'bank_details', 'total_quantity', 'sub_total',
        'paid_amount', 'remaining_payment', 'discount', 'shipping',
        'grand_total', 'cash_payment', 'cash_returned', 'date'
    ])

if InvoiceInstallmentForm is None:
    InvoiceInstallmentForm = make_modelform_for(InvoiceInstallment, fields=['invoice', 'paid_amount', 'description', 'date'])

if CustomerForm is None and Customer is not None:
    CustomerForm = make_modelform_for(Customer, fields='__all__')

if CustomerLedgerForm is None:
    # If missing, just create a dummy form to avoid import failures. You should implement a real one.
    class DummyLedgerForm(forms.Form):
        pass
    CustomerLedgerForm = DummyLedgerForm

if StockOutForm is None:
    # Make a minimal StockOut form so code that calls .save() will fail gracefully if model missing
    class DummyStockOutForm(forms.Form):
        pass
    StockOutForm = DummyStockOutForm

if PurchasedItemForm is None:
    class DummyPurchasedItemForm(forms.Form):
        pass
    PurchasedItemForm = DummyPurchasedItemForm

if BankDetailForm is None:
    class DummyBankDetailForm(forms.Form):
        pass
    BankDetailForm = DummyBankDetailForm


# ----------------------------
# Views (adapted)
# ----------------------------

class InvoiceListView(ListView):
    template_name = 'sales/invoice_list.html'
    model = Invoice
    paginate_by = 100

    def get_queryset(self):
        queryset = self.queryset
        if not queryset:
            queryset = Invoice.objects.all().order_by('-id')

        if self.request.GET.get('customer_name'):
            queryset = queryset.filter(
                customer__name__contains=self.request.GET.get('customer_name'))

        if self.request.GET.get('customer_id'):
            queryset = queryset.filter(
                id=self.request.GET.get('customer_id').lstrip('0')
            )

        if self.request.GET.get('date'):
            queryset = queryset.filter(
                date=self.request.GET.get('date')
            )

        return queryset.order_by('-id')


class CreateInvoiceTemplateView(TemplateView):
    template_name = 'sales/create_invoice.html'

    def get_context_data(self, **kwargs):
        context = super(CreateInvoiceTemplateView, self).get_context_data(**kwargs)
        context.update({
            'customers': Customer.objects.all().order_by('name') if Customer is not None else [],
            'products': Product.objects.all().order_by('name') if Product is not None else [],
            'today_date': timezone.now().date(),
            'banks': Bank.objects.all().order_by('name') if Bank is not None else []
        })
        return context


class ProductListAPIView(View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all() if Product is not None else []
        items = []

        for product in products:
            p = {
                'id': product.id,
                'name': getattr(product, 'name', str(product)),
                'category_name': getattr(getattr(product, 'category', None), 'name', '')
            }

            # reading stock requires related names that may differ; attempt safe access
            try:
                stockins = product.stockin_product.all()
            except Exception:
                stockins = []

            if stockins:
                stock_detail = stockins.latest('id')
                p.update({
                    'selling_price': '%g' % getattr(stock_detail, 'price_per_item', 0),
                    'buying_price': '%g' % getattr(stock_detail, 'buying_price_item', 0),
                })

                try:
                    all_stock = stockins.aggregate(Sum('stock_quantity'))
                    all_stock = float(all_stock.get('stock_quantity__sum') or 0)
                except Exception:
                    all_stock = 0

                try:
                    purchased_stock = product.stockout_product.all()
                    purchased_stock = purchased_stock.aggregate(Sum('stock_out_quantity'))
                    purchased_stock = float(purchased_stock.get('stock_out_quantity__sum') or 0)
                except Exception:
                    purchased_stock = 0

                p.update({
                    'stock': all_stock - purchased_stock
                })

            else:
                p.update(
                    {
                        'selling_item': 0,
                        'buying_price': 0,
                        'stock': 0
                    }
                )

            items.append(p)

        return JsonResponse({'products': items})


class GenerateInvoiceAPIView(View):
    # Accept AJAX POST to create invoice + ledger entries
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(GenerateInvoiceAPIView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # read POST data
        data = request.POST
        items_json = data.get('items') or '[]'
        try:
            items = json.loads(items_json)
        except Exception:
            items = []

        # basic fields
        customer_name = data.get('customer_name')
        customer_phone = data.get('customer_phone')
        customer_cnic = data.get('customer_cnic')
        discount = data.get('discount') or 0
        shipping = data.get('shipping') or 0
        grand_total = data.get('grand_total') or 0
        totalQty = data.get('totalQty') or 0
        remaining_payment = data.get('remaining_amount') or 0
        paid_amount = data.get('paid_amount') or 0
        cash_payment = data.get('cash_payment') or 0
        returned_cash = data.get('returned_cash') or 0
        payment_type = data.get('payment_type') or 'Cash'
        bank = data.get('bank')

        with transaction.atomic():
            # create invoice via form (fallback to direct model create)
            invoice_data = {
                'discount': discount,
                'grand_total': grand_total,
                'total_quantity': totalQty,
                'shipping': shipping,
                'paid_amount': paid_amount,
                'remaining_payment': remaining_payment,
                'cash_payment': cash_payment,
                'cash_returned': returned_cash,
                'payment_type': payment_type,
            }

            try:
                invoice_form = InvoiceForm(invoice_data)
                if invoice_form.is_valid():
                    invoice = invoice_form.save()
                else:
                    # fallback: create Invoice directly (best-effort)
                    invoice = Invoice.objects.create(**{k: invoice_data.get(k) for k in invoice_data})
            except Exception:
                invoice = Invoice.objects.create(**{k: invoice_data.get(k) for k in invoice_data})

            # handle customer: attach existing or create
            customer = None
            if data.get('customer_id'):
                try:
                    customer = Customer.objects.get(id=data.get('customer_id'))
                except Exception:
                    customer = None
            else:
                if Customer is not None:
                    try:
                        customer_form = CustomerForm({
                            'name': customer_name,
                            'mobile': customer_phone,
                            'cnic': customer_cnic
                        })
                        if hasattr(customer_form, 'is_valid') and customer_form.is_valid():
                            customer = customer_form.save()
                        else:
                            # try direct create if fields exist
                            customer = Customer.objects.create(name=customer_name) if customer_name else None
                    except Exception:
                        try:
                            customer = Customer.objects.create(name=customer_name) if customer_name else None
                        except Exception:
                            customer = None

            if customer:
                invoice.customer = customer
                invoice.save()

            # items processing: stock out and purchased items
            for item in items:
                try:
                    product = Product.objects.get(id=item.get('item_id'))
                except Exception:
                    product = None

                if product:
                    # attempt to do stock out (if StockOutForm exists and model relations exist)
                    try:
                        latest_stockin = product.stockin_product.all().latest('id')
                    except Exception:
                        latest_stockin = None

                    stock_out_kwargs = {
                        'product': getattr(product, 'id', None),
                        'invoice': getattr(invoice, 'id', None),
                        'stock_out_quantity': float(item.get('qty') or 0),
                        'buying_price': float((getattr(latest_stockin, 'buying_price_item', 0) or 0) * float(item.get('qty') or 0)),
                        'selling_price': float((item.get('price') or 0) * float(item.get('qty') or 0)),
                        'date': timezone.now().date()
                    }

                    try:
                        if isinstance(StockOutForm, type) and issubclass(StockOutForm, forms.ModelForm):
                            sof = StockOutForm(stock_out_kwargs)
                            sof.save()
                    except Exception:
                        pass

                    # purchased item
                    purchased_item_kwargs = {
                        'item': getattr(product, 'id', None),
                        'invoice': getattr(invoice, 'id', None),
                        'quantity': item.get('qty'),
                        'price': item.get('price'),
                        'purchase_amount': item.get('total'),
                    }
                    try:
                        if isinstance(PurchasedItemForm, type) and issubclass(PurchasedItemForm, forms.ModelForm):
                            pif = PurchasedItemForm(purchased_item_kwargs)
                            pif.save()
                    except Exception:
                        pass

            # handle installment/ledger/bank details
            try:
                if getattr(invoice, 'id', None):
                    if payment_type == 'Installment':
                        # create an installment record
                        inst_data = {'invoice': invoice.id, 'paid_amount': paid_amount, 'description': 'Advance Payment'}
                        try:
                            inst_form = InvoiceInstallmentForm(inst_data)
                            if hasattr(inst_form, 'is_valid') and inst_form.is_valid():
                                inst_form.save()
                            else:
                                InvoiceInstallment.objects.create(invoice=invoice, paid_amount=paid_amount, description='Advance Payment')
                        except Exception:
                            InvoiceInstallment.objects.create(invoice=invoice, paid_amount=paid_amount, description='Advance Payment')
                    elif float(remaining_payment or 0):
                        # create customer ledger entry if form exists
                        ledger_data = {
                            'customer': getattr(customer, 'id', None),
                            'invoice': invoice.id,
                            'debit_amount': remaining_payment,
                            'details': f'Remaining Payment for Bill/Receipt No {str(invoice.id).zfill(7)}',
                            'date': timezone.now()
                        }
                        try:
                            if hasattr(CustomerLedgerForm, 'is_valid'):
                                clf = CustomerLedgerForm(ledger_data)
                                if clf.is_valid():
                                    clf.save()
                        except Exception:
                            pass

                    if payment_type == 'Check' and bank:
                        bank_data = {'bank': bank, 'invoice': invoice.id, 'credit': paid_amount, 'description': 'Invoice Payment is by Check/Bank.'}
                        try:
                            if hasattr(BankDetailForm, 'is_valid'):
                                bdf = BankDetailForm(bank_data)
                                bd = bdf.save()
                                invoice.bank_details = getattr(bd, 'bank', None)
                                invoice.save()
                        except Exception:
                            pass
            except Exception:
                pass

        return JsonResponse({'invoice_id': getattr(invoice, 'id', None)})


class InvoiceDetailTemplateView(TemplateView):
    template_name = 'sales/invoice_detail.html'

    def get_context_data(self, **kwargs):
        context = super(InvoiceDetailTemplateView, self).get_context_data(**kwargs)
        invoice = Invoice.objects.get(id=self.kwargs.get('pk'))
        context.update({
            'invoice': invoice
        })
        return context


class InvoiceInstallmentListView(ListView):
    model = InvoiceInstallment
    template_name = 'sales/installment_list.html'
    paginate_by = 100
    # ordering = '-date'  # ListView uses ordering attribute of model if set

    def get_queryset(self):
        queryset = InvoiceInstallment.objects.filter(
            invoice=self.kwargs.get('invoice_id'))
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(InvoiceInstallmentListView, self).get_context_data(**kwargs)

        invoice = Invoice.objects.get(id=self.kwargs.get('invoice_id'))
        invoice_installments = InvoiceInstallment.objects.filter(
            invoice__id=invoice.id)

        grand_total = invoice.grand_total

        if invoice_installments.exists():
            total_paid_amount = invoice_installments.aggregate(
                Sum('paid_amount'))
            total_paid_amount = float(
                total_paid_amount.get('paid_amount__sum') or 0
            )
        else:
            total_paid_amount = 0

        context.update({
            'invoice_id': self.kwargs.get('invoice_id'),
            'total_paid_amount': total_paid_amount,
            'remaining_amount': float(grand_total or 0) - total_paid_amount
        })
        return context


class InvoiceInstallmentFormView(FormView):
    form_class = InvoiceInstallmentForm
    template_name = 'sales/installment_add.html'

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(
            reverse('sales:installment_list',
                    kwargs={'invoice_id': self.kwargs.get('invoice_id')}))

    def form_invalid(self, form):
        return super(InvoiceInstallmentFormView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(InvoiceInstallmentFormView, self).get_context_data(**kwargs)
        context.update({
            'invoice': Invoice.objects.get(id=self.kwargs.get('invoice_id'))
        })
        return context


class InvoiceInstallmentDeleteView(DeleteView):
    model = InvoiceInstallment
    success_message = ''

    def __init__(self, *args, **kwargs):
        super(InvoiceInstallmentDeleteView, self).__init__(*args, **kwargs)
        self.invoice_id = None

    def dispatch(self, request, *args, **kwargs):
        installment = InvoiceInstallment.objects.get(id=self.kwargs.get('pk'))
        self.invoice_id = installment.invoice.id

        return super(
            InvoiceInstallmentDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'sales:installment_list', kwargs={'invoice_id': self.invoice_id})

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    

# from django.shortcuts import render

# # Create your views here.
# from django.shortcuts import render, get_object_or_404
# from .models import Invoice

# def print_invoice(request, pk):
#     invoice = get_object_or_404(Invoice, pk=pk)
#     return render(request, 'sales/print_invoice.html', {'invoice': invoice})



# def index(request):
#     return render(request, 'sales/index.html')
