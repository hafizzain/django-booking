from django.contrib import admin
from Finance.models import Refund, RefundProduct, Coupon

class CouponInline(admin.TabularInline):
    model = Coupon

class RefundProductsAdmin(admin.TabularInline):
    model = RefundProduct
    
@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    inlines = [RefundProductsAdmin, CouponInline]
    ordering = ['-created_at']
    list_display = ['id', 'user', 'refund_invoice_id', 'refund_type', 'total_refund_amount']