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
    appointments_services = SaleRecordsAppointmentServicesSerializer(many= True)
    services = SaleRecordServicesSerializer(many= True)
    products = SaleRecordProductsSerializer(many= True)
    payment_methods = PaymentMethodsSerializer(many = True)
    gift_card = PurchasedGiftCardsSerilizer(many = True)
    membership = SaleRecordMembershipSerializer(many = True )
    vouchers = SaleRecordVouchersSerializer(many =True )
    tax = SaleTaxSerializer(many =True)
    tips = SaleOrderTipSerializer(many = True)
    
    # ================================================================   Applied Items  ==========================================
    applied_coupons = SaleRecordAppliedCouponsSerializer(many = True)
    applied_memberships = AppliedMembershipsSerializer(many = True)
    applied_vouchers = AppliedVouchersSerializer(many = True)
    applied_gift_cards = AppliedGiftCardsSerializer(many = True)
    
    
    class Meta:
        model = SaleRecords
        fields = '__all__'
        
    def create(self, validated_data):
        
        appointments_services_data = validated_data.pop('appointments_services', [])
        services_data = validated_data.pop('services', [])
        products_data = validated_data.pop('products', [])
        payment_methods_data = validated_data.pop('payment_methods',[])
        membership_data = validated_data.pop('membership', [])
        gift_cards_data = validated_data.pop('gift_card',[])
        vouchers_data = validated_data.pop('vouchers',[])
        tax_data = validated_data.pop('tax', [])
        tips_data = validated_data.pop('tips', [])

        applied_coupons_data = validated_data.pop('applied_coupons', [])
        applied_vouchers_data  = validated_data.pop('applied_vouchers',[])
        applied_memberships_data  = validated_data.pop('applied_memberships',[])
        applied_gift_card_data = validated_data.pop('applied_gift_cards',[])
        
        
        # =================================================== Checkout Records ========================================================
        '''
            Checkout records are being created here
        '''
        sale_record = SaleRecords.objects.create(**validated_data)
        with transaction.atomic():
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
            
            PurchasedGiftCards.objects.bulk_create([ 
                PurchasedGiftCards(sale_record = sale_record , **data) for data in gift_cards_data
            ])
            
            SaleTax.objects.bulk_create([
                SaleTax(sale_order=sale_record, **data) for data in tax_data
            ])
            
            SaleRecordTip.objects.bulk_create([
                SaleRecordTip(sale_record=sale_record, **data) for data in tips_data
            ])
            
            
            # ============================================================= Redeemed Items records ===================================================================
            '''
            Redeemed Items records are being creating here (if any)
            '''
            SaleRecordAppliedCoupons.objects.bulk_create([
                SaleRecordAppliedCoupons(sale_record=sale_record, **data) for data in applied_coupons_data
            ])
            AppliedVouchers.objects.bulk_create([
                AppliedVouchers(sale_record = sale_record, **data) for data in applied_vouchers_data
            ])
            AppliedMemberships.objects.bulk_create([
                AppliedMemberships(sale_record=sale_record, **data) for data in applied_memberships_data
            ])
            AppliedGiftCards.objects.bulk_create([
                AppliedGiftCards(sale_record=sale_record, **data) for data in applied_gift_card_data
            ])

        return sale_record