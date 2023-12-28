from rest_framework import serializers
from HRM.models import *

class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'
        
    
    def create(self, validated_data):
        is_active = validated_data.pop('is_active', True)
        holiday = Holiday.objects.create(is_active=is_active, **validated_data)
        return holiday
    