# sales/views.py
import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib import messages
from django.utils import timezone

from .models import Invoice, InvoiceItem, InvoiceInstallment
from .forms import InvoiceForm, InvoiceItemForm, InvoiceInstallmentForm
from products.models import Product
from customers.models import Customer
from products.models import StockOut  # adjust path if your app is named differently
from banking.models import Bank  # adjust if app label differs


def create_invoice(request):
    """
    GET: render create invoice page (POS-like UI).
    POST: expect 'items' JSON (list of {item_id, qty, price, total}), plus invoice fields.
    """
    if request.method == 'POST':
        # parse posted data
        items_json = request.POST.get('items', '[]')
        try:
            items = json.loads(items_json)
        except Exception:
            items = []

        # Basic invoice fields
        customer_id = request.POST.get('customer_id') or None
        payment_type = request.POST.get('payment_type') or Invoice.PAYMENT_CASH
        bank_id = request.POST.get('bank') or None
        discount = Decimal(request.POST.get('discount') or '0')
        shipping = Decimal(request.POST.get('shipping') or '0')
        paid_amount = Decimal(request.POST.get('paid_amount') or '0')
        cash_payment = Decimal(request.POST.get('cash_payment') or '0')
        cash_returned = Decimal(request.POST.get('returned_cash') or '0')
        date = request.POST.get('date') or timezone.now().date()

        # compute sub_total and total_quantity from items
        sub_total = Decimal('0')
        total_qty = Decimal('0')
        for it in items:
            q = Decimal(str(it.get('qty') or '0'))
            p = Decimal(str(it.get('price') or '0'))
            sub_total += (q * p)
            total_qty += q

        grand_total = (sub_total - discount + shipping)

        # Start atomic transaction
        with transaction.atomic():
            customer = None
            if customer_id:
                try:
                    customer = Customer.objects.get(pk=int(customer_id))
                except Exception:
                    customer = None

            bank_obj = None
            if bank_id:
                try:
                    bank_obj = Bank.objects.get(pk=int(bank_id))
                except Exception:
                    bank_obj = None

            invoice = Invoice.objects.create(
                customer=customer,
                payment_type=payment_type,
                bank_details=bank_obj,
                total_quantity=total_qty,
                sub_total=sub_total,
                discount=discount,
                shipping=shipping,
                grand_total=grand_total,
                paid_amount=paid_amount,
                remaining_payment=(grand_total - paid_amount),
                cash_payment=cash_payment,
                cash_returned=cash_returned,
                date=date
            )

            # create invoice items and stockouts
            for it in items:
                item_id = it.get('item_id')
                qty = Decimal(str(it.get('qty') or '0'))
                price = Decimal(str(it.get('price') or '0'))
                total = qty * price
                if not item_id:
                    continue
                product = Product.objects.get(pk=int(item_id))
                InvoiceItem.objects.create(
                    invoice=invoice,
                    item=product,
                    quantity=qty,
                    price=price,
                    total=total
                )
                # Create a StockOut entry and decrement product.stock
                try:
                    StockOut.objects.create(
                        product=product,
                        stock_out_quantity=int(qty),
                        invoice=invoice,
                        date=date
                    )
                    # decrement product.stock if field exists
                    if hasattr(product, 'stock'):
                        product.stock = max(0, int(product.stock or 0) - int(qty))
                        product.save(update_fields=['stock'])
                except Exception:
                    # if StockOut model or product.stock not present, ignore but log via messages
                    pass

            # If Installment and some paid amount, create installment record
            if payment_type == Invoice.PAYMENT_INSTALLMENT and paid_amount > 0:
                InvoiceInstallment.objects.create(
                    invoice=invoice,
                    paid_amount=paid_amount,
                    description='Advance Payment',
                    date=date
                )

        messages.success(request, f"Invoice {str(invoice)} created successfully.")
        return redirect('sales:invoice_detail', pk=invoice.pk)

    # GET - render form
    products = Product.objects.all().order_by('name')
    customers = Customer.objects.all().order_by('name')
    banks = Bank.objects.all().order_by('name')
    invoice_form = InvoiceForm(initial={'date': timezone.now().date()})

    return render(request, 'sales/create_invoice.html', {
        'products': products,
        'customers': customers,
        'banks': banks,
        'invoice_form': invoice_form,
        'today_date': timezone.now().date()
    })


def invoice_list(request):
    qs = Invoice.objects.select_related('customer').all().order_by('-date', '-id')
    # Filters
    q_name = request.GET.get('q_name')
    q_invoice = request.GET.get('q_invoice')
    q_date = request.GET.get('q_date')

    if q_name:
        qs = qs.filter(customer__name__icontains=q_name)
    if q_invoice:
        qs = qs.filter(id=int(q_invoice.lstrip('0') or 0))
    if q_date:
        qs = qs.filter(date=q_date)

    paginator = Paginator(qs, 20)
    page = request.GET.get('page')
    invoices = paginator.get_page(page)

    return render(request, 'sales/invoice_list.html', {
        'invoices': invoices
    })


def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = invoice.invoice_items.select_related('item').all()
    return render(request, 'sales/invoice_detail.html', {
        'invoice': invoice,
        'items': items
    })


# Installments
def installment_list(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    installments = invoice.invoice_installment.all().order_by('-date', '-id')
    return render(request, 'sales/installment_list.html', {
        'invoice': invoice,
        'installments': installments
    })


def installment_add(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    if request.method == 'POST':
        form = InvoiceInstallmentForm(request.POST)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.invoice = invoice
            inst.save()
            messages.success(request, "Installment added.")
            return redirect('sales:installment_list', invoice_id=invoice.id)
    else:
        form = InvoiceInstallmentForm(initial={'date': timezone.now().date()})
    return render(request, 'sales/installment_add.html', {
        'invoice': invoice,
        'form': form
    })








# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.db import transaction
# from django.http import JsonResponse, HttpResponseBadRequest

# import json # Needed for parsing dynamic item data

# from .forms import InvoiceForm # InvoiceItemForm not strictly needed here for processing
# from .models import Invoice, InvoiceItem, INVOICE_STATUS_CHOICES
# from products.models import Product, StockOut # Assuming StockOut is imported here
# # Assuming these models exist:
# from customers.models import Customer
# from banking.models import BankAccount

# # Helper function to calculate final totals based on items, discount, and shipping
# def calculate_invoice_totals(items_list, discount_amount, shipping_charge):
#     """Calculates subtotal and grand total based on line items."""
#     line_subtotal = sum(item['quantity'] * item['unit_price'] for item in items_list)
    
#     # Ensure discount and shipping are decimal fields
#     discount_amount = discount_amount if discount_amount is not None else 0.00
#     shipping_charge = shipping_charge if shipping_charge is not None else 0.00
    
#     grand_total = line_subtotal - discount_amount + shipping_charge
    
#     return line_subtotal, grand_total


# @login_required
# def sales_dashboard(request):
#     """Placeholder for the Sales Dashboard view."""
#     # ... (Keep existing dashboard, list, detail, print, installment placeholders) ...
#     # This is placeholder, will be implemented in a later step (Goal #4)
#     return render(request, 'sales/dashboard.html', {'title': 'Sales Dashboard'})

# @login_required
# def invoice_list(request):
#     """Placeholder for the Invoice List view."""
#     # ... (Keep existing placeholder) ...
#     return render(request, 'sales/invoice_list.html', {'title': 'Invoices List'})

# @login_required
# def invoice_detail(request, invoice_id):
#     """Placeholder for the Invoice Detail view."""
#     # ... (Keep existing placeholder) ...
#     invoice = get_object_or_404(Invoice, pk=invoice_id)
#     return render(request, 'sales/invoice_detail.html', {'title': f'Invoice #{invoice.id}', 'invoice': invoice})

# @login_required
# def invoice_print(request, invoice_id):
#     """Placeholder for the Printable Invoice view."""
#     # ... (Keep existing placeholder) ...
#     invoice = get_object_or_404(Invoice, pk=invoice_id)
#     return render(request, 'sales/invoice_print.html', {'title': f'Print Invoice #{invoice.id}', 'invoice': invoice})

# @login_required
# def invoice_installments(request, invoice_id):
#     """Placeholder for Installments List for an Invoice."""
#     # ... (Keep existing placeholder) ...
#     invoice = get_object_or_404(Invoice, pk=invoice_id)
#     return render(request, 'sales/invoice_installments.html', {'title': f'Installments for Invoice #{invoice.id}', 'invoice': invoice})

# @login_required
# def add_installment(request, invoice_id):
#     """Placeholder for adding a new Installment."""
#     # ... (Keep existing placeholder) ...
#     invoice = get_object_or_404(Invoice, pk=invoice_id)
#     return render(request, 'sales/add_installment.html', {'title': f'Add Installment to Invoice #{invoice.id}', 'invoice': invoice})


# @login_required
# @transaction.atomic
# def create_invoice(request):
#     """
#     Handles the POS-style form submission for creating a new Invoice, 
#     InvoiceItems, and corresponding StockOut records.
#     """
#     if request.method == 'POST':
#         # 1. Initialize Forms and Data
#         form = InvoiceForm(request.POST)
        
#         # Get line item data (expected to be a JSON string from frontend JS)
#         try:
#             items_data = json.loads(request.POST.get('items_data', '[]'))
#         except json.JSONDecodeError:
#             messages.error(request, "Error processing item data. Please ensure items are correctly formatted.")
#             return redirect('sales:create_invoice')

#         # Get financial values from the hidden/calculated fields passed by the frontend
#         try:
#             grand_total = float(request.POST.get('grand_total', 0.00))
#             amount_paid = float(request.POST.get('amount_paid', 0.00))
#             discount_amount = float(request.POST.get('discount_amount', 0.00))
#             shipping_charge = float(request.POST.get('shipping_charge', 0.00))
            
#             # Remaining balance should be calculated: Grand Total - Amount Paid
#             remaining_balance = grand_total - amount_paid
#         except ValueError:
#              messages.error(request, "Invalid financial values submitted.")
#              return redirect('sales:create_invoice')


#         # 2. Validate Items and Check Stock
        
#         # Check if there are any items
#         if not items_data:
#             messages.error(request, "Invoice must contain at least one item.")
#             return redirect('sales:create_invoice')

#         # Check stock and aggregate items
#         processed_items = []
#         products_to_update = {} # {product_id: Product object}
        
#         for item in items_data:
#             product_id = item.get('product_id')
#             quantity = int(item.get('quantity', 0))
#             unit_price = float(item.get('unit_price', 0.00))
            
#             if quantity <= 0:
#                 continue

#             try:
#                 # Use select_for_update for thread safety during stock check/update
#                 product = Product.objects.select_for_update().get(pk=product_id)
#             except Product.DoesNotExist:
#                 messages.error(request, f"Product ID {product_id} not found.")
#                 return redirect('sales:create_invoice')
            
#             # CRITICAL SAFETY CHECK: Use product.stock field
#             if product.stock < quantity:
#                 messages.error(request, f"Insufficient stock for {product.name}. Available: {product.stock}, Requested: {quantity}.")
#                 # The transaction will automatically roll back
#                 return redirect('sales:create_invoice')
            
#             processed_items.append({
#                 'product': product,
#                 'quantity': quantity,
#                 'unit_price': unit_price,
#                 'subtotal': quantity * unit_price
#             })
#             products_to_update[product.id] = product # Collect product object


#         # 3. Final Form Validation and Save
#         if form.is_valid():
#             invoice = form.save(commit=False)
            
#             # Recalculate totals one last time on the backend for security and accuracy
#             calculated_subtotal, calculated_grand_total = calculate_invoice_totals(
#                 [{'quantity': item['quantity'], 'unit_price': item['unit_price']} for item in processed_items],
#                 invoice.discount_amount,
#                 invoice.shipping_charge
#             )
            
#             # Assign final calculated values
#             invoice.subtotal = calculated_subtotal
#             invoice.grand_total = calculated_grand_total
#             invoice.amount_paid = amount_paid # User-submitted payment
#             invoice.remaining_balance = calculated_grand_total - amount_paid
#             invoice.created_by = request.user
            
#             # Determine status
#             if invoice.remaining_balance <= 0.00:
#                 invoice.status = 'Paid'
#             elif invoice.payment_type == 'Installment' and invoice.remaining_balance > 0.00:
#                 invoice.status = 'Confirmed'
#             else:
#                 invoice.status = 'Confirmed'

#             invoice.save()
            
#             # 4. Create Invoice Items and StockOut records
#             for item in processed_items:
#                 # Create InvoiceItem
#                 InvoiceItem.objects.create(
#                     invoice=invoice,
#                     product=item['product'],
#                     quantity=item['quantity'],
#                     unit_price=item['unit_price'],
#                     # subtotal calculated in model's save()
#                 )
                
#                 # Create StockOut Record (Linking StockOut to the Invoice for traceability)
#                 # --- CORRECTED FIELD NAMES TO MATCH YOUR MODEL ---
#                 StockOut.objects.create(
#                     product=item['product'],
#                     stock_out_quantity=item['quantity'], # Using your field name
#                     invoice=invoice, # Using your field name
#                 )

#                 # Update Product Stock (Atomic update)
#                 item['product'].stock -= item['quantity']
#                 item['product'].save(update_fields=['stock'])

#             # 5. Handle Initial Payment Integration (Cash/Check) - Follow-up step
            
#             messages.success(request, f"Invoice #{invoice.id} created successfully! Total: {invoice.grand_total}")
#             return redirect('sales:invoice_detail', invoice_id=invoice.id)
        
#         else:
#             # Form is invalid
#             messages.error(request, "Invoice submission failed. Please check the form errors.")
#             # Fall through to render the form with errors

#     else:
#         # GET request
#         form = InvoiceForm(initial={
#             'discount_amount': 0,
#             'shipping_charge': 0,
#             'amount_paid': 0,
#             'payment_type': 'Cash'
#         })
        
#     # Re-fetch item form for rendering the POS input row
#     item_form = InvoiceItemForm()
    
#     context = {
#         'title': 'Create New Invoice (POS)',
#         'invoice_form': form,
#         'item_form': item_form,
#         'customers': Customer.objects.all(), # Pass customers for dropdown
#         'products': Product.objects.all(), # Pass products for JS data
#         'banks': BankAccount.objects.all(), # Pass banks for dropdown
#     }
#     return render(request, 'sales/create_invoice.html', context)
