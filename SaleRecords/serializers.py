from rest_framework import serializers
from SaleRecords.models import *



class SaleOrderTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleRecordTip
        fields = '__all__'
        
class SaleRecordsAppointmentServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleRecordsAppointmentServices
        fields = "__all__"
    
class SaleRecordProductsSerializer(serializers.ModelSerializer):
    class Meta: 
        models = SaleRecordsProducts
        fields = "__all__"


class  SaleRecordServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleRecordServices
        fields = "__all__"
        
class SaleRecordVouchersSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleRecordVouchers
        fields = '__all__'
        
class SaleRecordMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleRecordMembership
        fields = "__all__"

class SaleRecordAppliedCouponsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleRecordAppliedCoupons
        fields = "__all__"

class PaymentMethodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethods
        fields = "__all__"

class RedeemedItemsSerializer(serializers.ModelSerializer):
    class Meta: 
        model = RedeemedItems
        fields = "__all__"


class SaleTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleTax
        fields = "__all__"
        
class SaleRecordSerializer(serializers.ModelSerializer):
    appointments_services = SaleRecordsAppointmentServicesSerializer(many= True, write_only = True)
    tips = SaleOrderTipSerializer(many = True, write_only = True)
    services = SaleRecordServicesSerializer(many= True, write_only= True)
    products = SaleRecordProductsSerializer(many= True, write_only = True)
    vouchers = SaleRecordVouchersSerializer(many =True , write_only= True)
    membership = SaleRecordMembershipSerializer(many = True , write_only = True)
    applied_coupons = SaleRecordAppliedCouponsSerializer(many= True , write_only = True)
    redeemed_items = RedeemedItemsSerializer(many= True , write_only = True)
    tax = SaleTaxSerializer(many =True, write_only = True)
    class Meta:
        model = SaleRecords
        fields = '__all__'
        
    def create(self, validated_data):
        appointments_services_data = validated_data.pop('appointments_services', [])
        tips_data = validated_data.pop('tips', [])
        services_data = validated_data.pop('services', [])
        products_data = validated_data.pop('products', [])
        applied_coupons_data = validated_data.pop('applied_coupons', [])
        redeemed_items_data = validated_data.pop('redeemed_items', [])
        tax_data = validated_data.pop('tax', [])

        sale_record = SaleRecords.objects.create(**validated_data)

        # Create related records
        SaleRecordsAppointmentServices.objects.bulk_create([
            SaleRecordsAppointmentServices(sale_record=sale_record, **data) for data in appointments_services_data
        ])

        SaleRecordTip.objects.bulk_create([
            SaleRecordTip(sale_record=sale_record, **data) for data in tips_data
        ])
        SaleRecordMembership.objects.bulk_create([
            
        ])
        SaleRecordServices.objects.bulk_create([
            SaleRecordServices(sale_record=sale_record, **data) for data in services_data
        ])

        SaleRecordsProducts.objects.bulk_create([
            SaleRecordsProducts(sale_record=sale_record, **data) for data in products_data
        ])

        SaleRecordAppliedCoupons.objects.bulk_create([
            SaleRecordAppliedCoupons(sale_records=sale_record, **data) for data in applied_coupons_data
        ])

        RedeemedItems.objects.bulk_create([
            RedeemedItems(sale_order=sale_record, **data) for data in redeemed_items_data
        ])

        SaleTax.objects.bulk_create([
            SaleTax(sale_order=sale_record, **data) for data in tax_data
        ])
        
        

        return sale_record