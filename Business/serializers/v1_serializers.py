


from rest_framework import serializers

from Business.models import BusinessType, Business, BusinessAddress
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
            'logo',
            'banner',
            'postal_code',
            'week_start',
            'team_size',
            'currency',
            'timezone',
            'time_format',
            'how_find_us',
        ]


class Business_PutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            'timezone',
            'time_format',
            'week_start',
        ]

class BusinessAddress_GetSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        fields = [
            'id',
            'country',
            'state',
            'city',
            'address',
            'postal_code',
            'website',
            'is_primary',
        ]