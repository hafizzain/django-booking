

from rest_framework import serializers

class DealSerializer(serializer.ModelSerializer):
    class Meta:
        model = Deal
        fields = '__all__'