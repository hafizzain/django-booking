from rest_framework import serializers
from threading import Thread
from django.db import transaction
from django.db.models import F, Q, Case, When, Value, FloatField, IntegerField, ExpressionWrapper
from django.core.exceptions import ValidationError

from Business.models import StockNotificationSetting
from Sale.Constants.stock_lowest import stock_lowest
from Sale.Constants.tunrover import ProductTurnover
from Invoices.models import SaleInvoice
from Product.models import ProductStock, ProductOrderStockReport
from Client.serializers import SaleInvoiceSerializer

from SaleRecords.models import *
from Invoices.models import SaleInvoice
from Client.helpers import calculate_validity
from Employee.models import *
from TragetControl.models import *


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'full_name']


class SaleRecordsAppointmentServicesSerializer(serializers.ModelSerializer):
    service_names = serializers.SerializerMethodField(read_only=True)
    client_data = serializers.SerializerMethodField(read_only=True)

    def get_client_data(self, obj):
        try:
            if obj.client:
                client = Client.objects.get(id=obj.client.id)
                return ClientSerializer(client).data
            return None
        except Exception as e:
            raise ValidationError(
                f'Error Occured while getting the client data appointment services {str(e)}')
            
    def get_service_names(self, obj):
        try:
            from Invoices.models import InvoiceTranslation

            secondary_invoice_traslation = InvoiceTranslation.objects.filter(
                id=obj.sale_record.location.secondary_translation.id).first()
            translation = obj.service.servicetranlations_set.filter(
                language__id=secondary_invoice_traslation.language.id).first()
            if translation:
                return {
                    'name': f"{obj.service.name}",
                    'arabic_name': f"{obj.service.arabic_name}",
                    'secondary_name': f"{translation.service_name}"
                }
            else:
                return None
        except Exception as e:
            raise ValidationError(
                f'Error Occured while getting the service names appointment services {str(e)}')

    class Meta:
        model = SaleRecordsAppointmentServices
        fields = "__all__"
        read_only_fields = ['sale_record', 'service_names']


class SaleRecordProductsSerializer(serializers.ModelSerializer):
    product_names = serializers.SerializerMethodField(read_only=True)

    def get_product_names(self, obj):
        try:
            from Invoices.models import InvoiceTranslation
            try:
                secondary_invoice_traslation = InvoiceTranslation.objects.filter(
                    id=obj.sale_record.location.secondary_translation.id).first()
                translation = obj.product.producttranslations_set.filter(
                    language__id=secondary_invoice_traslation.language.id).first()
            except : 
                translation=None
            if translation:
                return {
                    'name': f"{obj.product.name}"if obj.product.name else None,
                    'arabic_name': f"{obj.product.arabic_name}"if obj.product.arabic_name else None,
                    'secondary_name': f"{translation.product_name}"if translation.product_name else None,
                }
            else:
                return {
                    'name': f"{obj.product.name}"if obj.product.name else None,
                    'arabic_name': f"{obj.product.arabic_name}"if obj.product.arabic_name else None, 
                }
        except Exception as e:
            raise ValidationError(
                f'Error Occured while getting the product names {str(e)}')

    class Meta:
        model = SaleRecordsProducts
        fields = "__all__"
        read_only_fields = ['sale_record', 'product_names']


class SaleRecordServicesSerializer(serializers.ModelSerializer):
    from Invoices.templatetags import custom_tags

    service_names = serializers.SerializerMethodField(read_only=True)
    # secondary_name = serializers.SerializerMethodField(read_only = True)

    def get_service_names(self, obj):
        try:
            from Invoices.models import InvoiceTranslation

            secondary_invoice_traslation = InvoiceTranslation.objects.filter(
                id=obj.sale_record.location.secondary_translation.id).first()
            translation = obj.service.servicetranlations_set.filter(
                language__id=secondary_invoice_traslation.language.id).first()
            if translation:
                return {
                    'name': f"{obj.service.name}"if obj.service.name else None,
                    'arabic_name': f"{obj.service.arabic_name}"if obj.service.arabic_name else None,
                    'secondary_name': f"{translation.service_name}"if translation.service_name else None,
                }
            else:
                return {
                    'name': f"{obj.service.name}"if obj.service.name else None,
                    'arabic_name': f"{obj.service.arabic_name}"if obj.service.arabic_name else None,
                    'secondary_name': f""
                }
        except Exception as e:
            raise ValidationError(
                f'Error Occured while getting the service names {str(e)}')

    class Meta:
        model = SaleRecordServices
        fields = "__all__"
        read_only_fields = ['sale_record', 'service_names']


class SaleRecordVouchersSerializer(serializers.ModelSerializer):
    valid_till = serializers.CharField(write_only=True, required=True)
    voucher_names = serializers.SerializerMethodField(read_only=True)

    def get_voucher_names(self, obj):
        try:
            return {
                'name': f"{obj.voucher.name}",
                'arabic_name': f"{obj.voucher.arabic_name}",
            }
        except Exception as e:
            raise ValidationError(
                f'Error Occured while getting the voucher names {str(e)}')

    class Meta:
        model = SaleRecordVouchers
        fields = '__all__'
        read_only_fields = ['sale_record', 'voucher_names']


class PurchasedGiftCardsSerializer(serializers.ModelSerializer):
    gift_card_detail = serializers.SerializerMethodField(read_only=True)
    valid_till = serializers.CharField(write_only=True, required=True)

    def get_gift_card_detail(self, obj):
        try:
            if obj.gift_card:

                return {'title': f"{obj.gift_card.title}",
                        'code': f"{obj.gift_card.code}",
                        'spend_amount': f"{obj.spend_amount}",
                        'price': f"{obj.price}",
                        }
        except Exception as e:
            raise ValidationError(
                f'Error Occured while getting the gift card detail {str(e)}')
    class Meta:
        model = PurchasedGiftCards
        fields = "__all__"
        read_only_fields = ['sale_record', 'gift_card_detail']


class SaleRecordMembershipSerializer(serializers.ModelSerializer):
    valid_till = serializers.CharField(write_only=True, required=True)
    membership_names = serializers.SerializerMethodField(read_only=True)

    def get_membership_names(self, obj):
        try:
            return {
                'name': f"{obj.membership.name}",
                'arabic_name': f"{obj.membership.arabic_name}",
            }
        except Exception as e:
            raise ValidationError(
                f'Error Occured while getting the membership names {str(e)}')
    class Meta:
        model = SaleRecordMembership
        fields = "__all__"
        read_only_fields = ['sale_record', 'membership_names']


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
    client_data = serializers.SerializerMethodField(read_only=True)

    def get_client_data(self, obj):
        try:
            if obj.client:
                client = Client.objects.get(id=obj.client.id)
                return ClientSerializer(client).data
            return None
        except Exception as e:
            raise ValidationError(
                f'Error Occured while getting the client data coupons {str(e)}')

    class Meta:
        model = SaleRecordAppliedCoupons
        fields = "__all__"
        read_only_fields = ['sale_record']


class AppliedMembershipsSerializer(serializers.ModelSerializer):
    client_data = serializers.SerializerMethodField(read_only=True)

    def get_client_data(self, obj):
        try:
            if obj.client:
                client = Client.objects.get(id=obj.client.id)
                return ClientSerializer(client).data
            return None
        except Exception as e:
            raise ValidationError(
                f'Error Occured while getting the client data memberships {str(e)}')

    class Meta:
        model = AppliedMemberships
        fields = "__all__"
        read_only_fields = ['sale_record']


class AppliedVouchersSerializer(serializers.ModelSerializer):
    client_data = serializers.SerializerMethodField(read_only=True)

    def get_client_data(self, obj):
        try:
            if obj.client:
                client = Client.objects.get(id=obj.client.id)
                return ClientSerializer(client).data
            return None
        except Exception as e:
            raise ValidationError(
                f'Error Occured while getting the client data vouchers {str(e)}')
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
        read_only_fields = ['sale_record']


class RedeemedLoyaltyPointsSerializer(serializers.ModelSerializer):
    client_data = serializers.SerializerMethodField(read_only=True)

    def get_client_data(self, obj):
        try:
            if obj.client:
                client = Client.objects.get(id=obj.client.id)
                return ClientSerializer(client).data
            return None
        except Exception as e:
            raise ValidationError(
                f'Error Occured while getting the client data lolity points {str(e)}')

    class Meta:
        model = RedeemedLoyaltyPoints
        fields = "__all__"
        read_only_fields = ['sale_record']
        # read_only_fields = ['sale_record']


class SaleRecordSerializer(serializers.ModelSerializer):

    appointment_services = SaleRecordsAppointmentServicesSerializer(many=True)
    services_records = SaleRecordServicesSerializer(many=True)
    products_records = SaleRecordProductsSerializer(many=True)
    payment_methods_records = PaymentMethodsSerializer(many=True)
    gift_cards_records = PurchasedGiftCardsSerializer(many=True)
    membership_records = SaleRecordMembershipSerializer(many=True)
    vouchers_records = SaleRecordVouchersSerializer(many=True)
    tax_records = SaleTaxSerializer(many=True)
    tip_records = SaleOrderTipSerializer(many=True)

    # ================================================================   Applied Items  ==========================================
    applied_coupons_records = SaleRecordAppliedCouponsSerializer(many=True)
    applied_memberships_records = AppliedMembershipsSerializer(many=True)
    applied_vouchers_records = AppliedVouchersSerializer(many=True)
    applied_gift_cards_records = AppliedGiftCardsSerializer(many=True)
    applied_promotions_records = AppliedPromotionSerializer(many=True)
    applied_loyalty_points_records = RedeemedLoyaltyPointsSerializer(many=True)

    invoice = serializers.SerializerMethodField(read_only=True)

    client_data = serializers.SerializerMethodField(read_only=True)

    def get_invoice(self, obj):
        try:
            invoice = SaleInvoice.objects.get(checkout=obj.id)
            if invoice:
                return SaleInvoiceSerializer(invoice, context=self.context).data
            return None
        except Exception as e:
            raise ValidationError(
                f'Error Occured while getting the invoice in the serializer {str(e)}')

    def get_client_data(self, obj):
        try:
            if obj.client:
                client = Client.objects.get(id=obj.client.id)
                return ClientSerializer(client).data
            return None
        except Exception as e:
            raise ValidationError(
                f'Error Occured while getting the client data in the serializer {str(e)}')

    def validate(self, data):
        # Validate that there is at least one record in appointment_services, services_records, and products_records

        if not data.get('appointment_services') and not data.get('services_records') and not data.get('products_records') and not data.get('gift_cards_records') and not data.get('vouchers_records') and not data.get('membership_records'):
            raise serializers.ValidationError(
                "At least one record is required in appointment_services, services_records, products_records, vouchers_records, membership_records or gift_cards_records")

        return data

    class Meta:
        model = SaleRecords
        fields = "__all__"
        # exclude = ['is_active','is_blocked','is_deleted']
        read_only_fields = ['invoice']

        # exclude = ['updated_at','is_deleted','is_blocked','is_active']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.data.get('user')
        tenant = request.tenant
        # raise ValidationError(f'user: {user}')
        location_id = request.data.get('location')
        client = request.data.get('client', None)
        sub_total = request.data.get('sub_total')  # Without tax amount
        # raise ValidationError(f'client_id':str(client))
        # raise ValidationError(f"client = {client} location = {location_id} and user= {user}")

        appointment_services = validated_data.pop('appointment_services', [])
        services_records = validated_data.pop('services_records', [])
        products_records = validated_data.pop('products_records', [])
        payment_methods_records = validated_data.pop(
            'payment_methods_records', [])
        gift_cards_records = validated_data.pop('gift_cards_records', [])
        membership_records = validated_data.pop('membership_records', [])
        vouchers_records = validated_data.pop('vouchers_records', [])
        tax_records = validated_data.pop('tax_records', [])
        tip_records = validated_data.pop('tip_records', [])

        applied_coupons_records = validated_data.pop(
            'applied_coupons_records', [])
        applied_vouchers_records = validated_data.pop(
            'applied_vouchers_records', [])
        applied_memberships_records = validated_data.pop(
            'applied_memberships_records', [])
        applied_gift_cards_records = validated_data.pop(
            'applied_gift_cards_records', [])
        applied_promotions_records = validated_data.pop(
            'applied_promotions_records', [])
        applied_loyalty_points_records = validated_data.pop(
            'applied_loyalty_points_records', [])
        # raise ValidationError(f'{applied_loyalty_points_records}')

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
            appointment_ids = [
                f"{ids['appointment']}" for ids in appointment_services]
            Appointment.objects.filter(
                id__in=appointment_ids).update(status='Done')

            # Create records for SaleRecordServices
            SaleRecordServices.objects.bulk_create([
                SaleRecordServices(sale_record=sale_record, **data) for data in services_records
            ])

            # Create records for SaleRecordsProducts
            SaleRecordsProducts.objects.bulk_create([
                SaleRecordsProducts(sale_record=sale_record, **data) for data in products_records
            ])
            self.product_stock_update(
                location_id, products_records, user, tenant)

            # Create records for PaymentMethods
            PaymentMethods.objects.bulk_create([
                PaymentMethods(sale_record=sale_record, **data) for data in payment_methods_records
            ])

            # Create records for SaleRecordMembership
            SaleRecordMembership.objects.bulk_create([
                SaleRecordMembership(
                    sale_record=sale_record,
                    membership=data['membership'],
                    price=float(data['price'] * data['quantity']),
                    quantity=data['quantity'],
                    expiry=calculate_validity(data['valid_till']),
                ) for data in membership_records
            ])

            # Create records for SaleRecordVouchers
            SaleRecordVouchers.objects.bulk_create([
                SaleRecordVouchers(
                    sale_record=sale_record,
                    voucher=data['voucher'],
                    price=float(data['price'] * data['quantity']),
                    quantity=data['quantity'],
                    expiry=calculate_validity(data['valid_till']),
                ) for data in vouchers_records
            ])

            # Create records for PurchasedGiftCards
            PurchasedGiftCards.objects.bulk_create([
                PurchasedGiftCards(
                    sale_record=sale_record,
                    gift_card=data['gift_card'],
                    price=float(data['price'] * data['quantity']),
                    spend_amount=data['spend_amount'],
                    sale_code=data['sale_code'],
                    quantity=data['quantity'],
                    expiry=calculate_validity(data['valid_till']),
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
            self.gift_card_record_update(
                location_id, applied_gift_cards_records)

            AppliedPromotion.objects.bulk_create([
                AppliedPromotion(sale_record=sale_record, **data) for data in applied_promotions_records
            ])

            RedeemedLoyaltyPoints.objects.bulk_create([
                RedeemedLoyaltyPoints(sale_record=sale_record, **data) for data in applied_loyalty_points_records
            ])

            self.employee_commission_calculation(
                location_id, user, sub_total, sale_record, products_records, vouchers_records, services_records)

        return sale_record

    # Class Methods

    def product_stock_update(self, location=None, products=None, user=None, tenant=None):

        if location and products and user:

            with transaction.atomic():
                try:
                    for data in products:
                        ProductStock.objects.filter(location=f'{location}', product_id=data.get('product')).update(

                            location_id=f'{location}',
                            product=data.get('product'),
                            sold_quantity=ExpressionWrapper(
                                F('sold_quantity') + data.get('quantity'), output_field=IntegerField()),
                            available_quantity=ExpressionWrapper(
                                F('available_quantity') - data.get('quantity'), output_field=IntegerField()),
                            consumed_quantity=ExpressionWrapper(
                                F('consumed_quantity') + data.get('quantity'), output_field=IntegerField())
                        )
                        product = ProductStock.objects.get(
                            location_id=f'{location}', product=data.get('product'))

                        ProductOrderStockReport.objects.create(
                            report_choice='Sold',
                            product=data.get('product'),
                            user_id=user,
                            location_id=f'{location}',

                            before_quantity=product.available_quantity,
                            after_quantity=product.available_quantity -
                            data.get('quantity')
                        )
                        location = BusinessAddress.objects.get(
                            id=f'{location}')
                        try:

                            admin_email = StockNotificationSetting.objects.get(
                                business=str(location.business))
                            if admin_email.notify_stock_turnover == True and product.available_quantity <= 5:
                                try:
                                    thrd = Thread(target=ProductTurnover, args=[],
                                                  kwargs={'product': product, 'product_stock': product,
                                                          'business_address': location.id, 'tenant': tenant})
                                    thrd.start()
                                except Exception as e:
                                    raise ValidationError(f'{str(e)}')
                        except:
                            pass

                        try:
                            admin_email = StockNotificationSetting.objects.get(
                                business=str(location.business))
                            if admin_email.notify_for_lowest_stock == True and product.available_quantity <= 5:
                                try:
                                    thrd = Thread(target=stock_lowest, args=[],
                                                  kwargs={'product': product, 'product_stock': product,
                                                          'business_address': location.id, 'tenant': tenant,
                                                          'quantity': product.available_quantity})
                                    thrd.start()
                                except Exception as err:
                                    raise ValidationError(f'{str(e)}')
                        except:
                            pass

                except Exception as e:
                    raise ValidationError(f"error in product stock': {str(e)}")
        else:
            pass

    def gift_card_record_update(self, location=None, gift_cards=None):
        update_query = None
        if location and gift_cards:
            try:
                for data in gift_cards:

                    update_query = PurchasedGiftCards.objects.filter(
                        sale_record__location=location,
                        id=data['purchased_gift_card_id'].id,
                        # Ensure spend_amount is greater than or equal to partial_price
                        spend_amount__gte=data['partial_price']
                    ).update(spend_amount=Case(
                        When(
                            spend_amount__gte=data['partial_price'],
                            then=ExpressionWrapper(
                                F('spend_amount') - data['partial_price'], output_field=FloatField())
                        ),
                        # Keep the original value if spend_amount < partial_price
                        default=F('spend_amount'),
                        output_field=FloatField()
                    )
                    )
            except Exception as e:
                raise ValidationError(str(e))
            # Check if any records were updated
            if update_query is None or update_query == 0:
                raise ValidationError(
                    "Cannot update spend_amount to be less than partial_price.")
        else:
            pass

    def employee_commission_calculation(self, location=None, user=None,  sub_total=None, checkout_id=None, products_list=None, vouchers_list=None, service_list=None):
        try:
            if products_list:
                for item in products_list:
                    sale_commission = CategoryCommission.objects.filter(
                        commission__employee=item.get('employee'),
                        from_value__lte=float(item.get('price')),
                        category_comission__iexact='Retail'
                    ).order_by('-from_value').first()
                    # if sale_commission:
                    #     raise ValidationError('Commission found')
                    # raise ValidationError('Not found')

                    # raise ValidationError(f'{str(product_id)}')
                    product = Product.objects.get(id=f'{item.get("product")}')

                    if sale_commission:
                        calculated_commission = sale_commission.calculated_commission(
                            item.get('price'))
                        EmployeeCommission.objects.create(

                            user_id=user,
                            business=checkout_id.location.business,
                            location_id=location,
                            employee=item.get('employee'),
                            commission=sale_commission.commission,
                            category_commission=sale_commission,
                            commission_category=sale_commission.category_comission,
                            commission_type=sale_commission.comission_choice,
                            sale_value=float(item.get('price')),
                            commission_rate=float(
                                sale_commission.commission_percentage),
                            commission_amount=float(calculated_commission),
                            symbol=sale_commission.symbol,
                            sale_id=checkout_id.id,

                            item_name=product.name,
                            item_id=item.get('product'),
                            quantity=item.get('quantity'),
                            tip=0
                        )

            if vouchers_list:
                for item in vouchers_list:
                    sale_commission = CategoryCommission.objects.filter(
                        commission__employee=item.get('employee'),
                        from_value__lte=float(item.get("price")),
                        category_comission__iexact='Voucher'
                    ).order_by('-from_value').first()
                    voucher = Vouchers.objects.get(id=f'{item.get("voucher")}')
                    if sale_commission:
                        calculated_commission = sale_commission.calculated_commission(
                            item.get('price'))
                        EmployeeCommission.objects.create(
                            user_id=user,
                            business=checkout_id.location.business,
                            location_id=location,
                            employee=item.get('employee'),
                            commission=sale_commission.commission,
                            category_commission=sale_commission,
                            commission_category=sale_commission.category_comission,
                            commission_type=sale_commission.comission_choice,
                            sale_value=float(item.get('price')),
                            commission_rate=float(
                                sale_commission.commission_percentage),
                            commission_amount=float(calculated_commission),
                            symbol=sale_commission.symbol,
                            sale_id=checkout_id.id,

                            item_name=voucher.name,
                            item_id=item.get('voucher'),
                            quantity=item.get('quantity'),

                            tip=0
                        )

            if service_list:
                for item in service_list:
                    sale_commission = CategoryCommission.objects.filter(
                        commission__employee=item.get('employee'),
                        from_value__lte=float(item.get("price")),
                        category_comission__iexact='Service'
                    ).order_by('-from_value').first()
                    service = Service.objects.get(id=f'{item.get("service")}')
                    if sale_commission:
                        calculated_commission = sale_commission.calculated_commission(
                            item.get('price'))
                        EmployeeCommission.objects.create(

                            user_id=user,
                            business=checkout_id.location.business,
                            location_id=location,
                            employee=item.get('employee'),
                            commission=sale_commission.commission,
                            category_commission=sale_commission,
                            commission_category=sale_commission.category_comission,
                            commission_type=sale_commission.comission_choice,
                            sale_value=float(item.get('price')),
                            commission_rate=float(
                                sale_commission.commission_percentage),
                            commission_amount=float(calculated_commission),
                            symbol=sale_commission.symbol,
                            sale_id=checkout_id.id,

                            item_name=service.name,
                            item_id=item.get('service'),
                            quantity=item.get('quantity'),
                            tip=0
                        )

        except Exception as e:
            raise ValidationError(
                f'Error occured in Employee Commission Calculations {str(e)}')
