


from rest_framework import serializers

from Business.models import BusinessType, Business, BusinessAddress, BusinessSocial, BusinessTheme
from Authentication.serializers import UserSerializer

class BusinessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessType
        fields = ['id', 'name', 'image']


class Business_GetSerializer(serializers.ModelSerializer):
    website = serializers.SerializerMethodField()
    facebook = serializers.SerializerMethodField()
    instagram = serializers.SerializerMethodField()

    def get_website(self, obj):
        try:
            social = BusinessSocial.objects.get(business=obj)
            return social.website
        except Exception as err:
            print(err)
            return None
    
    def get_facebook(self, obj):
        try:
            social = BusinessSocial.objects.get(business=obj)
            return social.facebook
        except:
            return None

    def get_instagram(self, obj):
        try:
            social = BusinessSocial.objects.get(business=obj)
            return social.instagram
        except:
            return None

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
            'website',
            'facebook',
            'instagram',
        ]


class Business_PutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            'business_name',
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

class BusinessThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessTheme
        fields = [
            'id',
            'primary_color',
            'secondary_color',
            'menu_option',
            'calendar_option',
        ]