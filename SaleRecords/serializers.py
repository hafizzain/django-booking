from rest_framework import serializers
from django.db import transaction
from django.db.models import F ,Q

from Invoices.models import SaleInvoice
from Product.models import ProductStock

from SaleRecords.models import *
from Invoices.models import SaleInvoice
from Client.helpers import calculate_validity
from Employee.models import *

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
    valid_till = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = SaleRecordVouchers
        fields = '__all__'
        read_only_fields = ['sale_record']


class PurchasedGiftCardsSerializer(serializers.ModelSerializer):
    gift_card_detail = serializers.SerializerMethodField(read_only = True)
    valid_till = serializers.CharField(write_only=True, required=True)
    
    
    def get_gift_card_detail(self, obj):
        if obj.gift_card:
            

            return {'title': f"{obj.gift_card.title}",
                    'code': f"{obj.gift_card.code}",
                    'spend_amount': f"{obj.spend_amount}",
                    'price': f"{obj.price}",
                    }


    class Meta:
        model = PurchasedGiftCards
        fields = "__all__"
        read_only_fields = ['sale_record','gift_card_detail']
        
        
class SaleRecordMembershipSerializer(serializers.ModelSerializer):
    valid_till = serializers.CharField(write_only=True, required=True)
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

class AppliedPromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppliedPromotion
        fields = "__all__"


class SaleInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleInvoice
        fields = "__all__"
        
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id','full_name']

class SaleRecordSerializer(serializers.ModelSerializer):
    
    appointment_services = SaleRecordsAppointmentServicesSerializer(many= True, write_only = True)
    services_records = SaleRecordServicesSerializer(many= True, write_only = True)
    products_records = SaleRecordProductsSerializer(many= True, write_only = True)
    payment_methods_records = PaymentMethodsSerializer(many = True, write_only = True)
    gift_cards_records = PurchasedGiftCardsSerializer(many = True, write_only = True)
    membership_records = SaleRecordMembershipSerializer(many = True ,write_only = True)
    vouchers_records = SaleRecordVouchersSerializer(many =True , write_only = True)
    tax_records = SaleTaxSerializer(many =True, write_only = True)
    tip_records = SaleOrderTipSerializer(many = True, write_only = True)
    
    # ================================================================   Applied Items  ==========================================
    applied_coupons_records = SaleRecordAppliedCouponsSerializer(many = True, write_only = True)
    applied_memberships_records = AppliedMembershipsSerializer(many = True, write_only = True)
    applied_vouchers_records = AppliedVouchersSerializer(many = True, write_only = True)
    applied_gift_cards_records = AppliedGiftCardsSerializer(many = True, write_only = True)
    applied_promotions_records = AppliedPromotionSerializer(many = True, write_only = True)
    
    invoice = serializers.SerializerMethodField(read_only = True)
    
    client_data = serializers.SerializerMethodField(read_only = True)
    
    def get_invoice(self, obj):
        invoice = SaleInvoice.objects.get(checkout = obj.id)
        return SaleInvoiceSerializer(invoice).data
    
    def get_client_data(self, obj):
        if obj.client:
            client = Client.objects.get(id = obj.client.id)
            return ClientSerializer(client).data
        return None
    
    def product_stock_update(self, location, products):
        for data in products:
            ProductStock.objects.filter(location = location, product = data['product']).update(
                sold_quantity =  F('sold_quantity') + data['refunded_quantity'],
                available_quantity=F('available_quantity') - data['quantity'],
                consumed_quantity = F('consumed_quantity') + data['quantity']
                
            )
            
    
    def validate(self, data):
        # Validate that there is at least one record in appointment_services, services_records, and products_records

        if not data.get('appointment_services') and not data.get('services_records') and not data.get('products_records') and not data.get('gift_cards_records') and not data.get('vouchers_records') and not data.get('membership_records'):
            raise serializers.ValidationError("At least one record is required in appointment_services, services_records, products_records, vouchers_records, membership_records or gift_cards_records")

        return data
        
        
        
    class Meta:
        model = SaleRecords
        fields = "__all__"
        # exclude = ['is_active','is_blocked','is_deleted']
        read_only_fields = ['invoice']
        
        # exclude = ['updated_at','is_deleted','is_blocked','is_active']
    
    def create(self, validated_data):
        request = self.context.get('request')
        location = request.data.get('location')
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
        applied_promotions_records = validated_data.pop('applied_promotions_records',[])
        
        
        
        
        
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
                SaleRecordMembership(
                    sale_record=sale_record, 
                    membership = data['membership'],
                    price = float(data['price'] * data['quantity']),
                    quantity = data['quantity'],
                    expiry = calculate_validity(data['valid_till']),
                    ) for data in membership_records
            ])

            # Create records for SaleRecordVouchers
            SaleRecordVouchers.objects.bulk_create([
                SaleRecordVouchers(
                    sale_record=sale_record, 
                    voucher = data['voucher'],
                    price = float(data['price'] * data['quantity']),
                    quantity = data['quantity'],
                    expiry = calculate_validity(data['valid_till']),
                            ) for data in vouchers_records
            ])

            # Create records for PurchasedGiftCards
            PurchasedGiftCards.objects.bulk_create([
                PurchasedGiftCards(
                    sale_record=sale_record,
                    gift_card = data['gift_card'],
                    price = float(data['price'] * data['quantity']),
                    spend_amount = data['spend_amount'],
                    quantity = data['quantity'],
                    expiry = calculate_validity(data['valid_till']),
                            ) for data in gift_cards_records
            ])

            # Create records for SaleTax
            SaleTax.objects.bulk_create([
                SaleTax(sale_record=sale_record, **data) for data in tax_records
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
            
            AppliedPromotion.objects.bulk_create([
                AppliedPromotion(sale_record= sale_record, **data) for data in applied_promotions_records
            ])
            
            

        return sale_record
    