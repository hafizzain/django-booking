from django.contrib import admin 
from Order.models import Order, ProductOrder, ServiceOrder , MemberShipOrder ,VoucherOrder, Checkout , CheckoutPayment

# Register your models here.
admin.site.register(ProductOrder)
@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_filter = [
        'location__address_name',
        'created_at',
    ]
    list_display = [
        'id', 
        'location',
        'quantity',
        'total_price',
        'sold_quantity',
        'discount_price',
        'price',
        'created_at',
    ]

admin.site.register(MemberShipOrder)


@admin.register(VoucherOrder)
class VoucherOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'start_date', 'end_date']



@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = ['id', 'location', 'is_promotion', 'selected_promotion_id', 'selected_promotion_type', 'tax_applied', 'tax_amount', 'created_at',
        'total_service_price',
        'total_product_price',
        'total_voucher_price',
        'total_membership_price',
    ]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    ordering = ['-created_at']
    list_display = ['id', 'location', 'total_price', 'member', 'quantity', 'current_price', 'price', 'discount_price', 'discount_percentage']

    
admin.site.register(CheckoutPayment)