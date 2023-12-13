from rest_framework import serializers
from Product.Constants.index import tenant_media_base_url
from CRM.models import *
from Appointment.models import AppointmentService
from Order.models import Order, Checkout
from Appointment.models import Appointment

class SegmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  Segment
        fields = '__all__'
        
class CampaignsSerializer(serializers.ModelSerializer):
        
    class Meta:
        model =  Campaign
        fields = '__all__'
        
class ClientSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()
    total_done_appointments = serializers.SerializerMethodField(read_only=True)
    total_sales = serializers.SerializerMethodField(read_only=True)


    def get_total_done_appointments(self, obj):
        return AppointmentService.objects.filter(
            appointment_status__in = ['Done', 'Paid'],
            appointment__client = obj
        ).count()
    
    def get_total_sales(self, obj):
        total_price = 0
        appointments = AppointmentService.objects.filter(
            appointment_status__in = ['Done', 'Paid'],
            appointment__client = obj
        )
        for price in appointments:
            total_price += float(price.price or price.total_price or 0)

        checkout_orders_total = Checkout.objects.filter(
            is_deleted = False, 
            client = obj,
        )   
        total_orders = Order.objects.filter(
            checkout__id__in = list(checkout_orders_total.values_list('id', flat=True))
        )

        for order in total_orders:
            realPrice = order.price or order.total_price
            total_price += float(order.quantity) * float(realPrice)
    
        return total_price
    
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
        model = Client
        fields =['id','full_name','image','gender','created_at', 'total_done_appointments', 'total_sales']