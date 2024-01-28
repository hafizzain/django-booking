from rest_framework import serializers
from SaleRecords.models import *
from django.db import transaction


class SaleRecordsAppointmentServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleRecordsAppointmentServices
        fields = "__all__"
        read_only_fields = ['sale_record']
    
class SaleRecordProductsSerializer(serializers.ModelSerializer):
    class Meta: 
        model = SaleRecordsProducts
        fields = "__all__"
        read_only_fields = ['sale_record']


class SaleRecordServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleRecordServices
        fields = "__all__"
        read_only_fields = ['sale_record']
        
class SaleRecordVouchersSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleRecordVouchers
        fields = '__all__'
        read_only_fields = ['sale_record']

class PurchasedGiftCardsSerilizer(serializers.ModelSerializer):
    class Meta:
        model = PurchasedGiftCards
        fields = "__all__"
        read_only_fields = ['sale_record']
        
        
class SaleRecordMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleRecordMembership
        fields = "__all__"
        read_only_fields = ['sale_record']


class PaymentMethodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethods
        fields = "__all__"
        read_only_fields = ['sale_record']

class SaleOrderTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleRecordTip
        fields = '__all__'
        read_only_fields = ['sale_record']

class SaleTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleTax
        fields = "__all__"
        read_only_fields = ['sale_record']
        
# ====================================================================== Applied Items Serializer ===================================================

class SaleRecordAppliedCouponsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleRecordAppliedCoupons
        fields = "__all__"
        read_only_fields = ['sale_record']
class AppliedMembershipsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppliedMemberships
        fields = "__all__"
        read_only_fields = ['sale_record']
        
class AppliedVouchersSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppliedVouchers
        fields = "__all__"
        read_only_fields = ['sale_record']
        
class AppliedGiftCardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppliedGiftCards
        fields = "__all__"
        read_only_fields = ['sale_record']

        
class SaleRecordSerializer(serializers.ModelSerializer):
    
    appointment_services = SaleRecordsAppointmentServicesSerializer(many= True)
    services_records = SaleRecordServicesSerializer(many= True)
    products_records = SaleRecordProductsSerializer(many= True)
    payment_methods_records = PaymentMethodsSerializer(many = True)
    gift_cards_records = PurchasedGiftCardsSerilizer(many = True)
    membership_records = SaleRecordMembershipSerializer(many = True )
    vouchers_records = SaleRecordVouchersSerializer(many =True )
    tax_records = SaleTaxSerializer(many =True)
    tip_records = SaleOrderTipSerializer(many = True)
    
    # ================================================================   Applied Items  ==========================================
    applied_coupons_records = SaleRecordAppliedCouponsSerializer(many = True)
    applied_memberships_records = AppliedMembershipsSerializer(many = True)
    applied_vouchers_records = AppliedVouchersSerializer(many = True)
    applied_gift_cards_records = AppliedGiftCardsSerializer(many = True)
    
    
    class Meta:
        model = SaleRecords
        fields = '__all__'
    
    def validate(self, data):
        # Validate that there is at least one record in appointment_services, services_records, and products_records

        if not data.get('appointment_services') and not data.get('services_records') and not data.get('products_records'):
            raise serializers.ValidationError("At least one record is required in appointment_services, services_records, or products_records.")

        return data
        
    def create(self, validated_data):
        
        appointment_services = validated_data.pop('appointment_services', [])
        services_records = validated_data.pop('services_records', [])
        products_records = validated_data.pop('products_records', [])
        payment_methods_records = validated_data.pop('payment_methods_records', [])
        gift_cards_records = validated_data.pop('gift_cards_records', [])
        membership_records = validated_data.pop('membership_records', [])
        vouchers_records = validated_data.pop('vouchers_records', [])
        tax_records = validated_data.pop('tax_records', [])
        tip_records = validated_data.pop('tip_records', [])

        applied_coupons_records = validated_data.pop('applied_coupons_records', [])
        applied_vouchers_records = validated_data.pop('applied_vouchers_records', [])
        applied_memberships_records = validated_data.pop('applied_memberships_records', [])
        applied_gift_cards_records = validated_data.pop('applied_gift_cards_records', [])
        
        
        # =================================================== Checkout Records ========================================================
        '''
            Checkout records are being created here
        '''
        
        with transaction.atomic():
            
            sale_record = SaleRecords.objects.create(**validated_data)
            
            # Create records for SaleRecordsAppointmentServices
            SaleRecordsAppointmentServices.objects.bulk_create([
                SaleRecordsAppointmentServices(sale_record=sale_record, **data) for data in appointment_services
            ])

            # Create records for SaleRecordServices
            SaleRecordServices.objects.bulk_create([
                SaleRecordServices(sale_record=sale_record, **data) for data in services_records
            ])

            # Create records for SaleRecordsProducts
            SaleRecordsProducts.objects.bulk_create([
                SaleRecordsProducts(sale_record=sale_record, **data) for data in products_records
            ])

            # Create records for PaymentMethods
            PaymentMethods.objects.bulk_create([
                PaymentMethods(sale_record=sale_record, **data) for data in payment_methods_records
            ])

            # Create records for SaleRecordMembership
            SaleRecordMembership.objects.bulk_create([
                SaleRecordMembership(sale_record=sale_record, **data) for data in membership_records
            ])

            # Create records for SaleRecordVouchers
            SaleRecordVouchers.objects.bulk_create([
                SaleRecordVouchers(sale_record=sale_record, **data) for data in vouchers_records
            ])

            # Create records for PurchasedGiftCards
            PurchasedGiftCards.objects.bulk_create([
                PurchasedGiftCards(sale_record=sale_record, **data) for data in gift_cards_records
            ])

            # Create records for SaleTax
            SaleTax.objects.bulk_create([
                SaleTax(sale_order=sale_record, **data) for data in tax_records
            ])

            # Create records for SaleRecordTip
            SaleRecordTip.objects.bulk_create([
                SaleRecordTip(sale_record=sale_record, **data) for data in tip_records
            ])

            # ============================================================= Redeemed Items records ===================================================================
            '''
            Redeemed Items records are being created here (if any)
            '''

            # Create records for SaleRecordAppliedCoupons
            SaleRecordAppliedCoupons.objects.bulk_create([
                SaleRecordAppliedCoupons(sale_record=sale_record, **data) for data in applied_coupons_records
            ])

            # Create records for AppliedVouchers
            AppliedVouchers.objects.bulk_create([
                AppliedVouchers(sale_record=sale_record, **data) for data in applied_vouchers_records
            ])

            # Create records for AppliedMemberships
            AppliedMemberships.objects.bulk_create([
                AppliedMemberships(sale_record=sale_record, **data) for data in applied_memberships_records
            ])

            # Create records for AppliedGiftCards
            AppliedGiftCards.objects.bulk_create([
                AppliedGiftCards(sale_record=sale_record, **data) for data in applied_gift_cards_records
            ])

        return sale_record