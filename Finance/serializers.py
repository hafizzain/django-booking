# serializers.py

from rest_framework import serializers
from Finance.models import Refund, RefundProduct, Coupon

class RefundProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundProduct
        fields = '__all__'

class RefundSerializer(serializers.ModelSerializer):
    refunded_products = RefundProductSerializer(many=True)

    class Meta:
        model = Refund
        fields = '__all__'

    def create(self, validated_data):
        refunded_products_data = validated_data.pop('refunded_products')
        refund = Refund.objects.create(**validated_data)

        refund_products_instances = [
            RefundProduct(refund=refund, **refunded_product_data)
            for refunded_product_data in refunded_products_data
        ]
        RefundProduct.objects.bulk_create(refund_products_instances)

        return refund


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
