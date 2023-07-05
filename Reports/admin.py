from django.contrib import admin
from .models import DiscountPromotionSalesReport
# Register your models here.


@admin.register(DiscountPromotionSalesReport)
class DiscountPromotionSalesReportAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'checkout_type',
        'invoice',
        'promotion_id',
        'promotion_type',
        'promotion_name',
        'location',
        'gst',
        'original_price',
        'discount_price',
    ]