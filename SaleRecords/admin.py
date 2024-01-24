from django.contrib import admin
from SaleRecords.models import *
# Register your models here.


@admin.register (SaleRecords)
class SaleRecords(admin.ModelAdmin):
    list_display = ['id']