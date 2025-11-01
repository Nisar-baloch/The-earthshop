from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer
from .forms import CustomerForm
from django.shortcuts import render, get_object_or_404
from .models import Customer, Ledger
from django.db.models import Sum
from decimal import Decimal
from .forms import LedgerForm  
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import AddLedgerForm, PayLedgerForm
from django.http import JsonResponse, HttpResponseBadRequest
 


def customer_list(request):
    """
    Renders the customer list page. Shows all customers (you can paginate later).
    """
    customers = Customer.objects.order_by('-created_at')[:200]  # limit for performance
    form = CustomerForm()
    return render(request, 'customers/customer_list.html', {
        'customers': customers,
        'form': form
    })

@require_http_methods(["GET", "POST"])
def add_customer(request):
    """
    Handles add-customer requests.
    - Normal POST: behaves as before (redirect + messages).
    - AJAX POST: returns JSON (success or validation errors).
    """
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            # If AJAX request, return created object data as JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                data = {
                    'success': True,
                    'customer': {
                        'id': customer.id,
                        'name': customer.name,
                        'father_name': customer.father_name or '',
                        'city': customer.city or '',
                        'alternate_mobile': customer.alternate_mobile or '',
                        'resident': customer.resident or '',
                        'address': customer.address or '',
                        'created_at': customer.created_at.strftime('%Y-%m-%d %H:%M'),
                    }
                }
                return JsonResponse(data)
            # normal POST redirect
            messages.success(request, f'Customer "{customer.name}" was created successfully.')
            return redirect('customers:list')
        else:
            # Validation errors
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            messages.error(request, 'Please fix the errors below.')
    else:
        form = CustomerForm()

    # If GET or fallback render template (not expected for AJAX flow)
    return render(request, 'customers/add.html', {'form': form})

def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect("customers:list")
    else:
        form = CustomerForm(instance=customer)
    return render(request, "customers/customer_update.html", {"form": form, "customer": customer})


def customer_ledger(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    # Load ledgers for this customer (pagination optional)
    ledgers = Ledger.objects.filter(customer=customer).order_by('-date', '-id')

    # totals
    agg = ledgers.aggregate(total_debit=Sum('debit_amount'), total_credit=Sum('credit_amount'))
    total_debit = agg.get('total_debit') or 0
    total_credit = agg.get('total_credit') or 0

    return render(request, 'customers/ledger_list.html', {
        'customer': customer,
        'ledgers': ledgers,
        'total_debit': total_debit,
        'total_credit': total_credit,
    })

def customer_ledger(request, pk):
    """ Ledger listing for a single customer. """
    customer = get_object_or_404(Customer, pk=pk)
    ledgers = Ledger.objects.filter(customer=customer).order_by('-date', '-id')
    # compute totals
    total_debit = ledgers.aggregate_total('debit_amount') if hasattr(ledgers, 'aggregate_total') else sum((l.debit_amount or 0) for l in ledgers)
    total_credit = ledgers.aggregate_total('credit_amount') if hasattr(ledgers, 'aggregate_total') else sum((l.credit_amount or 0) for l in ledgers)
    return render(request, 'customers/ledger_list.html', {
        'customer': customer,
        'ledgers': ledgers,
        'total_debit': total_debit,
        'total_credit': total_credit,
    })




def ledger_list(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    ledgers = Ledger.objects.filter(customer=customer).order_by('-date', '-id')
    agg = ledgers.aggregate(total_debit=Sum('debit_amount'), total_credit=Sum('credit_amount'))
    total_debit = agg['total_debit'] or Decimal('0.00')
    total_credit = agg['total_credit'] or Decimal('0.00')
    add_form = AddLedgerForm()
    pay_form = PayLedgerForm()
    return render(request, 'customers/ledger_list.html', {
        'customer': customer,
        'ledgers': ledgers,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'add_form': add_form,
        'pay_form': pay_form,
    })

def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

def ledger_add_ajax(request, pk):
    if request.method != 'POST' or not _is_ajax(request):
        return HttpResponseBadRequest('Invalid request')
    customer = get_object_or_404(Customer, pk=pk)
    form = AddLedgerForm(request.POST)
    if form.is_valid():
        try:
            ledger = form.save(commit=False)
            ledger.customer = customer
            ledger.credit_amount = Decimal('0.00')
            ledger.save()
        except Exception as exc:
            # Return error message for client debug (safe in dev)
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)

        agg = Ledger.objects.filter(customer=customer).aggregate(total_debit=Sum('debit_amount'),
                                                                 total_credit=Sum('credit_amount'))
        total_debit = agg['total_debit'] or Decimal('0.00')
        total_credit = agg['total_credit'] or Decimal('0.00')

        entry = {
            'id': ledger.id,
            'date': ledger.date.strftime('%Y-%m-%d'),
            'detail': ledger.detail or '',
            'debit_amount': format(ledger.debit_amount, 'f'),
            'credit_amount': format(ledger.credit_amount, 'f'),
        }
        return JsonResponse({
            'success': True,
            'entry': entry,
            'total_debit': format(total_debit, 'f'),
            'total_credit': format(total_credit, 'f'),
        })
    else:
        # Return form errors as plain dict for easy display
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

def ledger_pay_ajax(request, pk):
    if request.method != 'POST' or not _is_ajax(request):
        return HttpResponseBadRequest('Invalid request')
    customer = get_object_or_404(Customer, pk=pk)
    form = PayLedgerForm(request.POST)
    if form.is_valid():
        try:
            ledger = form.save(commit=False)
            ledger.customer = customer
            ledger.debit_amount = Decimal('0.00')
            ledger.save()
        except Exception as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)

        agg = Ledger.objects.filter(customer=customer).aggregate(total_debit=Sum('debit_amount'),
                                                                 total_credit=Sum('credit_amount'))
        total_debit = agg['total_debit'] or Decimal('0.00')
        total_credit = agg['total_credit'] or Decimal('0.00')

        entry = {
            'id': ledger.id,
            'date': ledger.date.strftime('%Y-%m-%d'),
            'detail': ledger.detail or '',
            'debit_amount': format(ledger.debit_amount, 'f'),
            'credit_amount': format(ledger.credit_amount, 'f'),
        }
        return JsonResponse({
            'success': True,
            'entry': entry,
            'total_debit': format(total_debit, 'f'),
            'total_credit': format(total_credit, 'f'),
        })
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
