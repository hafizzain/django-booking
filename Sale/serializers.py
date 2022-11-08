from dataclasses import field
from pyexpat import model
from rest_framework import serializers
from Client.models import Client, Membership

from Employee.models import Employee, EmployeeSelectedService
from Business.models import BusinessAddress
from Order.models import Checkout, MemberShipOrder, ProductOrder, ServiceOrder, VoucherOrder
from Product.Constants.index import tenant_media_base_url
from Product.models import ProductStock

from Service.models import PriceService, Service, ServiceGroup

class PriceServiceSerializers(serializers.ModelSerializer):
    class Meta:
        model = PriceService
        fields = '__all__'
        

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        fields = ['id','address_name']
        
class ClientSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Client
        fields = ['id','full_name']
        
class MemberSerializer(serializers.ModelSerializer):
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
        model = Employee
        fields = ['id','full_name', 'image' ]
        
class ServiceSearchSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Service
        fields = ['id','name']

class EmployeeSelectedServiceSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    
    def get_full_name(self, obj):
        return obj.employee.full_name
    
    class Meta:
        model = EmployeeSelectedService
        fields = ['id', 'service', 'employee', 'level', 'full_name']

class LocationServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        #fields = '__all__'
        exclude =  ['is_primary', 'is_active', 'is_closed', 'is_deleted', 'created_at', 'user', 'business', 'is_email_verified','is_mobile_verified']
        
class ServiceSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)
    employees = serializers.SerializerMethodField(read_only=True)
    service_group = serializers.SerializerMethodField(read_only=True)
    
    priceservice = serializers.SerializerMethodField(read_only=True)
    
    def get_priceservice(self, obj):
        try:
            ser = PriceService.objects.filter(service = obj)
            return PriceServiceSerializers(ser, many = True).data
        except Exception as err:
            print(err)
            
    
    def get_service_group(self, obj):
        try:
            group = ServiceGroup.objects.get(services = obj)
            return ServiceSearchSerializer(group).data
        except Exception as err:
            print(str(err))
    
    def get_employees(self, obj):
        emp = EmployeeSelectedService.objects.filter(service = obj) 
        return EmployeeSelectedServiceSerializer(emp, many = True).data
        
    
    def get_location(self, obj):
        #loc = BusinessAddress.objects.filter(is_deleted = False)
        return LocationServiceSerializer(obj.location, many = True).data
    
    #employee = EmployeeServiceSerializer(read_only=True, many = True)
    
    class Meta:
        model = Service
        fields = [
            'id',
            'name' , 
            'service_availible',
            'employees', 
            'parrent_service' , 
            'description', 
            'location',
            'controls_time_slot',
            'initial_deposit',
            'client_can_book',
            'slot_availible_for_online',
            'is_package',
            'service_group',
            'priceservice',
            'enable_team_comissions',
            'enable_vouchers',
            ]
        
        
class ProductOrderSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)
    member  = serializers.SerializerMethodField(read_only=True)
    client = serializers.SerializerMethodField(read_only=True)
    product_name  = serializers.SerializerMethodField(read_only=True)
    order_type  = serializers.SerializerMethodField(read_only=True)
    #item_sold = serializers.SerializerMethodField(read_only=True)
    
    # def get_item_sold(self, obj):
    #     try:
    #         product_stck =ProductStock.objects.get(product = obj)
    #         return product_stck.sold_quantity
    #     except Exception as err:
    #         print(err)
    
    def get_order_type(self, obj):
        return 'Product'
    
    def get_product_name(self, obj):
        try:
            return obj.product.name
        except Exception as err:
            return None
    
    def get_location(self, obj):
        try:
            serializers = LocationSerializer(obj.location).data
            return serializers
        except Exception as err:
            return None
    
    def get_member(self, obj):
        try:
            serializers = MemberSerializer(obj.member, context=self.context).data
            return serializers
        except Exception as err:
            return None
        
    def get_client(self, obj):
        try:
            serializers = ClientSerializer(obj.client).data
            return serializers
        except Exception as err:
            return None
    
    class Meta:
        model = ProductOrder
        fields = ['id', 'client','status','created_at', 'location', 'member', 'tip', 'total_price' , 'payment_type', 'product_name', 'gst', 'order_type', 'sold_quantity' ]
   
        
class ServiceOrderSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    service = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    member  = serializers.SerializerMethodField(read_only=True)
    user  = serializers.SerializerMethodField(read_only=True)
    order_type  = serializers.SerializerMethodField(read_only=True)
    
    def get_order_type(self, obj):
        return 'Service'
    
    def get_service(self, obj):
        try:
            serializers = ServiceSearchSerializer(obj.service).data
            return serializers
        except Exception as err:
            return None
        
    def get_location(self, obj):
        try:
            serializers = LocationSerializer(obj.location).data
            return serializers
        except Exception as err:
            return None
    
    def get_member(self, obj):
        try:
            serializers = MemberSerializer(obj.member, context=self.context).data
            return serializers
        except Exception as err:
            return None
        
    def get_client(self, obj):
        try:
            serializers = ClientSerializer(obj.client).data
            return serializers
        except Exception as err:
            return None
        
    def get_user(self, obj):
        try:
            return obj.user.full_name
        except Exception as err:
            return None
    class Meta:
        model = ServiceOrder
        fields = ['id', 'client', 'service','created_at' ,'user', 'duration', 'location', 'member', 'total_price', 'payment_type','tip','gst', 'order_type','created_at']
        
class MemberShipOrderSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    member  = serializers.SerializerMethodField(read_only=True)
    membership  = serializers.SerializerMethodField(read_only=True)
    #location = serializers.SerializerMethodField(read_only=True)
    order_type  = serializers.SerializerMethodField(read_only=True)
    
    def get_order_type(self, obj):
        return 'Membership'
    
    # def get_location(self, obj):
    #     try:
    #         serializers = LocationSerializer(obj.location).data
    #         return serializers
    #     except Exception as err:
    #         return None
    
    def get_member(self, obj):
        try:
            serializers = MemberSerializer(obj.member,context=self.context ).data
            return serializers
        except Exception as err:
            return None
        
    def get_client(self, obj):
        try:
            serializers = ClientSerializer(obj.client).data
            return serializers
        except Exception as err:
            return None
        
    def get_membership(self, obj):
        try:
            return obj.membership.name
        except Exception as err:
            return None
    # ,'location' ,'start_date', 'end_date','status', 'total_price', 'payment_type', 'order_type'
    
    class Meta:
        model = MemberShipOrder
        fields =['id', 'membership','order_type' ,'client','member','location' ,'start_date', 'end_date','status', 'total_price', 'payment_type' ]
        
class VoucherOrderSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    member  = serializers.SerializerMethodField(read_only=True)
    voucher = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    order_type  = serializers.SerializerMethodField(read_only=True)
    
    def get_order_type(self, obj):
        return 'Voucher'
    
    def get_location(self, obj):
        try:
            serializers = LocationSerializer(obj.location).data
            return serializers
        except Exception as err:
            return None
    
    def get_member(self, obj):
        try:
            serializers = MemberSerializer(obj.member, context=self.context).data
            return serializers
        except Exception as err:
            return None
        
    def get_client(self, obj):
        try:
            serializers = ClientSerializer(obj.client).data
            return serializers
        except Exception as err:
            return None
    
    def get_voucher(self, obj):
        try:
            return obj.voucher.name
        except Exception as err:
            return None
    
    
    class Meta:
        model = VoucherOrder
        fields =['id', 'voucher', 'client' , 'location' , 'member' ,'start_date', 'end_date','status', 'total_price', 'payment_type' , 'order_type']
    
class ServiceGroupSerializer(serializers.ModelSerializer):
    
    services  = serializers.SerializerMethodField(read_only=True)
    
    def get_services(self, obj):
        try:
            all_service = obj.services.all()
            #ser = Service.objects.get(id = obj.services)
            return ServiceSearchSerializer(all_service, many = True).data
        except Exception as err:
            print(str(err))
    
    class Meta:
        model = ServiceGroup
        fields = ['id', 'business', 'name', 'services']
        
class CheckoutSerializer(serializers.ModelSerializer):
    product  = serializers.SerializerMethodField(read_only=True) #ProductOrderSerializer(read_only = True)
    service  = serializers.SerializerMethodField(read_only=True) #ProductOrderSerializer(read_only = True)
    
    def get_product(self, obj):
        try:
            check = ProductOrder.objects.filter(checkout =  obj)
            #all_service = obj.product.all()
            return ProductOrderSerializer(check, many = True , context=self.context ).data
        except Exception as err:
            print(str(err))
            
    def get_service(self, obj):
        try:
            check = ServiceOrder.objects.filter(checkout =  obj)
            #all_service = obj.product.all()
            return ProductOrderSerializer(check, many = True , context=self.context ).data
        except Exception as err:
            print(str(err))
    
    class Meta:
        model = Checkout
        fields = ['id', 'product', 'service']