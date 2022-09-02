from rest_framework import serializers
from Product.Constants.index import tenant_media_base_url


from Client.models import Client, ClientGroup

class ClientSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return None
    
    class Meta:
        model = Client
        fields =['id','full_name','image','client_id','email','mobile_number','dob','postal_code','card_number','country','city','state', 'is_active']
        
        
class ClientGroupSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ClientGroup
        fields = ['id','name','business','is_active','client','email']
    