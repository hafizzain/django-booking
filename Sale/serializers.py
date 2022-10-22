from dataclasses import field
from rest_framework import serializers
from Client.models import Membership

from Employee.models import Employee
from Business.models import BusinessAddress
from Order.models import MemberShipOrder, ProductOrder, ServiceOrder, VoucherOrder

from Service.models import Service

class EmployeeServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class LocationServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        #fields = '__all__'
        exclude =  ['is_primary', 'is_active', 'is_closed', 'is_deleted', 'created_at', 'user', 'business', 'is_email_verified','is_mobile_verified']
        
class ServiceSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)
    
    def get_location(self, obj):
        return LocationServiceSerializer(obj.location, many = True).data
    
    employee = EmployeeServiceSerializer(read_only=True, many = True)
    
    class Meta:
        model = Service
        fields = [
            'id',
            'name' , 
            'service_type', 
            'employee', 
            'parrent_service' , 
            'description', 
            'location',
            'duration',
            'enable_team_comissions',
            'enable_vouchers',
            'controls_time_slot',
            'initial_deposit',
            'client_can_book',
            'slot_availible_for_online',
            'price',
            'is_package'
            ]
class ProductOrderSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only=True)
    member  = serializers.SerializerMethodField(read_only=True)
    client = serializers.SerializerMethodField(read_only=True)
    
    def get_location(self, obj):
        try:
            return obj.location.address_name
        except Exception as err:
            return None
    
    def get_member(self, obj):
        try:
            return obj.member.full_name
        except Exception as err:
            return None
        
    def get_client(self, obj):
        try:
            return obj.client.full_name
        except Exception as err:
            return None
    
    class Meta:
        model = ProductOrder
        fields = ['id', 'client','status','created_at', 'location', 'member', 'tip', 'total_price' , 'payment_type' ]
   
        
class ServiceOrderSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    service = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    member  = serializers.SerializerMethodField(read_only=True)
    user  = serializers.SerializerMethodField(read_only=True)
    
    def get_client(self, obj):
        try:
            return obj.client.full_name
        except Exception as err:
            return None
    
    def get_service(self, obj):
        try:
            return obj.service.name
        except Exception as err:
            return None
        
    def get_location(self, obj):
        try:
            return obj.location.address_name
        except Exception as err:
            return None
        
    def get_member(self, obj):
        try:
            return obj.member.full_name
        except Exception as err:
            return None
        
    def get_user(self, obj):
        try:
            return obj.user.full_name
        except Exception as err:
            return None
    class Meta:
        model = ServiceOrder
        fields = ['id', 'client', 'service','created_at' ,'user', 'duration', 'location', 'member', 'total_price', 'payment_type']
        
class MemberShipOrderSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    member  = serializers.SerializerMethodField(read_only=True)
    membership  = serializers.SerializerMethodField(read_only=True)
    
    def get_member(self, obj):
        try:
            return obj.member.full_name
        except Exception as err:
            return None
        
    def get_membership(self, obj):
        try:
            return obj.membership.name
        except Exception as err:
            return None
    
    def get_client(self, obj):
        try:
            return obj.client.full_name
        except Exception as err:
            return None
    
    class Meta:
        model = MemberShipOrder
        fields =['id', 'membership', 'client' , 'member' ,'start_date', 'end_date','status', 'total_price', 'payment_type' ]
        
class VoucherOrderSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    member  = serializers.SerializerMethodField(read_only=True)
    voucher = serializers.SerializerMethodField(read_only=True)
    
    def get_voucher(self, obj):
        try:
            return obj.voucher.name
        except Exception as err:
            return None
    
    def get_member(self, obj):
        try:
            return obj.member.full_name
        except Exception as err:
            return None
    
    def get_client(self, obj):
        try:
            return obj.client.full_name
        except Exception as err:
            return None
    
    
    class Meta:
        model = VoucherOrder
        fields =['id', 'voucher', 'client' , 'member' ,'start_date', 'end_date','status', 'total_price', 'payment_type' ]