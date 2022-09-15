from rest_framework import serializers
from Service.models import Service

class ServiceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Service
        fields ='__all__'