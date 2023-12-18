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

        
class SegmentDropdownSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  Segment
        fields = ['id', 'name']
        
               
class CampaignsSerializer(serializers.ModelSerializer):
    segment_data = SegmentDropdownSerializer(read_only=True, source='segment')
    
    class Meta:
        model =  Campaign
        fields = ['id', 'title', 'content', 'start_date', 'end_date', 'campaign_type', 'segment_data']
    
    def get_segment_data(self, obj):
        segment = obj.segment
        return {'id': segment.id, 'name': segment.name}