from django.contrib import admin
from SaleRecords.models import *
# Register your models here.


@admin.register (SaleRecords)
class SaleRecords(admin.ModelAdmin):
    list_display = ['id']
    
@admin.register(SaleRecordsAppointmentServices)
class SaleRecordsAppointmentServicesAdmin(admin.ModelAdmin):
    list_display = ['id']

    
@admin.register(SaleRecordServices)
class SaleRecordServicesAdmin(admin.ModelAdmin):
    list_display =['id']
    
@admin.register(SaleRecordsProducts)
class SaleRecordsProductsAdmin(admin.ModelAdmin):
    list_display = ['id']

@admin.register(SaleRecordMembership)
class SaleRecordMembershipAdmin(admin.ModelAdmin):
    list_display = ['id']

@admin.register(SaleRecordVouchers)
class SaleRecordVouchersAdmin(admin.ModelAdmin):
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
    
@admin.register(PurchasedGiftCards)
class PUrchasedGiftCard(admin.ModelAdmin):
    list_display = ['id']
    ordering = ['-created_at']
    
# ============================================= Redeemed Items Records ====================================
    
@admin.register(AppliedMemberships)
class AppliedMembershipsAdmin(admin.ModelAdmin):
    list_display = ['id']
@admin.register(SaleRecordAppliedCoupons)
class SaleRecordAppliedCouponsAdmin(admin.ModelAdmin):
    list_display = ['id']
    
@admin.register(AppliedVouchers)
class AppliedMembershipsAdmin(admin.ModelAdmin):
    list_display = ['id']

@admin.register(AppliedPromotion)
class AppliedPromotionAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(RedeemedLoyaltyPoints)
class RedeemedLoyaltyPointsAdmn(admin.ModelAdmin):
    list_display = ['id', 'clinet_loyalty_point']