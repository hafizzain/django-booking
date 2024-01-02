from rest_framework import serializers
from django.db.models import F 
from django.db import transaction
from Product.models import ProductStock, Product
from Finance.models import Refund, RefundProduct, RefundServices ,RefundCoupon

class RefundProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundProduct
        fields = '__all__'
        read_only_fields = ['refund']

class RefundServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundServices
        fields = '__all__'
        read_only_fields = ['refund']
    
class RefundSerializer(serializers.ModelSerializer):
    refunded_products = RefundProductSerializer(many=True)
    refunded_services = RefundServiceSerializer(many=True)

    class Meta:
        model = Refund
        fields = '__all__'
        
    '''
    This fundtion is updating the stock if the product has the in_stock key. Only thoes product record will be update in the ProductStock
    '''
    def product_stock_update(self, location,refunded_products_data):
        [ProductStock.objects.filter(product_id=product_data["product"], location_id = location).update(sold_quantity=F('sold_quantity') - product_data["refunded_quantity"], available_quantity=F('available_quantity') + product_data['refunded_quantity'], is_refunded = True)
                                for product_data in refunded_products_data if product_data['in_stock'] == True]
        return True
    
    def create(self, validated_data):  # sourcery skip: extract-method
        request = self.context.get('request')
        location = request.data.get('location')
        refunded_products_data = validated_data.pop('refunded_products', [])
        refunded_services_data = validated_data.pop('refunded_services', [])
        with transaction.atomic():
            refund = Refund.objects.create(**validated_data)

            # Create refunded products
            refunded_products_instances = [
                RefundProduct(refund=refund, **product_data)
                for product_data in refunded_products_data
            ]
            
            RefundProduct.objects.bulk_create(refunded_products_instances)
            self.product_stock_update(location,refunded_products_data)
            
            # Create refunded services
            refunded_services_instances = [
                RefundServices(refund=refund, **service_data)
                for service_data in refunded_services_data
            ]
            RefundServices.objects.bulk_create(refunded_services_instances)

        return refund


class CouponSerializer(serializers.ModelSerializer):
    related_refund = RefundSerializer(read_only = True)
    class Meta:
        model = RefundCoupon
        fields = '__all__'
