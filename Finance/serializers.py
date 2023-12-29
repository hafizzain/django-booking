from rest_framework import serializers
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

    def create(self, validated_data):
        refunded_products_data = validated_data.pop('refunded_products', [])
        refunded_services_data = validated_data.pop('refunded_services', [])

        refund = Refund.objects.create(**validated_data)

        # Create refunded products
        refunded_products_instances = [
            RefundProduct(refund=refund, **product_data)
            for product_data in refunded_products_data
        ]
        RefundProduct.objects.bulk_create(refunded_products_instances)

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
