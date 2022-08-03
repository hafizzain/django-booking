


from rest_framework import serializers

from Business.models import BusinessType

class BusinessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessType
        fields = ['id', 'name', 'image']