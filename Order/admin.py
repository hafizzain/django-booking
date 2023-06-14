from django.contrib import admin 
from Order.models import Order, ProductOrder, ServiceOrder , MemberShipOrder ,VoucherOrder, Checkout , CheckoutPayment

# Register your models here.
admin.site.register(ProductOrder)
admin.site.register(ServiceOrder)
admin.site.register(MemberShipOrder)


@admin.register(VoucherOrder)
class VoucherOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'start_date', 'end_date']



@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = ['id', 'location', 'is_promotion', 'selected_promotion_id', 'selected_promotion_type', 'tax_applied', 'tax_amount', 'created_at',]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    ordering = ['-created_at']
    list_display = ['id', 'total_price', 'current_price', 'price', 'discount_price', 'discount_percentage']

    
admin.site.register(CheckoutPayment)