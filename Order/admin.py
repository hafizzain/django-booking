from django.contrib import admin 
from Order.models import Order, ProductOrder, ServiceOrder , MemberShipOrder ,VoucherOrder, Checkout , CheckoutPayment

# Register your models here.
admin.site.register(ProductOrder)
admin.site.register(ServiceOrder)
admin.site.register(MemberShipOrder)


@admin.register(VoucherOrder)
class VoucherOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'start_date', 'end_date']



admin.site.register(Checkout)
admin.site.register(CheckoutPayment)