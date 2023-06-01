from django.contrib import admin

from .models import Category, Brand, CurrencyRetailPrice, Product, ProductMedia, ProductOrderStockReport, ProductStock, OrderStock, OrderStockProduct, ProductConsumption

admin.site.register(Category)
admin.site.register(Brand)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active']

    
admin.site.register(ProductMedia)
#admin.site.register(ProductStock)
admin.site.register(OrderStock)
admin.site.register(OrderStockProduct)
admin.site.register(ProductConsumption)
admin.site.register(CurrencyRetailPrice)
#admin.site.register(ProductOrderStockReport)
@admin.register(ProductStock)
class ProductStockpAdmin(admin.ModelAdmin):
    list_display= [
                'id', 
                'product',
                'location', 
                'available_quantity',
                   ]
@admin.register(ProductOrderStockReport)
class ProductOrderStockReportAdmin(admin.ModelAdmin):
    list_display= [
                'id', 
                'product',
                'location', 
                'report_choice',
                   ]