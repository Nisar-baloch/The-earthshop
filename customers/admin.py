from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'father_name', 'address', 'city', 'cnic', 'resident')
    search_fields = ('name', 'phone')

# Register your models here.
