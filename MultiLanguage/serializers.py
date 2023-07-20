from .models import *
from rest_framework import serializers

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Labels
        fields = '__all__'



class InvoiceTransSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceTranslation
        fields = '__all__'