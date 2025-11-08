# sales/models.py
from decimal import Decimal
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.conf import settings


class Invoice(models.Model):
    PAYMENT_CASH = 'Cash'
    PAYMENT_INSTALLMENT = 'Installment'
    PAYMENT_CHECK = 'Check'

    PAYMENT_TYPES = (
        (PAYMENT_CASH, 'Cash'),
        (PAYMENT_INSTALLMENT, 'Installment'),
        (PAYMENT_CHECK, 'Check'),
    )

    # lazy FK references to avoid circular imports
    customer = models.ForeignKey(
        'customers.Customer', related_name='invoices',
        blank=True, null=True, on_delete=models.SET_NULL
    )

    payment_type = models.CharField(max_length=32, choices=PAYMENT_TYPES, default=PAYMENT_CASH)

    bank_details = models.ForeignKey(
        'banking.Bank', related_name='invoice_payments',
        blank=True, null=True, on_delete=models.SET_NULL
    )

    total_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sub_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    remaining_payment = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    cash_payment = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    cash_returned = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return str(self.id).zfill(7)

    def recalc_totals(self):
        """
        Recalculate totals from related InvoiceItem/PurchasedItem records.
        Call this after creating/updating items.
        """
        items = self.invoice_items.all()
        sub_total = Decimal('0.00')
        total_qty = Decimal('0.00')
        for it in items:
            sub_total += (it.price or Decimal('0.00')) * (it.quantity or Decimal('0.00'))
            total_qty += it.quantity or Decimal('0.00')

        self.sub_total = sub_total
        self.total_quantity = total_qty
        self.grand_total = (sub_total - (self.discount or Decimal('0.00')) + (self.shipping or Decimal('0.00')))
        # remaining_payment may be updated by view based on paid_amount
        self.remaining_payment = (self.grand_total - (self.paid_amount or Decimal('0.00')))
        self.save(update_fields=['sub_total', 'total_quantity', 'grand_total', 'remaining_payment'])

    def total_paid_installments(self):
        agg = self.invoice_installment.aggregate(total=Sum('paid_amount'))
        return Decimal(agg.get('total') or 0)

    def is_fully_paid(self):
        return (self.total_paid_installments() + (self.paid_amount or Decimal('0'))) >= (self.grand_total or Decimal('0'))

    def remaining_installment_amount(self):
        return (self.grand_total or Decimal('0')) - (self.total_paid_installments() + (self.paid_amount or Decimal('0')))


class InvoiceItem(models.Model):
    """
    line item in an invoice (product sold)
    """
    invoice = models.ForeignKey(Invoice, related_name='invoice_items', on_delete=models.CASCADE)
    item = models.ForeignKey('products.Product', related_name='invoice_items', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)  # quantity * price
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        name = getattr(self.item, 'name', str(self.item))
        return f"{name} x {self.quantity}"

    def save(self, *args, **kwargs):
        # maintain total
        q = self.quantity or Decimal('0.00')
        p = self.price or Decimal('0.00')
        self.total = (q * p)
        super().save(*args, **kwargs)


class InvoiceInstallment(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='invoice_installment', on_delete=models.CASCADE)
    paid_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Installment for {self.invoice} - {self.paid_amount}"


# from django.db import models
# from django.db.models import Sum
# from django.utils import timezone


# class Invoice(models.Model):

#     PAYMENT_CASH = 'Cash'
#     PAYMENT_INSTALLMENT = 'Installment'
#     PAYMENT_CHECK = 'Check'

#     PAYMENT_TYPES = (
#         (PAYMENT_CASH, 'Cash'),
#         (PAYMENT_INSTALLMENT, 'Installment'),
#         (PAYMENT_CHECK, 'Check'),
#     )

#     customer = models.ForeignKey(
#         'customers.Customer',
#         related_name='customer_sales',
#         blank=True, null=True, on_delete=models.SET_NULL
#     )

#     payment_type = models.CharField(
#         choices=PAYMENT_TYPES, default=PAYMENT_CASH, max_length=100)

#     bank_details = models.ForeignKey(
#         'banking.Bank', related_name='bank_detail_payments',
#         blank=True, null=True, on_delete=models.SET_NULL
#     )

#     total_quantity = models.CharField(
#         max_length=10, blank=True, null=True, default=1
#     )

#     sub_total = models.DecimalField(
#         max_digits=65, decimal_places=2, default=0, blank=True, null=True
#     )

#     paid_amount = models.DecimalField(
#         max_digits=65, decimal_places=2, default=0, blank=True, null=True
#     )

#     remaining_payment = models.DecimalField(
#         max_digits=65, decimal_places=2, default=0, blank=True, null=True
#     )

#     discount = models.DecimalField(
#         max_digits=65, decimal_places=2, default=0, blank=True, null=True
#     )

#     shipping = models.DecimalField(
#         max_digits=65, decimal_places=2, default=0, blank=True, null=True
#     )

#     grand_total = models.DecimalField(
#         max_digits=65, decimal_places=2, default=0, blank=True, null=True
#     )

#     cash_payment = models.DecimalField(
#         max_digits=65, decimal_places=2, default=0, blank=True, null=True
#     )

#     cash_returned = models.DecimalField(
#         max_digits=65, decimal_places=2, default=0, blank=True, null=True
#     )
#     date = models.DateField(default=timezone.now, blank=True, null=True)

#     def __str__(self):
#         return str(self.id).zfill(7)

#     def is_installment(self):
#         invoice_installments = InvoiceInstallment.objects.filter(
#             invoice__id=self.id)

#         grand_total = self.grand_total

#         if invoice_installments.exists():
#             total_paid_amount = invoice_installments.aggregate(
#                 Sum('paid_amount'))
#             total_paid_amount = float(
#                 total_paid_amount.get('paid_amount__sum') or 0
#             )

#         else:
#             total_paid_amount = 0

#         if float(grand_total) <= total_paid_amount:
#             return True

#         return False

#     def remaining_installment(self):
#         invoice_installments = InvoiceInstallment.objects.filter(
#             invoice__id=self.id)

#         grand_total = self.grand_total

#         if invoice_installments.exists():
#             total_paid_amount = invoice_installments.aggregate(
#                 Sum('paid_amount'))
#             total_paid_amount = float(
#                 total_paid_amount.get('paid_amount__sum') or 0
#             )

#         else:
#             total_paid_amount = 0

#         return float(grand_total) - total_paid_amount

#     def has_installment(self):
#         if self.invoice_installment.all().exists():
#             return True

#         return False




# class InvoiceInstallment(models.Model):
#     invoice = models.ForeignKey(
#         Invoice, related_name='invoice_installment', on_delete=models.CASCADE)
#     paid_amount = models.DecimalField(
#         max_digits=65, decimal_places=2, default=0, blank=True, null=True
#     )
#     description = models.TextField(blank=True, null=True)
#     date = models.DateField(
#         default=timezone.now, blank=True, null=True)

#     def __str__(self):
#         return (
#             '%s Installment' % self.invoice.customer.name if
#             self.invoice.customer else ''
#         )



# # class Invoice(models.Model):
# #     customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)
# #     date = models.DateTimeField(default=timezone.now)
# #     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
# #     payment_method = models.CharField(max_length=20, choices=[('cash', 'Cash'), ('credit', 'Credit')])

# # class InvoiceItem(models.Model):
# #     invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
# #     product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
# #     quantity = models.IntegerField()
# #     price = models.DecimalField(max_digits=10, decimal_places=2)
