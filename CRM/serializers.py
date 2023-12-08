from rest_framework import serializers
from Product.Constants.index import tenant_media_base_url
from CRM.models import *


class SegmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  Segment
        fields = '__all__'
        
class CampaignsSerializer(serializers.ModelSerializer):
        
    class Meta:
        model =  Campaign
        fields = '__all__'