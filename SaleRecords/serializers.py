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

class SaleRecordAppliedCouponsSerializer(serializers.ModelSerializer):
    class Meta:
        models = SaleRecordAppliedCoupons
        fields = "__all__"

class SaleRecordSerializer(serializers.ModelSerializer):
    sale_record_appointments_services = SaleRecordsAppointmentServicesSerializer(read_only = True)
    sale_record_tips = SaleOrderTipSerializer(many = True, read_only = True)
    sale_record_services = SaleRecordProductsSerializer(many= True, read_only= True)
    sale_record_prodcuts = SaleRecordProductsSerializer(many= True, read_only = True)
    sale_record_applied_coupons = SaleRecordAppliedCouponsSerializer(many= True , read_only = True)
    class Meta:
        model = SaleRecords
        fields = '__all__'
