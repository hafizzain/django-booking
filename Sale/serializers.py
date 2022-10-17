from dataclasses import field
from rest_framework import serializers

from Employee.models import Employee
from Business.models import BusinessAddress

from Service.models import Service

class EmployeeServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'full_name')

class LocationServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        fields = '__all__'
        
class ServiceSerializer(serializers.ModelSerializer):
    employee = EmployeeServiceSerializer(read_only=True)
    location = LocationServiceSerializer(read_only=True)
    class Meta:
        model = Service
        fields = ['id', 'name' , 'service_type', 'employee', 'parrent_service' , 'description', 'location']