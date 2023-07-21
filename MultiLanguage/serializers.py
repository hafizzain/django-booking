from .models import *
from rest_framework import serializers
from Utility.serializers import LanguageSerializer
from Utility.models import Language
from Business.models import BusinessAddress
class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Labels
        fields = '__all__'


class BusinessAddressSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = BusinessAddress
        fields = ['id', 'address_name' ]

class InvoiceTransSerializer(serializers.ModelSerializer):
    language_data = serializers.SerializerMethodField()
    location_data = serializers.SerializerMethodField()
    
    def get_language_data(self, obj):
        lang = Language.objects.get(id__icontains = str(obj.language))
        return LanguageSerializer(lang).data
    
    def get_location_data(self, obj):
        loc = BusinessAddress.objects.get(id__icontains = str(obj.location))
        return BusinessAddressSerializers(loc).data


    class Meta:
        model = InvoiceTranslation
        fields = '__all__'


