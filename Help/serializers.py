from rest_framework import serializers
from .models import HelpContent

class HelpContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpContent
        fields = ['content', 'parent_comment', 'is_parent']
