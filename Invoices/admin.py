from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(SaleInvoice)
class SaleInvoiceAdmin(admin.ModelAdmin):
    ordering = ['-created_at']
    list_display = [
        'id',
        'file',
        'checkout',
        'created_at'
    ]
