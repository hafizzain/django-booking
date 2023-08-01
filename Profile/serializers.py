


from rest_framework import serializers
from .models import UserLanguage
from Utility.serializers import LanguageSerializer

class UserLanguageSerializer(serializers.ModelSerializer):
    language = LanguageSerializer()

    
    class Meta:
        model = UserLanguage
        fields = ['id', 'language', 'is_default']