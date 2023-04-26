from Business.models import BusinessAddress
from rest_framework import serializers
from Product.Constants.index import tenant_media_base_url, tenant_media_domain

from Product.models import Product
from Service.models import Service
from Utility.models import Country, State, City

from Client.models import Client, ClientGroup, CurrencyPriceMembership, DiscountMembership, LoyaltyPoints, Subscription, Promotion , Rewards , Membership, Vouchers, ClientLoyaltyPoint, LoyaltyPointLogs

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
    
    class Meta:
        model = Vouchers
        fields = '__all__'


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
        fields = '__all__'
        

class ClientLoyaltyPointSerializer(serializers.ModelSerializer):
    # location = serializers.SerializerMethodField(read_only=True)
    
    # def get_location(self, obj):
    #     try:
    #         loc = BusinessAddress.objects.get(id = obj.location.id)
    #         return LocationSerializerLoyalty(loc).data
    #     except Exception as err:
    #         print(err)
    class Meta:
        model = ClientLoyaltyPoint
        fields = '__all__'
    
class CustomerLoyaltyPointsLogsSerializer(serializers.ModelSerializer):

    customer = serializers.SerializerMethodField()
    loyalty = serializers.SerializerMethodField()
    points_earned = serializers.SerializerMethodField()
    points_redeemed = serializers.SerializerMethodField()
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

    def get_points_redeemed(self, c_points):
        return c_points.points_redeemed

    def get_balance(self, c_points):
        return 0


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
        return '0000-00-00'

    def get_actual_sale_value_redeemed(self, c_points):
        return 0

    def get_invoice(self, c_points):
        return {}

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

    def get_points_redeemed(self, c_points):
        return c_points.points_redeemed

    def get_balance(self, c_points):
        return 0


    class Meta:
        model = LoyaltyPointLogs
        fields = ['customer', 'loyalty', 'points_earned', 'points_redeemed', 'balance', 'invoice', 'actual_sale_value_redeemed', 'date']