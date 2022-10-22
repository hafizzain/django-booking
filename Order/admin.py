from django.contrib import admin 
from Order.models import Order, ProductOrder, ServiceOrder , MemberShipOrder ,VoucherOrder

# Register your models here.
admin.site.register(ProductOrder)
admin.site.register(ServiceOrder)
admin.site.register(MemberShipOrder)
admin.site.register(VoucherOrder)