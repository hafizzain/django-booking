
from Business.models import BusinessAddress
from rest_framework import serializers
from Product.Constants.index import tenant_media_base_url, tenant_media_domain
from Order.models import VoucherOrder, MemberShipOrder
from Product.models import Product
from Service.models import Service
from Utility.models import Country, State, City

from Client.models import Client, ClientGroup, CurrencyPriceMembership, DiscountMembership, LoyaltyPoints, Subscription, Promotion , Rewards , Membership, Vouchers, ClientLoyaltyPoint, LoyaltyPointLogs , VoucherCurrencyPrice 

class LocationSerializerLoyalty(serializers.ModelSerializer):
    
    class Meta:
        model = BusinessAddress
        fields = ('id', 'address_name')

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name')
        # exclude = ['is_deleted', 'created_at', 'slug', 'published'
        #            , 'user', 'business' , 'vendor', 'category' ,'brand' , 'product_type' ,'cost_price' , 'full_price'
        #            , 'sell_price', 'tax_rate', 'short_description' , 'description' , 'barcode_id', ''
        #            ]

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name')
        #exclude = ['is_deleted', 'created_at', 'updated_at']

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        exclude = ['is_deleted', 'created_at', 'unique_code', 'key']

class ClientSerializer(serializers.ModelSerializer):
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
                request = self.context["request"]
                url = tenant_media_base_url(request)
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
                url = tenant_media_domain(request)
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
    client =serializers.SerializerMethodField(read_only=True)
    
    def get_client(self, obj):
        all_client =obj.client.all()
        return ClientSerializer(all_client, many=True, context=self.context).data
    
    class Meta:
        model = ClientGroup
        fields = ['id','name','business','is_active','email','created_at','client']
    
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
        try:
            pro = CurrencyPriceMembership.objects.filter(membership = obj).distinct()
            return CurrencyPriceMembershipSerializers(pro, many= True).data
        except Exception as err:
            print(err)
            
    class Meta:
        model = Membership
        fields = ['id', 'name','valid_for','discount','description', 'term_condition','products', 'services', 'currency_membership']

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
        fields = ['id', 'name','user','business','voucher_type',
                'validity','sales','is_deleted','is_active','created_at','currency_voucher','discount_percentage', 'voucher_count']


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
                  'name','created_at','discount_percentage', 'voucher_price' ]

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
        return obj.current_price
    

    def get_employee(self, membership_order):
        if membership_order.member:
            return {
                'full_name' : str(membership_order.member.full_name),
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
        model = MemberShipOrder
        fields = ['id','name', 'client' , 'location' , 
                  'status','quantity','products', 'services', 'checkout','employee','start_date', 'end_date',
                  'total_price', 'payment_type' , 'order_type','price',
                  'name','created_at','discount_percentage', 'membership_price', 'discount_type' ]


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
        fields = ['customer', 'loyalty', 'points_earned', 'points_redeemed', 'balance']
    
class CustomerDetailedLoyaltyPointsLogsSerializer(serializers.ModelSerializer):

    date = serializers.SerializerMethodField()
    actual_sale_value_redeemed = serializers.SerializerMethodField()
    invoice = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    loyalty = serializers.SerializerMethodField()
    points_earned = serializers.SerializerMethodField()
    points_redeemed = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()

    def get_date(self, c_points):
        return c_points.created_at.strftime('%Y-%m-%d')

    def get_actual_sale_value_redeemed(self, c_points):
        return c_points.actual_sale_value_redeemed

    def get_invoice(self, c_points):
        return c_points.invoice

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


    class Meta:
        model = LoyaltyPointLogs
        fields = ['customer', 'loyalty', 'points_earned', 'points_redeemed','balance', 'invoice', 'actual_sale_value_redeemed', 'date']