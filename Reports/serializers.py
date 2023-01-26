from rest_framework import serializers

from Order.models import ServiceOrder


class ServiceOrderSerializer(serializers.ModelSerializer):
    # client = serializers.SerializerMethodField(read_only=True)
    # service = serializers.SerializerMethodField(read_only=True)
    # location = serializers.SerializerMethodField(read_only=True)
    # member  = serializers.SerializerMethodField(read_only=True)
    user  = serializers.SerializerMethodField(read_only=True)
    order_type  = serializers.SerializerMethodField(read_only=True)
    
    def get_order_type(self, obj):
        return 'Service'
    
    # def get_service(self, obj):
    #     try:
    #         serializers = ServiceSearchSerializer(obj.service).data
    #         return serializers
    #     except Exception as err:
    #         return None
        
    # def get_location(self, obj):
    #     try:
    #         serializers = LocationSerializer(obj.location).data
    #         return serializers
    #     except Exception as err:
    #         return None
    
    # def get_member(self, obj):
    #     try:
    #         serializers = MemberSerializer(obj.member, context=self.context).data
    #         return serializers
    #     except Exception as err:
    #         return None
        
    # def get_client(self, obj):
    #     try:
    #         serializers = ClientSerializer(obj.client).data
    #         return serializers
    #     except Exception as err:
    #         return None
        
    def get_user(self, obj):
        try:
            return obj.user.full_name
        except Exception as err:
            return None
    class Meta:
        model = ServiceOrder
        fields = ('__all__')
        #fields = ['id', 'client','quantity', 'service','created_at' ,'user',
                  'duration', 'location', 'member', 'total_price',
                  'payment_type','tip','gst', 'order_type','created_at'
                  ]