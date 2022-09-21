from pyexpat import model
from rest_framework import serializers
from Appointment.models import Appointment
from Employee.models import Employee


class EmployeAppoinmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'full_name', 'image')
        
class CalenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

class AppoinmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'