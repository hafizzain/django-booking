from rest_framework import serializers
from SaleRecords.models import *


class SaleRecordsAppointmentServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleRecordsAppointmentServices
        fields = "__all__"
    
class SaleRecordProductsSerializer(serializers.ModelSerializer):
    class Meta: 
        models = SaleRecordsProducts
        fields = "__all__"


class SaleRecordServicesSerializer(serializers.ModelSerializer):
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


class PaymentMethodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethods
        fields = "__all__"

class SaleOrderTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleRecordTip
        fields = '__all__'

class SaleTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleTax
        fields = "__all__"
        
        
# ----------------------------------------------------------------------------------------------------------------------------------

class SaleRecordAppliedCouponsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleRecordAppliedCoupons
        fields = "__all__"
class AppliedMembershipsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppliedMemberships
        fields = "__all__"
        
class AppliedVouchersSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppliedVouchers
        field = "__all__"
        
        
class SaleRecordSerializer(serializers.ModelSerializer):
    appointments_services = SaleRecordsAppointmentServicesSerializer(many= True, write_only = True)
    services = SaleRecordServicesSerializer(many= True, write_only= True)
    products = SaleRecordProductsSerializer(many= True, write_only = True)
    payment_methods = PaymentMethodsSerializer(many = True, write_only = True)
    membership = SaleRecordMembershipSerializer(many = True , write_only = True)
    vouchers = SaleRecordVouchersSerializer(many =True , write_only= True)
    tax = SaleTaxSerializer(many =True, write_only = True)
    tips = SaleOrderTipSerializer(many = True, write_only = True)
    # Applied Items 
    applied_coupons = SaleRecordAppliedCouponsSerializer(many = True)
    applied_memberships = AppliedMembershipsSerializer(many = True)
    applied_vouchers = AppliedVouchersSerializer(many = True)
    
    class Meta:
        model = SaleRecords
        fields = '__all__'
        
    def create(self, validated_data):
        appointments_services_data = validated_data.pop('appointments_services', [])
        services_data = validated_data.pop('services', [])
        products_data = validated_data.pop('products', [])
        payment_methods_data = validated_data.pop('payment_methods',[])
        membership_data = validated_data.pop('membership', [])
        vouchers_data = validated_data.pop('vouchers',[])
        tax_data = validated_data.pop('tax', [])
        tips_data = validated_data.pop('tips', [])

        applied_coupons_data = validated_data.pop('applied_coupons', [])
        applied_vouchers_data  = validated_data.pop('applied_vouchers',[])
        applied_memberships_data  = validated_data.pop('applied_memberships',[])
        
        # =================================================== Checkout Records ========================================================
        '''
            Checkout records are being created here
        '''
        sale_record = SaleRecords.objects.create(**validated_data)
        
        SaleRecordsAppointmentServices.objects.bulk_create([
            SaleRecordsAppointmentServices(sale_record=sale_record, **data) for data in appointments_services_data
        ])

        SaleRecordServices.objects.bulk_create([
            SaleRecordServices(sale_record=sale_record, **data) for data in services_data
        ])

        SaleRecordsProducts.objects.bulk_create([
            SaleRecordsProducts(sale_record=sale_record, **data) for data in products_data
        ])
        
        PaymentMethods.objects.bulk_create([ 
            PaymentMethods(sale_record = sale_record, **data)   for data in payment_methods_data
        ])
        
        SaleRecordMembership.objects.bulk_create([ 
            SaleRecordMembership(sale_record = sale_record , **data) for data in membership_data
        ])
        
        SaleRecordVouchers.objects.bulk_create([ 
            SaleRecordVouchers(sale_record = sale_record , **data) for data in vouchers_data
        ])
        
        SaleRecordVouchers.objects.bulk_create([ 
            SaleRecordVouchers(sale_record = sale_record , **data) for data in vouchers_data
        ])
        
        SaleTax.objects.bulk_create([
            SaleTax(sale_order=sale_record, **data) for data in tax_data
        ])
        
        SaleRecordTip.objects.bulk_create([
            SaleRecordTip(sale_record=sale_record, **data) for data in tips_data
        ])
        
        
        # ============================================================= Redeemed Items records ===================================================================
        '''
        Redeemed Items records is being creating here if any
        '''
        SaleRecordAppliedCoupons.objects.bulk_create([
            SaleRecordAppliedCoupons(sale_records=sale_record, **data) for data in applied_coupons_data
        ])
        AppliedVouchers.objects.bulk_create([
            AppliedVouchers(sale_record = sale_record, **data) for data in applied_vouchers_data
        ])
        AppliedMemberships.objects.bulk_create([
            AppliedMemberships(sale_record=sale_record, **data) for data in applied_memberships_data
        ])
        

        
        
        
        

        return sale_record