from django.contrib import admin

from .models import Category, Brand, CurrencyRetailPrice, Product, ProductMedia, ProductOrderStockReport, ProductStock, OrderStock, OrderStockProduct, ProductConsumption, ProductTranslations

admin.site.register(Category)
admin.site.register(Brand)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'arabic_id', 'name', 'arabic_name', 'is_active']

    
@admin.register(ProductMedia)
class ProductMediaAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'image_path',
        'image_name'
    ]

    def image_name(self, obj):
        if obj.image:
            return obj.image.name

    def image_path(self, obj):
        if obj.image:
            return obj.image.path
#admin.site.register(ProductStock)
admin.site.register(OrderStock)
admin.site.register(OrderStockProduct)
@admin.register(ProductConsumption)
class ProductConsumptionAdmin(admin.ModelAdmin):
    list_display= [
        'id', 
        'created_at', 
    ]


admin.site.register(CurrencyRetailPrice)
#admin.site.register(ProductOrderStockReport)
@admin.register(ProductStock)
class ProductStockpAdmin(admin.ModelAdmin):
    list_filters = ['product']
    list_display= [
        'id', 
        'product_name',
        'location', 
        'available_quantity',
    ]

    def product_name(self, stock_instance):
        if stock_instance.product:
            return f'{stock_instance.product.id}-{stock_instance.product.name}'
        
        return '-------'


@admin.register(ProductOrderStockReport)
class ProductOrderStockReportAdmin(admin.ModelAdmin):
    list_display= [
                'id', 
                'product',
                'location', 
                'from_location',
                'to_location',
                'report_choice',
            ]
    
admin.site.register(ProductTranslations)