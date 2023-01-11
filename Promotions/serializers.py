from rest_framework import serializers

from Business.models import BusinessAddress, BusinessTax
from Product.Constants.index import tenant_media_base_url
from django_tenants.utils import tenant_context

from Promotions.models import DirectOrFlatDiscount , CategoryDiscount , DateRestrictions , DayRestrictions, BlockDate

class BlockDateSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    class Meta:
        model = BlockDate
        fields = '__all__'
        
class DayRestrictionsSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    class Meta:
        model = DayRestrictions
        fields = '__all__'
class LocationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BusinessAddress
        fields = ['id','address_name']        
        
class DateRestrictionsSerializers(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()
    is_deleted = serializers.SerializerMethodField(read_only=True)
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    
    def get_address(self, obj):
        try:
            address = BusinessAddress.objects.get(id =obj.business_address)
            return LocationSerializer(address).data
        except Exception as err:
            pass
    class Meta:
        model = DateRestrictions
        fields = '__all__'
        
class CategoryDiscountSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    class Meta:
        model = CategoryDiscount
        fields = '__all__'

class DirectOrFlatDiscountSerializers(serializers.ModelSerializer):
    category_discount = serializers.SerializerMethodField(read_only=True)
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    is_deleted = serializers.SerializerMethodField(read_only=True)
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    
    def get_type(self, obj):
        return 'Direct Or Flat'
    
    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(directorflat = obj)
            return BlockDateSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(directorflat = obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    
    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(directorflat = obj)
            return DayRestrictionsSerializers(ser, many = True).data
        except Exception as err:
            pass
        
    
    
    def get_category_discount(self, obj):
        try:
            ser = CategoryDiscount.objects.filter(directorflat = obj)
            return CategoryDiscountSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    class Meta:
        model = DirectOrFlatDiscount
        fields = '__all__'