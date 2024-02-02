

from rest_framework import serializer

class DealSerializer(serializer.ModelSerializer):
    class Meta:
        model = Deal
        fields = '__all__'