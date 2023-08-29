from rest_framework import serializers

from .models import CustomFCMDevice

class FCMDeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomFCMDevice
        fields = '__all__'