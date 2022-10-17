from dataclasses import field
from rest_framework import serializers

from Employee.models import Employee
from Business.models import BusinessAddress

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