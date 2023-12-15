from rest_framework import serializers
from Product.Constants.index import tenant_media_base_url
from CRM.models import *
from Appointment.models import Appointment
from Client.models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'full_name', 'image'] 
        
        
class SegmentSerializer(serializers.ModelSerializer):
    client_data = ClientSerializer(many=True, read_only=True, source='client')
    
    class Meta:
        model =  Segment
        fields = '__all__'
    
    def get_client_data(self, obj):
        return [{'full_name': client.full_name,
                    'image': client.image} for client in obj.client.all()]

        
class CampaignsSerializer(serializers.ModelSerializer):
        
    class Meta:
        model =  Campaign
        fields = '__all__'
        