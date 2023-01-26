from rest_framework import serializers
from Appointment.serializers import LocationSerializer
from Employee.models import Employee
from Product.Constants.index import tenant_media_base_url

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
                #   'duration', 'location', 'member', 'total_price',
                #   'payment_type','tip','gst', 'order_type','created_at'
                #   ]


class ReportsEmployeSerializer(serializers.ModelSerializer):    
    image = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField(read_only=True)
    sale_price = serializers.SerializerMethodField(read_only=True)
    
    def get_sale_price(self, obj):
        try:
            total = 0
            service_orders = ServiceOrder.objects.filter(is_deleted=False, member = obj)
            for ord  in service_orders:
                total += ord.total_price
                return total
        except Exception as err:
            return str(err)
    
    def get_location(self, obj):
        loc = obj.location.all()
        return LocationSerializer(loc, many =True ).data
    
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
        model = Employee
        fields = ['id', 'employee_id','is_active','full_name','image','location','created_at','sale_price']