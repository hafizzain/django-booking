from rest_framework import serializers
from Service.models import Service, ServiceTranlations
from Product.Constants.index import tenant_media_base_url, tenant_media_domain
from SaleRecords.models import *

class ServiceSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return f'{obj.image}'
        return None
    class Meta:
        model = Service
        fields ='__all__'

class ServiceTranslationsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceTranlations
        fields = ['id', 'service', 'service_name', 'language']

class BasicServiceSerializer(serializers.ModelSerializer):
    total_count = serializers.SerializerMethodField()
    
    def get_total_count(self, obj):
        sale_count = SaleRecordServices.objects.filter(service_id=obj.id).count()
        return obj.total_count+sale_count
    class Meta:
        model = Service
        fields = ['id', 'name', 'total_count']