from rest_framework import serializers


from Client.models import Client

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields =['id','full_name','image','client_id','email','mobile_number','dob','postal_code','card_number','country','city','state', 'is_active']