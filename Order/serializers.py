from rest_framework import serializers


from .models  import Checkout



class CreatedAtCheckoutSerializer(serializers.ModelSerializer):

    class Meta:
        model = Checkout
        fields = ['created_at']