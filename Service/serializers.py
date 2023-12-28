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

class BasicServiceSerializer(serializers.ModelSerializer):
    appointment_count = serializers.IntegerField()
    total_orders_quantity = serializers.IntegerField()
    service_orders = serializers.SerializerMethodField()

    def get_service_orders(self, obj):
        return obj.service_orders.values()
         

    class Meta:
        model = Service
        fields = ['id', 'name', 'appointment_count', 'total_orders_quantity', 'service_orders']