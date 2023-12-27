# serializers.py
from django.db import transaction
from rest_framework import serializers
from Finance.models import Refund, RefundProduct, Coupon
from Product.models import Product
from Client.models import Client
from django.shortcuts import get_object_or_404

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

        # Create RefundProduct instances and set the refund field
        refund_products_instances = []
        for refunded_product_data in refunded_products_data:
            refunded_product_data['refund'] = refund  # Set the refund field
            product_instance = get_object_or_404(Product, id=refunded_product_data['product'])
            refund_products_instances.append(RefundProduct(product=product_instance, **refunded_product_data))

        # Bulk create RefundProduct instances
        RefundProduct.objects.bulk_create(refund_products_instances)

        return refund


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
