from rest_framework import serializers
from Product.Constants.index import tenant_media_base_url
from CRM.models import *
from Appointment.models import Appointment
from Client.models import Client


class ClientSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()


    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return f'{obj.image}'
        return None
    
    class Meta:
        model = Client
        fields = ['id', 'full_name', 'image'] 
        
        
class SegmentSerializer(serializers.ModelSerializer):
    client_data = serializers.SerializerMethodField(read_only=True)
    def get_client_data(self, obj):
        request = self.context.get('request')
        clients = obj.client.all()
        serializer = ClientSerializer(clients, many=True, context={'request': request})
        return serializer.data 
    class Meta:
        model =  Segment
        fields = ['id', 'name', 'segment_type', 'description',
                  'client_data', 'created_at', 'is_active', 'client']
           
class SegmentDropdownSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  Segment
        fields = ['id', 'name']
        
               
class CampaignsSerializer(serializers.ModelSerializer):
    segment_data = SegmentDropdownSerializer(read_only=True, source='segment')
    
    class Meta:
        model =  Campaign
        fields = '__all__'
    
    def get_segment_data(self, obj):
        segment = obj.segment
        return {'id': segment.id, 'name': segment.name}