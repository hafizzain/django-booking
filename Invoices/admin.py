from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(SaleInvoice)
class SaleInvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'file'
    ]
