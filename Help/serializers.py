from rest_framework import serializers
from .models import HelpContent
from Product.Constants.index import tenant_media_base_url

class HelpContentSerializer(serializers.ModelSerializer):
    imagee = serializers.SerializerMethodField()
    
    def get_imagee(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return ''
    
    class Meta:
        model = HelpContent
        fields = ['id', 'content', 'parent_comment', 'is_parent', 'imagee']
