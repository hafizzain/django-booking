

from rest_framework import serializers
from Product.models import Category, Brand, Product, ProductMedia, ProductStock



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_active']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'website', 'image', 'is_active']


class ProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = ['id', 'image']

class ProductStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStock
        fields = ['id', 'quantity' , 'amount', 'unit' , 'alert_when_stock_becomes_lowest']


class ProductSerializer(serializers.ModelSerializer):

    media = serializers.SerializerMethodField()
    stocks = serializers.SerializerMethodField()

    def get_media(self, obj):
        all_medias = ProductMedia.objects.filter(product=obj, is_deleted=False)
        return ProductMediaSerializer(all_medias, many=True).data

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
            'short_description',
            'description',
            'barcode_id',
            'sku',
            'slug',
            'is_active',
            'media',
            'stocks',
        ]