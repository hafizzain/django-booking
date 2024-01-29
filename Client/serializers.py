# from Appointment.serializers import ClientImagesSerializerResponse
from Business.models import BusinessAddress
from rest_framework import serializers
from Product.Constants.index import tenant_media_base_url, tenant_media_domain
from Order.models import VoucherOrder, MemberShipOrder, Checkout
from SaleRecords.models import SaleRecordMembership
from Order.serializers import CreatedAtCheckoutSerializer
from Product.models import Product
from Service.models import Service
from Utility.models import Country, State, City

from Client.models import Client, ClientGroup, CurrencyPriceMembership, DiscountMembership, LoyaltyPoints, Subscription, \
    Promotion, Rewards, Membership, Vouchers, ClientLoyaltyPoint, LoyaltyPointLogs, VoucherCurrencyPrice, ClientImages, \
    Comments
from Invoices.models import SaleInvoice
from Appointment.models import AppointmentCheckout, AppointmentEmployeeTip, AppointmentService, Appointment
from Order.models import Checkout, Order
from Utility.serializers import StateSerializer, CitySerializer
# from Sale.serializers import SaleOrders_CheckoutSerializer, SaleOrders_AppointmentCheckoutSerializer


class LocationSerializerLoyalty(serializers.ModelSerializer):
    
    class Meta:
        model = BusinessAddress
        fields = ('id', 'address_name')

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'arabic_name')
        # exclude = ['is_deleted', 'created_at', 'slug', 'published'
        #            , 'user', 'business' , 'vendor', 'category' ,'brand' , 'product_type' ,'cost_price' , 'full_price'
        #            , 'sell_price', 'tax_rate', 'short_description' , 'description' , 'barcode_id', ''
        #            ]

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name', 'arabic_name')
        #exclude = ['is_deleted', 'created_at', 'updated_at']

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        exclude = ['is_deleted', 'created_at', 'unique_code', 'key']

class ClientImagesSerializerResponses(serializers.ModelSerializer):
    class Meta:
        model = ClientImages
        fields = "__all__"

class SingleClientSerializer(serializers.ModelSerializer):
    country_obj = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField()
    total_done_appointments = serializers.SerializerMethodField(read_only=True)
    total_sales = serializers.SerializerMethodField(read_only=True)
    country = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField(read_only=True)

    def get_images(self,obj):
        try:
            images = ClientImages.objects.filter(client_id=obj.id)
            aval_images = ClientImagesSerializerResponses(images,many=True , context={'request':self.context.get('request')}).data
            return aval_images
        except Exception as ex:
            return [str(ex)]

    def get_country(self, obj):
        return CountrySerializer(obj.country).data if obj.country else None
    
    def get_state(self, obj):
        return StateSerializer(obj.state).data if obj.state else None
    

    def get_city(self, obj):
        return CitySerializer(obj.city).data if obj.city else None


    def get_total_done_appointments(self, obj):
        return AppointmentService.objects.filter(
            appointment_status__in = ['Done', 'Paid'],
            appointment__client = obj
        ).count()
    
    def get_total_sales(self, obj):
        total_price = 0
        appointments = AppointmentService.objects.filter(
            appointment_status__in = ['Done', 'Paid'],
            appointment__client = obj
        )
        for price in appointments:
            total_price += float(price.price or price.total_price or 0)

        checkout_orders_total = Checkout.objects.filter(
            is_deleted = False, 
            client = obj,
        )   
        total_orders = Order.objects.filter(
            checkout__id__in = list(checkout_orders_total.values_list('id', flat=True))
        )

        for order in total_orders:
            realPrice = order.price or order.total_price
            total_price += float(order.quantity) * float(realPrice)
    
        return total_price
    
    def get_country_obj(self, obj):
        try:
            return CountrySerializer(obj.country).data
        except Exception as err:
            return None
    
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return f'{obj.image}'
        return None
    
    class Meta:
        model = Client
        fields =['id','full_name','image','client_id','email','mobile_number','dob','postal_code','address','gender','card_number',
                 'country','city','state', 'is_active','images',
                 'language', 'about_us', 'marketing','country_obj','customer_note',
                 'created_at', 'total_done_appointments', 'total_sales']
        
class CreatedAtAppointmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Appointment
        fields = ['created_at']


class ClientDropdownSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()
    total_visit = serializers.IntegerField(read_only=True)
    images = serializers.SerializerMethodField(read_only=True)

    client_info = serializers.SerializerMethodField(read_only=True)

    def get_client_info(self, obj):
        client_info_data = {
            'client_type': obj.client_type,
            'client_tag': obj.client_tag,
        }
        return ClientInfoSerializer(client_info_data).data
    
    def get_images(self, obj):
        try:
            images = ClientImages.objects.filter(client_id=obj.id)
            aval_images = ClientImagesSerializerResponses(images, many=True,
                                                          context={'request': self.context.get('request')}).data
            return aval_images
        except Exception as ex:
            return [str(ex)]

    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return f'{obj.image}'
        return None

    class Meta:
        model  = Client
        fields = ['id','images', 'full_name', 'email', 'client_id', 'image', 'total_visit', 'client_info']

class ClientInfoSerializer(serializers.Serializer):
    client_type = serializers.CharField()
    client_tag = serializers.CharField()
    
class ClientSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    last_transaction_date = serializers.DateTimeField(read_only=True)

    last_appointment = serializers.SerializerMethodField(read_only=True)
    last_sale = serializers.SerializerMethodField(read_only=True)

    country_obj = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField()
    total_done_appointments = serializers.SerializerMethodField(read_only=True)
    total_sales = serializers.SerializerMethodField(read_only=True)
    
    client_info = serializers.SerializerMethodField(read_only=True)

    def get_client_info(self, obj):
        client_info_data = {
            'client_type': obj.client_type,
            'client_tag': obj.client_tag,
        }
        return ClientInfoSerializer(client_info_data).data

    def get_last_sale(self, obj):
        last_sale = Checkout.objects.filter(client=obj).order_by('-created_at')
        if len(last_sale) > 0:
            return CreatedAtCheckoutSerializer(last_sale[0]).data
        return None

    def get_last_appointment(self, obj):
        last_appointment = Appointment.objects.filter(client=obj).order_by('-created_at')
        if len(last_appointment) > 0:
            return CreatedAtAppointmentSerializer(last_appointment[0]).data
        return None


    def get_total_done_appointments(self, obj):
        return AppointmentService.objects.filter(
            appointment_status__in = ['Done', 'Paid'],
            appointment__client = obj
        ).count()
    
    def get_total_sales(self, obj):
        total_price = 0
        appointments = AppointmentService.objects.filter(
            appointment_status__in = ['Done', 'Paid'],
            appointment__client = obj
        )
        for price in appointments:
            total_price += float(price.price or price.total_price or 0)

        checkout_orders_total = Checkout.objects.filter(
            is_deleted = False, 
            client = obj,
        )   
        total_orders = Order.objects.filter(
            checkout__id__in = list(checkout_orders_total.values_list('id', flat=True))
        )

        for order in total_orders:
            realPrice = order.price or order.total_price
            total_price += float(order.quantity) * float(realPrice)
    
        return total_price
    
    def get_country_obj(self, obj):
        try:
            return CountrySerializer(obj.country).data
        except Exception as err:
            return None
    
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return f'{obj.image}'
        return None
    
    class Meta:
        model = Client
        fields =['id','full_name','image','client_id','email','mobile_number','dob','postal_code','address','gender','card_number',
                'country','city','state', 'is_active', 'language', 'about_us', 'marketing','country_obj','customer_note',
                'created_at', 'total_done_appointments', 'total_sales', 'last_appointment', 'last_sale', 'last_transaction_date','client_info']
        
class ClientSerializerOP(serializers.ModelSerializer):
    
    image = serializers.SerializerMethodField()


    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return f'{obj.image}'
        return None

    class Meta:
        model = Client
        fields = ['id', 'is_active', 'full_name', 'email', 'client_id', 'mobile_number', 'image']
        
class Client_TenantSerializer(serializers.ModelSerializer):
    country_obj = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField()
    
    
    def get_country_obj(self, obj):
        try:
            return CountrySerializer(obj.country).data
        except Exception as err:
            return None
    
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["tenant"]
                url = tenant_media_domain(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return None
    
    class Meta:
        model = Client
        fields =['id','full_name','image','client_id','email','mobile_number','dob','postal_code','address','gender','card_number',
                 'country','city','state', 'is_active',
                 'language', 'about_us', 'marketing','country_obj','customer_note',
                 'created_at']
        
        
class ClientGroupSerializer(serializers.ModelSerializer):
    client = ClientSerializerOP(read_only=True, many=True)
    
    class Meta:
        model = ClientGroup
        fields = ['id','name','is_active','email','created_at','client']
    
class SubscriptionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Subscription
        fields =['id','name','price' ,'days','select_amount', 'subscription_type','is_active']
     
     
class RewardSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    service = ServiceSerializer()
    
    class Meta:
        model = Rewards
        fields =['id','name', 'reward_value','reward_point','reward_type' ,'discount', 'total_points' ,'product' , 'service' ]
        
class PromotionSerializer(serializers.ModelSerializer):
    
    product = ProductSerializer()
    service = ServiceSerializer()
    
    class Meta:
        model = Promotion
        fields = ['id', 'name','purchases' , 'promotion_type', 'product', 'service','discount','valid_til']

class DiscountMembershipSerializers(serializers.ModelSerializer):
    service_name = serializers.SerializerMethodField(read_only=True)
    product_name = serializers.SerializerMethodField(read_only=True)
    
    def get_product_name(self, obj):
        try:
            return obj.product.name
        except:
            return None
    def get_service_name(self, obj):
        try:
            return obj.service.name
        except:
            return None
    class Meta:
        model = DiscountMembership
        fields = '__all__'
class CurrencyPriceMembershipSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = CurrencyPriceMembership
        fields = '__all__'
        

class CurrencyPriceVoucherSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = VoucherCurrencyPrice
        fields = '__all__'


class MembershipSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    currency_membership = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField(read_only=True)
    
    def get_products(self, obj):
        try:
            pro = DiscountMembership.objects.filter(membership = obj, service__isnull = True)
            return DiscountMembershipSerializers(pro, many= True).data
        except Exception as err:
            print(err)
            
    def get_services(self, obj):
        try:
            pro = DiscountMembership.objects.filter(membership = obj,  product__isnull = True)
            return DiscountMembershipSerializers(pro, many= True).data
        except Exception as err:
            print(err)
    
    
    def get_currency_membership(self, obj):
        location_id = self.context.get('location_id', None)
        query = {}
        if location_id:
            try:
                location = BusinessAddress.objects.get(id = location_id)
            except:
                pass
            else:
                query['currency'] = location.currency
        try:
            pro = CurrencyPriceMembership.objects.filter(
                membership = obj,
                **query,
            ).distinct()
            return CurrencyPriceMembershipSerializers(pro, many= True).data
        except Exception as err:
            print(err)

    def get_is_expired(self, obj):
        return obj.is_expired()
            
    class Meta:
        model = Membership
        fields = ['id', 'name', 'arabic_name', 'is_expired', 'valid_for','discount','description', 
                  'term_condition','products', 'services', 'currency_membership']
        read_only_fields = ['arabic_name', 'is_expired']

class VoucherSerializer(serializers.ModelSerializer):
    # currency_voucher_prices = serializers.SerializerMethodField(read_only=True)
    currency_voucher = serializers.SerializerMethodField()
    voucher_count = serializers.SerializerMethodField()

    def get_currency_voucher(self, obj):
        try:
            cvp = VoucherCurrencyPrice.objects.filter(voucher = obj).distinct()
            return CurrencyPriceVoucherSerializers(cvp, many= True).data
        except Exception as err:
            print(err)

    def get_voucher_count(self, obj):
        count = VoucherOrder.objects.filter(voucher=obj).count()
        return count

    class Meta:
        model = Vouchers
        fields = ['id', 'name', 'arabic_name', 'user','business','voucher_type',
                'validity','sales','is_deleted','is_active','created_at','currency_voucher','discount_percentage', 'voucher_count']
        read_only_fields = ['arabic_name']


class ClientAppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ['id', 'full_name', 'image']
        
class LoyaltyPointsSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)
    
    def get_location(self, obj):
        try:
            loc = BusinessAddress.objects.get(id = obj.location.id)
            return LocationSerializerLoyalty(loc).data
        except Exception as err:
            print(err)
    class Meta:
        model = LoyaltyPoints
        fields = ['id', 'user', 'business','location','name','amount_spend','number_points','earn_points','total_earn_from_points','is_active','is_deleted','is_blocked','created_at']
        

class ClientLoyaltyPointSerializer(serializers.ModelSerializer):
    # location = serializers.SerializerMethodField(read_only=True)
    total_available_points = serializers.SerializerMethodField(read_only=True)

    def get_total_available_points(self, obj):
        return obj.total_available_points
    
    # def get_location(self, obj):
    #     try:
    #         loc = BusinessAddress.objects.get(id = obj.location.id)
    #         return LocationSerializerLoyalty(loc).data
    #     except Exception as err:
    #         print(err)
    class Meta:
        model = ClientLoyaltyPoint
        fields = '__all__'
    
class ClientVouchersSerializer(serializers.ModelSerializer):
    voucher = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    order_type  = serializers.SerializerMethodField(read_only=True)
    client = serializers.SerializerMethodField(read_only=True)
    name  = serializers.SerializerMethodField(read_only=True)
    voucher_price  = serializers.SerializerMethodField(read_only=True)
        
    def get_order_type(self, obj):
        return 'Voucher'
    
    def get_voucher_price(self, obj):
        return obj.current_price
    
    employee = serializers.SerializerMethodField()
    

    def get_employee(self, voucher_order):
        if voucher_order.member:
            return {
                'full_name' : str(voucher_order.member.full_name),
            }
        return ''

    def get_location(self, obj):
        try:
            loc = BusinessAddress.objects.get(id = obj.location.id)
            return LocationSerializerLoyalty(loc).data
        except Exception as err:
            print(err)

    def get_client(self, obj):
        try:
            serializers = ClientSerializer(obj.client).data
            return serializers
        except Exception as err:
            return None
    
    def get_voucher(self, obj):
        if obj.voucher:
            return {
                'voucher_type' : obj.voucher.voucher_type,
                'name' : obj.voucher.name,
                'sales': obj.voucher.sales,
                'start_date' : f'{obj.start_date}',
                'end_date' : f'{obj.end_date}',
            }
        
        return {}
    
    def get_name(self, obj):
        try:
            return obj.voucher.name
        except Exception as err:
            return None

    class Meta:
        model = VoucherOrder
        fields = ['id', 'voucher', 'client' , 'location' , 
                  'status','quantity', 'checkout','employee','start_date', 'end_date',
                  'total_price', 'payment_type' , 'order_type','price',
                  'name','created_at','discount_percentage', 'voucher_price', 'max_sales']

class ClientMembershipsSerializer(serializers.ModelSerializer):
    # membership = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    order_type  = serializers.SerializerMethodField(read_only=True)
    client = serializers.SerializerMethodField(read_only=True)
    name  = serializers.SerializerMethodField(read_only=True)
    membership_price  = serializers.SerializerMethodField(read_only=True)
    discount_type = serializers.SerializerMethodField(read_only=True)
    products = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()

    def get_products(self, obj):
        try:
            pro = DiscountMembership.objects.filter(membership=obj.membership, service__isnull=True)
            return DiscountMembershipSerializers(pro, many=True).data
        except Exception as err:
            return str(err)
            
    def get_services(self, obj):
        try:
            pro = DiscountMembership.objects.filter(membership=obj.membership, product__isnull=True)
            return DiscountMembershipSerializers(pro, many=True).data
        except Exception as err:
            return str(err)
    

    def get_order_type(self, obj):
        return 'Membership'
    
    def get_membership_price(self, obj):
        return (obj.price)
    

    def get_employee(self, membership_records):
        if membership_records.employee:
            return {
                'full_name': str(membership_records.employee.full_name),
            }
        return ''

    def get_location(self, membership_records):
        try:
            loc = BusinessAddress.objects.get(id = membership_records.location.id)
            return LocationSerializerLoyalty(loc).data
        except Exception as err:
            print(err)

    def get_client(self, membership_records):
        try:
            serializered_data = ClientSerializer(membership_records.client).data
            return serializered_data
        except Exception as err:
            return None
    
    
    def get_name(self, obj):
        try:
            return obj.membership.name
        except Exception as err:
            return None

    def get_discount_type(self, obj):
        try:
            return obj.membership.discount
        except Exception as err:
            return None
        
    
    class Meta:
        model = SaleRecordMembership
        fields = [
            'id',
            'name', 
            'client', 
            'location',
            # 'status',
            # 'quantity',
            'products', 
            'services',
            # 'checkout',
            'employee',
            # 'start_date', 
            # 'end_date',
            # 'total_price', 
            # 'payment_type', 
            'order_type',
            'price',
            'created_at',
            # 'discount_percentage', 
            'membership_price', 
            'discount_type' 
        ]


class CustomerLoyaltyPointsLogsSerializer(serializers.ModelSerializer):

    customer = serializers.SerializerMethodField()
    loyalty = serializers.SerializerMethodField()
    points_earned = serializers.SerializerMethodField()
    # points_redeemed = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()

    def get_customer(self, c_points):
        return {
            'customer_id' : f'{c_points.client.client_id}',
            'customer_name' : f'{c_points.client.full_name}',
        }

    def get_loyalty(self, c_points):
        return {
            'loyalty_name' : f'{c_points.loyalty_points.name}'
        }

    def get_points_earned(self, c_points):
        return c_points.total_earn

    # def get_points_redeemed(self, c_points):
    #     return c_points.points_redeemed

    def get_balance(self, c_points):
        return c_points.total_earn - c_points.points_redeemed


    class Meta:
        model = ClientLoyaltyPoint
        fields = ['customer', 'loyalty', 'points_earned', 'points_redeemed', 'balance', 'invoice']

class CustomerDetailedLoyaltyPointsLogsSerializer(serializers.ModelSerializer):

    date = serializers.SerializerMethodField()
    actual_sale_value_redeemed = serializers.SerializerMethodField()
    invoice_data = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    loyalty = serializers.SerializerMethodField()
    points_earned = serializers.SerializerMethodField()
    points_redeemed = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    checkout_data = serializers.SerializerMethodField()

    def get_date(self, c_points):
        return c_points.created_at.strftime('%Y-%m-%d')

    def get_actual_sale_value_redeemed(self, c_points):
        return c_points.actual_sale_value_redeemed

    def get_invoice_data(self, c_points):
        try:
            invoice = SaleInvoice.objects.get(id__icontains = c_points.invoice)
            serializer = SaleInvoiceSerializer(invoice, context=self.context)
            return serializer.data
        except Exception as e:
            return str(e)

    def get_customer(self, c_points):
        return {
            'customer_id' : f'{c_points.client.client_id}',
            'customer_name' : f'{c_points.client.full_name}',
        }

    def get_loyalty(self, c_points):
        return {
            'loyalty_name' : f'{c_points.loyalty.name}',
            'id' : f'{c_points.loyalty.id}',
        }

    def get_points_earned(self, c_points):
        return c_points.points_earned

    def get_points_redeemed(self, c_points):
        return c_points.points_redeemed

    def get_balance(self, c_points):
        return c_points.balance

    def get_checkout_data(self, c_points):
        from Sale.serializers import SaleOrders_CheckoutSerializer, SaleOrders_AppointmentCheckoutSerializer

        is_checkout = False
        try:
            data = Checkout.objects.filter(id = c_points.checkout)
            serializer = SaleOrders_CheckoutSerializer(data, many=True, context=self.context)

            if len(data) == 0:                
                data = AppointmentCheckout.objects.filter(id = c_points.checkout)
                # serializer = AppointmentCheckoutSerializer(data, many=True)
                serializer = SaleOrders_AppointmentCheckoutSerializer(data, many=True, context=self.context)

        except Exception as e:
            return str(e)

        return serializer.data
        



    class Meta:
        model = LoyaltyPointLogs
        fields = ['customer', 'loyalty', 'points_earned', 'points_redeemed','balance', 'checkout', 'checkout_data', 'invoice', 'invoice_data', 'actual_sale_value_redeemed', 'date']


class CustomerDetailedLoyaltyPointsLogsSerializerOP(serializers.ModelSerializer):

    customer = serializers.SerializerMethodField()
    loyalty = serializers.SerializerMethodField()

    def get_customer(self, c_points):
        return {
            'customer_id' : f'{c_points.client.client_id}',
            'customer_name' : f'{c_points.client.full_name}',
        }

    def get_loyalty(self, c_points):
        return {
            'loyalty_name' : f'{c_points.loyalty.name}',
        }

    class Meta:
        model = LoyaltyPointLogs
        fields = ['id', 'customer', 'loyalty', 'points_earned', 'points_redeemed','balance',
                  'checkout', 'invoice', 'actual_sale_value_redeemed', 'created_at']

class SaleInvoiceSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField(read_only = True)

    def get_file(self, obj):
        if obj.file:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=False)
                return f'{url}{obj.file}'
            except:
                return f'{obj.file}'
        return None
    class Meta:
        model = SaleInvoice
        fields = '__all__'


class CheckoutSerializer(serializers.ModelSerializer):
    gst = serializers.FloatField(source='tax_applied')
    gst1 = serializers.FloatField(source='tax_applied1')
    gst_price = serializers.FloatField(source='tax_amount')
    gst_price1 = serializers.FloatField(source='tax_amount1')


    class Meta:
        model = Checkout
        fields = '__all__'

class AppointmentCheckoutSerializer(serializers.ModelSerializer):
    tip = serializers.SerializerMethodField(read_only = True)


    def get_tip(self, appointment_checkout):
        tips = AppointmentEmployeeTip.objects.filter(
            appointment = appointment_checkout.appointment
        ).values('member', 'tip', 'id')
        tips = list(tips)
        return tips

    class Meta:
        model = AppointmentCheckout
        fields = '__all__'
        
class ClientImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class ClientResponse(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = "__all__"