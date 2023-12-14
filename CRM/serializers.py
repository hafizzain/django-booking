from rest_framework import serializers
from Product.Constants.index import tenant_media_base_url
from CRM.models import *
from Appointment.models import Appointment

class SegmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  Segment
        fields = '__all__'
        
    # def create(self, validated_data):
    #     user = self.context['request'].user
    #     segment = Segment.objects.create(
    #         **validated_data,
    #         user=user
    #     )
        
    #     return segment
        
class CampaignsSerializer(serializers.ModelSerializer):
        
    class Meta:
        model =  Campaign
        fields = '__all__'
        