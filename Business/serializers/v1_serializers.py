


from rest_framework import serializers

from Business.models import BusinessType, Business
from Authentication.serializers import UserSerializer

class BusinessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessType
        fields = ['id', 'name', 'image']


class Business_GetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Business
        fields = [
            'id',
            'business_name',
        ]


class Business_PutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            'timezone',
            'time_format',
            'week_start',
        ]