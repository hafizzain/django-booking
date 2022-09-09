from rest_framework import serializers
from Appointment.models import Appointment


class AppoinmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'