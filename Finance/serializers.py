
from django.db import transaction
from rest_framework import serializers
from Finance.models import Refund, RefundProduct, RefundServices ,Coupon
from Product.models import Product
from Service.models import Service
from Client.models import Client
from django.shortcuts import get_object_or_404

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
    return f"Validated Data RP: {validated_data.pop('refunded_products')}, Only Valdated Data : {validated_data} "
    # refund_services_data = validated_data.pop('refunded_services')
    # refund = Refund.objects.create(**validated_data)
    # refund.save()
    
    # if refunded_products_data:
    #     refund_products_instances = [
    #         RefundProduct(refund= refund,product=Product.objects.get(id=refunded_product_data['product']))
    #         for refunded_product_data in refunded_products_data
    #     ]
    #     # refund_service = RefundServices.objects.bulk_create(refunded_services_instances)
    #     # refund.refundproduct_set.set(refund_products)
    #     return RefundProduct
        
    # if refund_services_data : 
    #     refunded_services_instances = [
    #         RefundServices(refund= refund,service = get_object_or_404(Service, id = refunded_service_data['service']))
    #         for refunded_service_data in refund_services_data
    #     ]
    #     # refund_products = RefundProduct.objects.bulk_create(refund_products_instances)
    #     # refund.refundedservices_set.set(refund_service)

    # return refund


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
