from rest_framework import serializers
from Product.Constants.index import tenant_media_base_url

from Product.models import Product
from Service.models import Service

from Client.models import Client, ClientGroup, Subscription, Promotion , Rewards , Membership, Vouchers

class ClientSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

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
        fields =['id','full_name','image','client_id','email','mobile_number','dob','postal_code','address','gender','card_number','country','city','state', 'is_active']
        
        
class ClientGroupSerializer(serializers.ModelSerializer):
    client =serializers.SerializerMethodField()
    
    def get_client(self, obj):
        all_client =obj.client.all()
        return ClientSerializer(all_client, many=True, context=self.context).data
    
    class Meta:
        model = ClientGroup
        fields = ['id','name','business','is_active','email','created_at','client']
    
class SubscriptionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Subscription
        fields ='__all__'
     
     
class RewardSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField(read_only=True)
    service_name = serializers.SerializerMethodField(read_only=True)
    
    def get_product_name(self, obj):
        try:
            return obj.product.name
        except Exception as err:
            return None
        
    def get_service_name(self, obj):
        try:
            return obj.service.name
        except Exception:
            return None
    
    class Meta:
        model = Rewards
        fields =['id','name', 'reward_value', 'discount', 'total_points' ,'product_name' , 'service_name' ]
        
class PromotionSerializer(serializers.ModelSerializer):
    
    product_name = serializers.SerializerMethodField(read_only=True)
    service_name = serializers.SerializerMethodField(read_only=True)
    
    def get_product_name(self, obj):
        try:
            return obj.product.name
        except Exception as err:
            return None
        
    def get_service_name(self, obj):
        try:
            return obj.service.name
        except Exception:
            return None
    
    class Meta:
        model = Promotion
        fields = ['id','promotion_type', 'product_name', 'products', 'service_name','services', 'discount_service', 'discount_product','discount','duration']
        
class MembershipSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Membership
        fields = '__all__'

class VoucherSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Vouchers
        fields = '__all__'