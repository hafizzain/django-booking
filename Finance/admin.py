from django.contrib import admin
from Finance.models import Refund, RefundProduct, RefundServices ,RefundCoupon, AllowRefundPermissionsEmployees, AllowRefunds

@admin.register(RefundCoupon)
class RefundCouponAdmin(admin.ModelAdmin):
    list_display = ['id','refund_coupon_code','amount','expiry_date','is_used']


@admin.register(RefundProduct)
class RefundProductsAdmin(admin.ModelAdmin):
    list_display = ['id','refunded_quantity','refunded_amount','in_stock']

@admin.register(RefundServices)
class RefundServiceAdmin(admin.ModelAdmin):
    list_display = ['id','service','refunded_amount']
    
@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    ordering = ['-created_at']
    list_display = ['id', 'user', 'refund_invoice_id', 'business','refund_type', 'total_refund_amount']
    
    
@admin.register(AllowRefunds)
class AllowRefundAdmin(admin.ModelAdmin):
    list_display = ['id','location', 'number_of_days']
    
@admin.register(AllowRefundPermissionsEmployees)
class AllowedRefundEmployeesAdmin(admin.ModelAdmin):
    list_display = ['id', 'allowed_refund','employee']