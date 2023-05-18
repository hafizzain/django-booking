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
    list_display = ['id', 'is_promotion']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'total_price', 'price']

    
admin.site.register(CheckoutPayment)