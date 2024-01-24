from django.contrib import admin
from SaleRecords.models import *
# Register your models here.


@admin.register (SaleRecords)
class SaleRecords(admin.ModelAdmin):
    list_display = ['id']
    
@admin.register(SaleRecordsAppointmentServices)
class SaleRecordsAppointmentServicesAdmin(admin.ModelAdmin):
    list_display = ['id']

@admin.register(SaleRecordAppliedCoupons)
class SaleRecordAppliedCouponsAdmin(admin.ModelAdmin):
    list_display = ['id']
    
@admin.register(SaleRecordServices)
class SaleRecordServicesAdmin(admin.ModelAdmin):
    list_display =['id']
    
@admin.register(SaleRecordsProducts)
class SaleRecordsProductsAdmin(admin.ModelAdmin):
    list_display = ['id']
    
    
@admin.register(SaleRecordTip)
class SaleRecordAppliedCouponsAdmin(admin.ModelAdmin):
    list_display = ['id']
    
@admin.register(SaleTax)
class SaleTaxAdmin(admin.ModelAdmin):
    list_display = ['id']
    
@admin.register(PaymentMethods)
class PaymentMethodsAdmin(admin.ModelAdmin):
    list_display = ['id']
    
@admin.register(RedeemedItems)
class RedeemedItems(admin.ModelAdmin):
    list_display = ['id']