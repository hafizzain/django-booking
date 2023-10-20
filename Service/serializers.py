from rest_framework import serializers
from Service.models import Service, ServiceTranlations

class ServiceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Service
        fields ='__all__'

class ServiceTranslationsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceTranlations
        fields = ['id', 'service', 'service_name', 'language']