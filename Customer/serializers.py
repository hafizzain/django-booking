from rest_framework import serializers

from Appointment.models import Appointment, AppointmentService
from Business.models import BusinessAddress
from Product.Constants.index import tenant_media_base_url
from Employee.models import Employee
from Service.models import PriceService, Service


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        fields = ['id','address_name']

class EmployeAppoinmentSerializer(serializers.ModelSerializer):
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
        fields = ('id', 'full_name', 'image')
        
class ServiceAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name', 'price')
        
class AppointmentServiceClientSerializer(serializers.ModelSerializer):
    business_address = serializers.SerializerMethodField()
    member = serializers.SerializerMethodField()
    service = serializers.SerializerMethodField()
    
    def get_business_address(self, obj):
        try:
            addres = BusinessAddress.objects.get(id = str(obj.business_address) )
            return LocationSerializer(addres).data
        except Exception as err:
            pass
        
    def get_member(self, obj):
        try:
            emp = Employee.objects.get(id = str(obj.member) )
            return EmployeAppoinmentSerializer(emp).data
        except Exception as err:
            pass
    
    
    def get_service(self, obj):
        try:
            service = Service.objects.get(id = str(obj.service) )
            return ServiceAppointmentSerializer(service).data
        except Exception as err:
            pass
            
    class Meta:
        model = AppointmentService
        fields = '__all__'
    

class AppointmentClientSerializer(serializers.ModelSerializer):
    appointment_service = serializers.SerializerMethodField()

    def get_appointment_service(self,obj):
        service = AppointmentService.objects.filter(appointment = obj)
        return AppointmentServiceClientSerializer(service, many = True).data

    class Meta:
        model = Appointment
        fields = '__all__'