from rest_framework import serializers

from Appointment.models import Appointment, AppointmentService

class AppointmentServiceClientSerializer(serializers.ModelSerializer):
    
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