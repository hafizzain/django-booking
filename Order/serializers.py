from rest_framework import serializers


from .models  import Checkout



class CreatedAtCheckoutSerializer(serializers.ModelSerializer):

    model = Checkout
    fields = ['created_at']