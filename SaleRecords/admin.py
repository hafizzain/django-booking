from django.contrib import admin
from SaleRecords.models import *
# Register your models here.


@admin.register (SaleRecords)
class SaleRecords(admin.ModelAdmin):
    list_display = ['id','status','checkout_type','sub_total','total_price','created_at']
    ordering = ['-created_at']
    
@admin.register(SaleRecordsAppointmentServices)
class SaleRecordsAppointmentServicesAdmin(admin.ModelAdmin):
    list_display = ['id','sale_record','price','created_at']
    ordering = ['-created_at']

    
@admin.register(SaleRecordServices)
class SaleRecordServicesAdmin(admin.ModelAdmin):
    list_display =['id','sale_record','price','created_at']
    ordering = ['-created_at']
    
@admin.register(SaleRecordsProducts)
class SaleRecordsProductsAdmin(admin.ModelAdmin):
    list_display = ['id','sale_record','price','created_at']
    ordering = ['-created_at']

@admin.register(SaleRecordMembership)
class SaleRecordMembershipAdmin(admin.ModelAdmin):
    list_display = ['id']
    ordering = ['-created_at']

@admin.register(SaleRecordVouchers)
class SaleRecordVouchersAdmin(admin.ModelAdmin):
    list_display = ['id']
    ordering = ['-created_at']
    
@admin.register(SaleRecordTip)
class SaleRecordAppliedCouponsAdmin(admin.ModelAdmin):
    list_display = ['id']
    ordering = ['-created_at']
    
@admin.register(SaleTax)
class SaleTaxAdmin(admin.ModelAdmin):
    list_display = ['id']
    ordering = ['-created_at']
    
@admin.register(PaymentMethods)
class PaymentMethodsAdmin(admin.ModelAdmin):
    list_display = ['id']
    ordering = ['-created_at']
    
@admin.register(PurchasedGiftCards)
class PUrchasedGiftCard(admin.ModelAdmin):
    list_display = ['id']
    ordering = ['-created_at']
    
# ============================================= Redeemed Items Records ====================================
    
@admin.register(AppliedMemberships)
class AppliedMembershipsAdmin(admin.ModelAdmin):
    list_display = ['id']
    ordering = ['-created_at']
@admin.register(SaleRecordAppliedCoupons)
class SaleRecordAppliedCouponsAdmin(admin.ModelAdmin):
    list_display = ['id']
    ordering = ['-created_at']
    
@admin.register(AppliedVouchers)
class AppliedMembershipsAdmin(admin.ModelAdmin):
    list_display = ['id']
    ordering = ['-created_at']

@admin.register(AppliedPromotion)
class AppliedPromotionAdmin(admin.ModelAdmin):
    list_display = ['id']
    ordering = ['-created_at']

@admin.register(RedeemedLoyaltyPoints)
class RedeemedLoyaltyPointsAdmn(admin.ModelAdmin):
    list_display = ['id', 'clinet_loyalty_point']
    ordering = ['-created_at']