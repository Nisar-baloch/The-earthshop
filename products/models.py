from django.db import models
from django.utils import timezone
from django.db.models import F
# Create your models here.
    

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date = models.DateField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    stock = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    # selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    # company = models.CharField(max_length=200, blank=True)
    # barcode = models.CharField(max_length=100, blank=True)
    date = models.DateField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return self.name



# products/models.py

class StockIn(models.Model):
    product = models.ForeignKey(
        'products.Product', related_name='stockin_product',
        on_delete=models.CASCADE
    )
    buying_price_item = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    buying_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                         help_text="Buying percent (if applicable)")
    stock_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_buying_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # NEW fields for selling
    selling_price_item = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_selling_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']

    def save(self, *args, **kwargs):
        # compute totals (buying and selling) before saving
        try:
            qty = float(self.stock_quantity or 0)
            buy_price = float(self.buying_price_item or 0)
            buy_percent = float(self.buying_percent or 0)
            sell_price = float(self.selling_price_item or 0)
            # buying: price * qty * (1 + percent/100)
            self.total_buying_amount = round(buy_price * qty * (1 + buy_percent / 100.0), 2)
            # selling total
            self.total_selling_amount = round(sell_price * qty, 2)
        except Exception:
            self.total_buying_amount = 0
            self.total_selling_amount = 0

        is_new = self._state.adding
        super().save(*args, **kwargs)

        # Atomic stock update only for new records
        if is_new:
            try:
                self.product.stock = F('stock') + self.stock_quantity
                self.product.save(update_fields=['stock'])
            except Exception:
                # safe fallback: ignore stock update failure here and let admin correct
                pass

    def __str__(self):
        return f"StockIn: {self.product.name} (+{self.stock_quantity}) on {self.date}"


# --- StockOut model: when created, decreases product.stock ---
class StockOut(models.Model):
    product = models.ForeignKey('Product', related_name='stockout_product', on_delete=models.CASCADE)
    stock_out_quantity = models.PositiveIntegerField(default=0)
    date = models.DateField(default=timezone.now)
    invoice = models.ForeignKey(
        'sales.Invoice', related_name='invoice_stockout',
        blank=True, null=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.product.name} - {self.stock_out_quantity}"