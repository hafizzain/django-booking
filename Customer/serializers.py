from rest_framework import serializers

from Appointment.models import Appointment, AppointmentService, AppointmentCheckout
from Business.models import BusinessAddress
from Product.Constants.index import tenant_media_base_url
from Employee.models import Employee, EmployeeProfessionalInfo
from Service.models import PriceService, Service


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        fields = ['id','address_name', 'address']

class EmployeAppoinmentSerializer(serializers.ModelSerializer):
    designation = serializers.SerializerMethodField()
    #image = serializers.SerializerMethodField()
    
    def get_designation(self, obj):
        try:
            designation = EmployeeProfessionalInfo.objects.get(employee = obj)
            return designation.designation
        except Exception as err:
            pass
            
    # def get_image(self, obj):
    #     try:
    #         if obj.image:
    #             try:
    #                 tenant = self.context["tenant"]
    #                 url = tenant_media_base_url(tenant)
    #                 return f'{url}{obj.image}'
    #             except:
    #                 return obj.image
    #         return None
    #     except Exception as err:
    #         return str(err)
    
    class Meta:
        model = Employee
        fields = ('id', 'full_name', 'image','designation')
        
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
            return EmployeAppoinmentSerializer(emp, context=self.context).data
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
    tip = serializers.SerializerMethodField()

    def get_appointment_service(self,obj):
        service = AppointmentService.objects.filter(appointment = obj)
        return AppointmentServiceClientSerializer(service, many = True, context=self.context).data
    
    def get_tip(self,obj):
        service = AppointmentCheckout.objects.filter(appointment = obj)
        total_tip = sum(int(obj.tip) for obj in service)
        return total_tip

    class Meta:
        model = Appointment
        fields = '__all__'