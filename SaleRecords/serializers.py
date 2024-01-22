from rest_framework import serializers
from SaleRecords.models import SaleRecords,SaleOrderItem, SaleOrderTip



class SaleItemsSerializers(serializers.ModelSerializer):
    class Meta:
        model = SaleOrderItem
        fields = '__all__'
        
        
class SaleOrderTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleOrderTip
        fields = '__all__'
        

class SaleRecordSerializer(serializers.ModelSerializer):
    sale_items = SaleItemsSerializers(many= True, read_only =True)
    sale_order_tips = SaleOrderTipSerializer(many = True, read_only = True)
    class Meta:
        model = SaleRecords
        fields = '__all__'
        