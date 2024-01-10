from django.contrib import admin 
from Order.models import Order, ProductOrder, ServiceOrder , MemberShipOrder ,VoucherOrder, Checkout , CheckoutPayment
from Service.models import ServiceGroup

# Register your models here.
admin.site.register(ProductOrder)
@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    ordering = ['-created_at']
    list_filter = [
        'location__address_name',
        'service__name',
        'created_at',
    ]
    list_display = [
        'id', 
        'location_name',
        'service_name',
        'service_group_name',
        'quantity',
        'duration_text',
        'total_price',
        'sold_quantity',
        'discount_price',
        'price',
        'created_at',
    ]
    # search_fields = ('id')
    def location_name(self, order):
        if order.location:
            return order.location.address_name
    
    def service_name(self, order):
        if order.service:
            return order.service.name

    def duration_text(self, order):
        return f'{order.duration}'

    def service_group_name(self, service):
        groups = ServiceGroup.objects.filter(
            services = service.service,
            is_deleted = False
        )

        if len(groups) > 0:
            return groups[0].name


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
    # search_fields = ('id')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    ordering = ['-created_at']
    list_display = ['id', 'location', 'total_price', 'member', 'quantity', 'current_price', 'price', 'discount_price', 'discount_percentage']
    # search_fields = ('id')

    
admin.site.register(CheckoutPayment)