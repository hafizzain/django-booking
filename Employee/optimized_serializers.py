from rest_framework import serializers
from .models import Employee, GiftCards

from Employee.Constants.total_sale import total_sale_employee
from Product.Constants.index import tenant_media_base_url, tenant_media_domain



class OptimizedEmployeeSerializerDashboard(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()
    total_sale = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return None
    
    def get_total_sale(self, obj):
        return total_sale_employee(obj.id)
    class Meta:
        model = Employee
        fields =['full_name', 'image', 'total_sale', 'employee_id']


class GiftCardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftCards
        fields = "__all__"