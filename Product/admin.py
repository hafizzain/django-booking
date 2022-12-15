from django.contrib import admin

from .models import Category, Brand, Product, ProductMedia, ProductStock, OrderStock, OrderStockProduct, ProductConsumption

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductMedia)
admin.site.register(ProductStock)
admin.site.register(OrderStock)
admin.site.register(OrderStockProduct)
admin.site.register(ProductConsumption)
@admin.register(ProductStock)
class ProductStockpAdmin(admin.ModelAdmin):
    list_display= [
                'id', 
                'product',
                'location', 
                'available_quantity',
                   ]