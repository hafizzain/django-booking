# from django.contrib import admin
# from .models import Refund, RefundProduct, Coupon
# # Register your models here.

# @admin.register(Coupon)
# class Coupon(admin.TabularInline):
#     model = Coupon
# @admin.register(RefundProduct)
# class RefundProductsAdmin(admin.TabularInline):
#     model = RefundProduct
    
# # class RefundServicesAdmin(RefundServices):
# #     model = RefundServices

# @admin.register(Refund)
# class RefundAdmin(admin.ModelAdmin):
#     inlines = [RefundProductsAdmin,Coupon]
#     ordering = ['-created_at']
#     list_display = ['id','user','refund_invoice_id','refund_type','total_refund_amount']