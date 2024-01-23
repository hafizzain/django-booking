from rest_framework import serializers
from SaleRecords.models import *



class SaleOrderTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleRecordTip
        fields = '__all__'
        
class SaleRecordsAppointmentServicesSerializer(serializers.ModelSerializer):
    class Meta:
        models = SaleRecordsAppointmentServices
        fields = "__all__"
    
class SaleRecordProductsSerializer(serializers.ModelSerializer):
    class Meta: 
        models = SaleRecordsProducts
        fields = "__all__"


class  SaleRecordServicesSerializer(serializers.ModelSerializer):
    class Meta:
        models = SaleRecordServices
        fields = "__all__"

class SaleRecordAppliedCouponsSerializer(serializers.ModelSerializer):
    class Meta:
        models = SaleRecordAppliedCoupons
        fields = "__all__"

class PaymentMethodsSerializer(serializers.ModelSerializer):
    class Meta:
        models = PaymentMethods
        fields = "__all__"

class RedeemedItemsSerializer(serializers.ModelSerializer):
    class Meta: 
        models = RedeemedItems
        fields = "__all__"


class SaleTaxSerializer(serializers.ModelSerializer):
    class Meta:
        models = SaleTax
        fields = "__all__"
        
class SaleRecordSerializer(serializers.ModelSerializer):
    appointments_services = SaleRecordsAppointmentServicesSerializer(read_only = True)
    tips = SaleOrderTipSerializer(many = True, read_only = True)
    services = SaleRecordServicesSerializer(many= True, read_only= True)
    products = SaleRecordProductsSerializer(many= True, read_only = True)
    applied_coupons = SaleRecordAppliedCouponsSerializer(many= True , read_only = True)
    redeemed_items = RedeemedItemsSerializer(many= True , read_only = True)
    tax = SaleTaxSerializer(many =True, read_only = True)
    class Meta:
        model = SaleRecords
        fields = '__all__'
        
    def create(self, validated_data):
        pass