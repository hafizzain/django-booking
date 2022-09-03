

from unicodedata import category
from rest_framework import serializers
from Product.Constants.index import tenant_media_base_url
from Product.models import Category, Brand, Product, ProductMedia, ProductStock
from Business.models import BusinessVendor
from django.conf import settings



class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    
class SaveFileSerializer(serializers.Serializer):
    
    class Meta:
        model = Product
        fields = "__all__"




class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_active', 'created_at']

class BrandSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return None
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'website', 'image', 'is_active']


class ProductMediaSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context['request']
                url = tenant_media_base_url(request)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return None
    class Meta:
        model = ProductMedia
        fields = ['id', 'image']
        
        
class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessVendor
        fields = '__all__'

class ProductStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStock
        fields = ['id', 'quantity' , 'amount', 'unit' , 'alert_when_stock_becomes_lowest', 'is_active' ]

class ProductWithStockSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()
    category= CategorySerializer(read_only=True)
    brand = serializers.SerializerMethodField()
    vendor= VendorSerializer(read_only=True)
    

    def get_brand(self, obj):
        brand = BrandSerializer(obj.brand, read_only=True, context=self.context)
        return brand.data


    def get_stock(self, obj):
        stock = ProductStock.objects.filter(product=obj, is_deleted=False)[0]
        return {
            'id' : stock.id,
            'available_stock' : stock.available_quantity,
            'quantity' : stock.quantity,
            'sold_stock' : stock.sold_quantity,
            'price' : stock.product.sell_price,
            'usage' : (int(stock.quantity) // int(stock.sold_quantity)) * 100 if stock.sold_quantity > 0 else 100,
            'status' : True if stock.available_quantity > 0 else False,
            'status_text' : 'In Stock' if stock.available_quantity > 0 else 'Out of stock',
            'sale_status' : 'High',
            'turnover' : 'Highest',
        }
        

    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'cost_price',
            'full_price',
            'sell_price',
            'category', 
            'brand', 
            'vendor',
            'stock',
        ]
        read_only_fields = ['id']
        
        

class ProductSerializer(serializers.ModelSerializer):
    brand=BrandSerializer(read_only=True)
    category= CategorySerializer(read_only=True)
    vendor= VendorSerializer(read_only=True)
    
    media = serializers.SerializerMethodField()
    stocks = serializers.SerializerMethodField()

    def get_media(self, obj):
        try:
            context = self.context
        except:
            context = {}
        all_medias = ProductMedia.objects.filter(product=obj, is_deleted=False)
        return ProductMediaSerializer(all_medias, many=True, context=context).data

    def get_stocks(self, obj):
        all_stocks = ProductStock.objects.filter(product=obj, is_deleted=False)
        return ProductStockSerializer(all_stocks, many=True).data


    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'vendor',
            'category',
            'brand',    
            'product_type',
            'cost_price',
            'full_price',
            'sell_price',
            'tax_rate',
            'short_description',
            'description',
            'barcode_id',
            'sku',
            'slug',
            'is_active',
            'media',
            'stocks',
        ]
        read_only_fields = ['slug', 'id']