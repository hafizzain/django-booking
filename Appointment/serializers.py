from pyexpat import model
from rest_framework import serializers
from Appointment.models import Appointment, AppointmentService
from Employee.models import Employee
from Service.models import Service



class ServiceAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name', 'price')

class EmployeAppoinmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'full_name', 'image')
        
class CalenderSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField(read_only=True)
    service = serializers.SerializerMethodField(read_only=True)
    appointment_id= serializers.SerializerMethodField(read_only=True)
    client_type= serializers.SerializerMethodField(read_only=True)
    
    def get_client_type(self, obj):
        try:
            return obj.appointment.client_type
        except Exception as err:
            None
    
    def get_appointment_id(self, obj):
        try:
            return obj.appointment.id
        except Exception as err:
            None
    
    def get_service(self, obj):
        try:
            return ServiceAppointmentSerializer(obj.service).data
        except Exception:
            return None
    
    def get_member(self, obj):
        try:
            return EmployeAppoinmentSerializer(obj.member).data
        except Exception:
            return None
    
    class Meta:
        model = AppointmentService
        fields =['id','appointment_id','appointment_date', 'appointment_time','client_type','duration','service', 'member']

class AppoinmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'