# products/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CategoryForm, ProductForm, StockInForm, StockOutForm 
from .models import Product, Category, StockIn, StockOut
from django.utils import timezone



# CATEGORY
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products:product_list')
    else:
        form = CategoryForm()
    return render(request, 'products/add_category.html', {'form': form})

# def category_list(request):
#     categories = Category.objects.all()
#     return render(request, 'products/category_list.html', {'categories': categories})

# PRODUCT
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created.")
        else:
            # show errors in template
            
            return redirect('products:product_list')  # 👈 redir
        
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/update_product.html', {'form': form})

def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect('products:product_list')
    return render(request, 'products/delete_product.html', {'product': product})
# products/views.py (paste/replace the functions below)

def add_stock(request):
    """
    Manual add-stock form only.
    If GET has ?product=ID, prefill the product select and show read-only product_display.
    After POST, redirect to product-specific stockin list so user sees the new entry at top.
    """
    product_id = request.GET.get('product') or request.POST.get('product')
    product = None
    initial = {}

    if product_id:
        product = get_object_or_404(Product, pk=product_id)
        initial['product'] = product.id
        # attempt to use product fields as defaults (if present)
        if hasattr(product, 'buying_price'):
            initial['buying_price_item'] = product.buying_price
        if hasattr(product, 'selling_price'):
            initial['selling_price_item'] = product.selling_price

    if request.method == 'POST':
        form = StockInForm(request.POST)
        if form.is_valid():
            stockin = form.save()
            messages.success(request, "Stock added successfully.")
            return redirect('products:product_stockins', product_id=stockin.product.id)
    else:
        form = StockInForm(initial=initial)

    product_display = None
    if product:
        # Some projects store category name in different attribute — try .name then .category
        catname = getattr(product.category, 'name', getattr(product.category, 'category', ''))
        product_display = f"{product.name} | {catname}" if catname else f"{product.name}"

    return render(request, 'products/add_stock.html', {
        'form': form,
        'product': product,
        'product_display': product_display,
    })





# Product-specific StockOut list
def product_stockouts(request, pk):
    product = get_object_or_404(Product, pk=pk)
    stockouts = StockOut.objects.filter(product=product).order_by('-id')
    return render(request, 'products/stockout_list.html', {
        'product': product,
        'stockouts': stockouts,
        'product_specific': True
    })


# Add StockOut manually
def add_stock_out(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = StockOutForm(request.POST)
        if form.is_valid():
            stockout = form.save(commit=False)
            stockout.product = product
            stockout.save()
            return redirect('products:product_stockouts', pk=product.pk)
    else:
        form = StockOutForm(initial={
            'product': product,
            'date': timezone.now().date()
        })

    return render(request, 'products/add_stockout.html', {
        'form': form,
        'product': product
    })



def available_stock(self):
    stockin_total = self.stockin_product.aggregate(Sum('stock_quantity'))['stock_quantity__sum'] or 0
    stockout_total = self.stockout_product.aggregate(Sum('stock_out_quantity'))['stock_out_quantity__sum'] or 0
    return stockin_total - stockout_total

# STOCKIN - product-specific list (NEW)
# -------------------------
def product_stockins(request, product_id):
    """
    Show only stock-ins for a single product.
    Newest first: order by -date, -id so newest rows appear at top.
    """
    product = get_object_or_404(Product, pk=product_id)
    stockins = StockIn.objects.filter(product=product).order_by('-date', '-id')
    return render(request, 'products/stockin_list.html', {
        'product': product,
        'stockins': stockins,
        'product_specific': True,
    })


    
# List all stockins
def stockin_list(request):
    stockins = StockIn.objects.select_related('product', 'product__category').all().order_by('-date', '-id')
    return render(request, 'products/stockin_list.html', {'stockins': stockins, 'product_specific': False})

# StockIn detail (shows related stockins for a product or a specific record)
def stockin_detail(request, pk):
    stockin = get_object_or_404(StockIn, pk=pk)
    # also show an Add Stock modal (form) - template will include modal markup
    form = StockInForm()
    return render(request, 'products/stockin_detail.html', {'stockin': stockin, 'form': form})


def stockout_list(request):
    stockouts = StockOut.objects.select_related('product', 'invoice').all().order_by('-date', '-id')
    return render(request, 'products/stockout_list.html', {'stockouts': stockouts, 'product_specific': False})


# StockOut detail
def stockout_detail(request, pk):
    stockout = get_object_or_404(StockOut, pk=pk)
    form = StockOutForm()
    return render(request, 'products/stockout_detail.html', {'stockout': stockout, 'form': form})