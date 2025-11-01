# sales/models.py
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Invoice(models.Model):

    PAYMENT_CASH = 'Cash'
    PAYMENT_INSTALLMENT = 'Installment'
    PAYMENT_CHECK = 'Check'

    PAYMENT_TYPES = (
        (PAYMENT_CASH, 'Cash'),
        (PAYMENT_INSTALLMENT, 'Installment'),
        (PAYMENT_CHECK, 'Check'),
    )

    customer = models.ForeignKey(
        'customers.Customer',
        related_name='customer_sales',
        blank=True, null=True, on_delete=models.SET_NULL
    )

    payment_type = models.CharField(
        choices=PAYMENT_TYPES, default=PAYMENT_CASH, max_length=100)

    bank_details = models.ForeignKey(
        'banking.Bank', related_name='bank_detail_payments',
        blank=True, null=True, on_delete=models.SET_NULL
    )

    total_quantity = models.CharField(
        max_length=10, blank=True, null=True, default=1
    )

    sub_total = models.DecimalField(
        max_digits=65, decimal_places=2, default=0, blank=True, null=True
    )

    paid_amount = models.DecimalField(
        max_digits=65, decimal_places=2, default=0, blank=True, null=True
    )

    remaining_payment = models.DecimalField(
        max_digits=65, decimal_places=2, default=0, blank=True, null=True
    )

    discount = models.DecimalField(
        max_digits=65, decimal_places=2, default=0, blank=True, null=True
    )

    shipping = models.DecimalField(
        max_digits=65, decimal_places=2, default=0, blank=True, null=True
    )

    grand_total = models.DecimalField(
        max_digits=65, decimal_places=2, default=0, blank=True, null=True
    )

    cash_payment = models.DecimalField(
        max_digits=65, decimal_places=2, default=0, blank=True, null=True
    )

    cash_returned = models.DecimalField(
        max_digits=65, decimal_places=2, default=0, blank=True, null=True
    )
    date = models.DateField(default=timezone.now, blank=True, null=True)

    def __str__(self):
        return str(self.id).zfill(7)

    def is_installment(self):
        invoice_installments = InvoiceInstallment.objects.filter(
            invoice__id=self.id)

        grand_total = self.grand_total

        if invoice_installments.exists():
            total_paid_amount = invoice_installments.aggregate(
                Sum('paid_amount'))
            total_paid_amount = float(
                total_paid_amount.get('paid_amount__sum') or 0
            )

        else:
            total_paid_amount = 0

        if float(grand_total) <= total_paid_amount:
            return True

        return False

    def remaining_installment(self):
        invoice_installments = InvoiceInstallment.objects.filter(
            invoice__id=self.id)

        grand_total = self.grand_total

        if invoice_installments.exists():
            total_paid_amount = invoice_installments.aggregate(
                Sum('paid_amount'))
            total_paid_amount = float(
                total_paid_amount.get('paid_amount__sum') or 0
            )

        else:
            total_paid_amount = 0

        return float(grand_total) - total_paid_amount

    def has_installment(self):
        if self.invoice_installment.all().exists():
            return True

        return False




class InvoiceInstallment(models.Model):
    invoice = models.ForeignKey(
        Invoice, related_name='invoice_installment', on_delete=models.CASCADE)
    paid_amount = models.DecimalField(
        max_digits=65, decimal_places=2, default=0, blank=True, null=True
    )
    description = models.TextField(blank=True, null=True)
    date = models.DateField(
        default=timezone.now, blank=True, null=True)

    def __str__(self):
        return (
            '%s Installment' % self.invoice.customer.name if
            self.invoice.customer else ''
        )



# class Invoice(models.Model):
#     customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)
#     date = models.DateTimeField(default=timezone.now)
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_method = models.CharField(max_length=20, choices=[('cash', 'Cash'), ('credit', 'Credit')])

# class InvoiceItem(models.Model):
#     invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
#     product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
#     quantity = models.IntegerField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
