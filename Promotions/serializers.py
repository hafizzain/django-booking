
from Sale.serializers import AvailPriceServiceSerializers,PriceServiceSerializers
from Service.models import PriceService
from rest_framework import serializers

from Business.models import BusinessAddress, BusinessTax
from Product.Constants.index import tenant_media_base_url
from django_tenants.utils import tenant_context

from Promotions.models import BundleFixed, ComplimentaryDiscount, DirectOrFlatDiscount , CategoryDiscount , DateRestrictions , DayRestrictions, BlockDate, DiscountOnFreeService, FixedPriceService, FreeService, MentionedNumberService, PackagesDiscount, ProductAndGetSpecific, PurchaseDiscount, RetailAndGetService, ServiceDurationForSpecificTime, ServiceGroupDiscount, SpecificBrand, SpecificGroupDiscount, SpendDiscount, SpendSomeAmount, SpendSomeAmountAndGetDiscount, UserRestrictedDiscount, Service

class ServiceGroupDiscountSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    class Meta:
        model = ServiceGroupDiscount
        fields = '__all__'


class AvailServiceGroupDiscountSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    class Meta:
        model = ServiceGroupDiscount
        fields = ['specificgroupdiscount','discount']
class ServiceDurationForSpecificTimeSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    class Meta:
        model = ServiceDurationForSpecificTime
        fields = '__all__'

class AvailServiceDurationForSpecificTimeSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    class Meta:
        model = ServiceDurationForSpecificTime
        fields = ['id','service']
class SpendSomeAmountAndGetDiscountSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    class Meta:
        model = SpendSomeAmountAndGetDiscount
        fields = '__all__'

class AvailSpendSomeAmountAndGetDiscountSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    class Meta:
        model = SpendSomeAmountAndGetDiscount
        fields = ['id','spandsomeamount']
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

class AvailBlockDateSerializers(serializers.ModelSerializer):
    
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    class Meta:
        model = BlockDate
        fields = ['date','id']
        
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

class AvailDayRestrictionsSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    class Meta:
        model = DayRestrictions
        fields = ['id','day']
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

class AvailDateRestrictionsSerializers(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()
    
    
    
    def get_address(self, obj):
        try:
            address = BusinessAddress.objects.get(id =obj.business_address)
            return LocationSerializer(address).data
        except Exception as err:
            pass
    class Meta:
        model = DateRestrictions
        fields = ['id','start_date','end_date']

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


class FreeServiceSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    priceservice = serializers.SerializerMethodField(read_only=True)
    
    def get_priceservice(self, obj):
        try:
            ser = PriceService.objects.filter(service = obj.service)
            return PriceServiceSerializers(ser, many = True).data
        except Exception as err:
            return str(err)
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    class Meta:
        model = FreeService
        fields = '__all__'
class ProductAndGetSpecificSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    class Meta:
        model = ProductAndGetSpecific
        fields = '__all__'
class DiscountOnFreeServiceSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    class Meta:
        model = DiscountOnFreeService
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


class SpecificGroupDiscountSerializers(serializers.ModelSerializer):
    servicegroup_discount = serializers.SerializerMethodField(read_only=True)
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
        return 'Specific Group Discount'
    
    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(specificgroupdiscount = obj)
            return BlockDateSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(specificgroupdiscount = obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    
    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(specificgroupdiscount = obj)
            return DayRestrictionsSerializers(ser, many = True).data
        except Exception as err:
            pass
        
    def get_servicegroup_discount(self, obj):
        try:
            ser = ServiceGroupDiscount.objects.filter(specificgroupdiscount = obj)
            return ServiceGroupDiscountSerializers(ser, many = True).data
        except Exception as err:
            pass
    class Meta:
        model = SpecificGroupDiscount
        fields = '__all__'



class PurchaseDiscountSerializers(serializers.ModelSerializer):
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
        return 'Purchase Discount'
    
    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(purchasediscount = obj)
            return BlockDateSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(purchasediscount = obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    
    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(purchasediscount = obj)
            return DayRestrictionsSerializers(ser, many = True).data
        except Exception as err:
            pass
        
    class Meta:
        model = PurchaseDiscount
        fields = '__all__'

class AvailPurchaseDiscountSerializers(serializers.ModelSerializer):
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    discount_product = serializers.SerializerMethodField(read_only=True)
    discount_service = serializers.SerializerMethodField(read_only=True)
    
    def get_purchase_discount(self, obj):
        try:
            ser = PurchaseDiscount.objects.filter(purchasediscount = obj)
            return AvailPurchaseDiscountSerializers(ser, many = True).data
        except Exception as err:
            pass

    def get_discount_service(self, obj):
        try:
            ser = PurchaseDiscount.objects.filter(purchasediscount = obj)
            return AvailPurchaseDiscountSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    def get_type(self, obj):
        return 'Purchase Discount'
    
    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(purchasediscount = obj)
            return BlockDateSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(purchasediscount = obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    
    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(purchasediscount = obj)
            return DayRestrictionsSerializers(ser, many = True).data
        except Exception as err:
            pass
        
    class Meta:
        model = PurchaseDiscount
        fields = ['type','block_date','day_restrictions','date_restrictions','discount_product','discount_service']


class SpecificBrandSerializers(serializers.ModelSerializer):
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
        return 'Specific Brand Discount'
    
    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(specificbrand = obj)
            return BlockDateSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(specificbrand = obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    
    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(specificbrand = obj)
            return DayRestrictionsSerializers(ser, many = True).data
        except Exception as err:
            pass
    class Meta:
        model = SpecificBrand
        fields = '__all__'


class AvailSpecificBrandSerializers(serializers.ModelSerializer):
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    brand = serializers.SerializerMethodField(read_only=True)

    
    def get_type(self, obj):
        return 'Specific Brand Discount'
    
    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(specificbrand = obj)
            return BlockDateSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(specificbrand = obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    
    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(specificbrand = obj)
            return DayRestrictionsSerializers(ser, many = True).data
        except Exception as err:
            pass
    class Meta:
        model = SpecificBrand
        fields = ['id','type','brand','block_date','day_restrictions','date_restrictions']


class SpendDiscountSerializers(serializers.ModelSerializer):
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
        return 'Spend_Discount'
    
    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(specificbrand = obj)
            return BlockDateSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(specificbrand = obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    
    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(specificbrand = obj)
            return DayRestrictionsSerializers(ser, many = True).data
        except Exception as err:
            pass
    class Meta:
        model = SpendDiscount
        fields = '__all__'


class AvailSpendDiscountSerializers(serializers.ModelSerializer):
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    
    
    def get_type(self, obj):
        return 'Spend_Discount'
    
    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(specificbrand = obj)
            return BlockDateSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(specificbrand = obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    
    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(specificbrand = obj)
            return DayRestrictionsSerializers(ser, many = True).data
        except Exception as err:
            pass
    class Meta:
        model = SpendDiscount
        fields = ['type','day_restrictions','date_restrictions','block_date']


class SpendSomeAmountSerializers(serializers.ModelSerializer):
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    spend_service = serializers.SerializerMethodField(read_only=True)
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
        return 'Spend_Some_Amount'
    
    def get_spend_service(self, obj):
        try:
            ser = SpendSomeAmountAndGetDiscount.objects.filter(spandsomeamount = obj)
            return SpendSomeAmountAndGetDiscountSerializers(ser, many = True).data
        except Exception as err:
            return str(err)
            pass
        
    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(spendsomeamount = obj)
            return BlockDateSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(spendsomeamount = obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(spendsomeamount = obj)
            return DayRestrictionsSerializers(ser, many = True).data
        except Exception as err:
            pass
    class Meta:
        model = SpendSomeAmount
        fields = '__all__'


class FixedPriceServiceSerializers(serializers.ModelSerializer):
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    #spend_service = serializers.SerializerMethodField(read_only=True)
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
        return 'Fixed_Price_Service'
        
    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(fixedpriceservice = obj)
            return BlockDateSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(fixedpriceservice = obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(fixedpriceservice = obj)
            return DayRestrictionsSerializers(ser, many = True).data
        except Exception as err:
            pass
    class Meta:
        model = FixedPriceService
        fields = '__all__'

class AvailFixedPriceServiceSerializers(serializers.ModelSerializer):
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    #spend_service = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)
    # block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    # is_deleted = serializers.SerializerMethodField(read_only=True)

    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    
    def get_type(self, obj):
        return 'Fixed_Price_Service'
        
    class Meta:
        model = FixedPriceService
        fields = ['id','service']

class MentionedNumberServiceSerializers(serializers.ModelSerializer):
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    free_service = serializers.SerializerMethodField(read_only=True)
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
        return 'Mentioned_Number_Service'
        
    def get_free_service(self, obj):
        try:
            ser = FreeService.objects.filter(mentionnumberservice = obj)
            return FreeServiceSerializers(ser, many = True).data
        except Exception as err:
            return str(err)
            pass
        
    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(mentionednumberservice = obj)
            return BlockDateSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(mentionednumberservice = obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(mentionednumberservice = obj)
            return DayRestrictionsSerializers(ser, many = True).data
        except Exception as err:
            pass
    class Meta:
        model = MentionedNumberService
        fields = '__all__'
        


class BundleFixedSerializers(serializers.ModelSerializer):
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
        return 'Bundle_Fixed_Service'
        
    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(bundlefixed = obj)
            return BlockDateSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(bundlefixed = obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(bundlefixed = obj)
            return DayRestrictionsSerializers(ser, many = True).data
        except Exception as err:
            pass
    class Meta:
        model = BundleFixed
        fields = '__all__'
        
class AvailBundleFixedSerializers(serializers.ModelSerializer):
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)
    # block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    # is_deleted = serializers.SerializerMethodField(read_only=True)

    
    def get_type(self, obj):
        return 'Bundle_Fixed_Service'
        
    
    class Meta:
        model = BundleFixed
        fields = ['id','service']
        
# class AvailBundleFixedSerializers(serializers.ModelSerializer):
#     is_deleted = serializers.SerializerMethodField(read_only=True)

#     def get_is_deleted(self, obj):
#         if obj.is_deleted == True:
#             return 'True'
#         else:
#             return 'False'
    
#     class Meta:
#         model = BundleFixed
#         fields = ['id','service']
        
class RetailAndGetServiceSerializers(serializers.ModelSerializer):
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    promotion = serializers.SerializerMethodField(read_only=True)
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
        return 'Retail_and_Get_Service'
        
    def get_promotion(self, obj):
        try:
            ser = ProductAndGetSpecific.objects.filter(retailandservice = obj)
            return ProductAndGetSpecificSerializers(ser, many = True).data
        except Exception as err:
            return str(err)
            pass
        
    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(retailandservice = obj)
            return BlockDateSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(retailandservice = obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(retailandservice = obj)
            return DayRestrictionsSerializers(ser, many = True).data
        except Exception as err:
            pass
    class Meta:
        model = RetailAndGetService
        fields = '__all__'


class AvailRetailAndGetServiceSerializers(serializers.ModelSerializer):
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    promotion = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)
    # block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    # is_deleted = serializers.SerializerMethodField(read_only=True)

    # def get_is_deleted(self, obj):
    #     if obj.is_deleted == True:
    #         return 'True'
    #     else:
    #         return 'False'
    
    def get_type(self, obj):
        return 'Retail_and_Get_Service'
        
    def get_promotion(self, obj):
        try:
            ser = ProductAndGetSpecific.objects.filter(retailandservice = obj)
            return ProductAndGetSpecificSerializers(ser, many = True).data
        except Exception as err:
            return err
            pass
        
    # def get_block_date(self, obj):
    #     try:
    #         ser = BlockDate.objects.filter(retailandservice = obj)
    #         return BlockDateSerializers(ser, many = True).data
    #     except Exception as err:
    #         pass
    
    # def get_date_restrictions(self, obj):
    #     try:
    #         ser = DateRestrictions.objects.get(retailandservice = obj)
    #         return DateRestrictionsSerializers(ser).data
    #     except Exception as err:
    #         pass
   
    # def get_day_restrictions(self, obj):
    #     try:
    #         ser = DayRestrictions.objects.filter(retailandservice = obj)
    #         return DayRestrictionsSerializers(ser, many = True).data
    #     except Exception as err:
    #         pass
    class Meta:
        model = RetailAndGetService
        fields = ['id','promotion','type']


class UserRestrictedDiscountSerializers(serializers.ModelSerializer):
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
        return 'User_Restricted_discount'
        
    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(userrestricteddiscount = obj)
            return BlockDateSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(userrestricteddiscount = obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(userrestricteddiscount = obj)
            return DayRestrictionsSerializers(ser, many = True).data
        except Exception as err:
            pass
    class Meta:
        model = UserRestrictedDiscount
        fields = '__all__'
        

class AvailUserRestrictedDiscountSerializers(serializers.ModelSerializer):
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)
    # block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    # is_deleted = serializers.SerializerMethodField(read_only=True)

    # def get_is_deleted(self, obj):
    #     if obj.is_deleted == True:
    #         return 'True'
    #     else:
    #         return 'False'
    
    def get_type(self, obj):
        return 'User_Restricted_discount'
        
    # def get_block_date(self, obj):
    #     try:
    #         ser = BlockDate.objects.filter(userrestricteddiscount = obj)
    #         return BlockDateSerializers(ser, many = True).data
    #     except Exception as err:
    #         pass
    
    # def get_date_restrictions(self, obj):
    #     try:
    #         ser = DateRestrictions.objects.get(userrestricteddiscount = obj)
    #         return DateRestrictionsSerializers(ser).data
    #     except Exception as err:
    #         pass
   
    # def get_day_restrictions(self, obj):
    #     try:
    #         ser = DayRestrictions.objects.filter(userrestricteddiscount = obj)
    #         return DayRestrictionsSerializers(ser, many = True).data
    #     except Exception as err:
    #         pass
    class Meta:
        model = UserRestrictedDiscount
        fields = ['id','type','discount_percentage']
        

class ComplimentaryDiscountSerializers(serializers.ModelSerializer):
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    freeservice = serializers.SerializerMethodField(read_only=True)
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
        return 'Complimentary_Discount'
        
    def get_freeservice(self, obj):
        try:
            ser = DiscountOnFreeService.objects.filter(complimentary = obj)
            return DiscountOnFreeServiceSerializers(ser, many = True).data
        except Exception as err:
            return str(err)
            pass
        
    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(complimentary = obj)
            return BlockDateSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(complimentary = obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(complimentary = obj)
            return DayRestrictionsSerializers(ser, many = True).data
        except Exception as err:
            pass
    class Meta:
        model = ComplimentaryDiscount
        fields = '__all__'
        
class AvailComplimentaryDiscountSerializers(serializers.ModelSerializer):
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    service = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)
    # block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    # is_deleted = serializers.SerializerMethodField(read_only=True)

    # def get_is_deleted(self, obj):
    #     if obj.is_deleted == True:
    #         return 'True'
    #     else:
    #         return 'False'
    
    def get_type(self, obj):
        return 'Complimentary_Discount'
        
    def get_service(self, obj):
        try:
            ser = DiscountOnFreeService.objects.filter(complimentary = obj)
            return DiscountOnFreeServiceSerializers(ser, many = True).data
        except Exception as err:
            return err
            pass
        
    # def get_block_date(self, obj):
    #     try:
    #         ser = BlockDate.objects.filter(complimentary = obj)
    #         return BlockDateSerializers(ser, many = True).data
    #     except Exception as err:
    #         pass
    
    # def get_date_restrictions(self, obj):
    #     try:
    #         ser = DateRestrictions.objects.get(complimentary = obj)
    #         return DateRestrictionsSerializers(ser).data
    #     except Exception as err:
    #         pass
   
    # def get_day_restrictions(self, obj):
    #     try:
    #         ser = DayRestrictions.objects.filter(complimentary = obj)
    #         return DayRestrictionsSerializers(ser, many = True).data
    #     except Exception as err:
    #         pass
    class Meta:
        
        model = ComplimentaryDiscount
        fields = ['id','type','service']
        

class PackagesDiscountSerializers(serializers.ModelSerializer):
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    service_duration = serializers.SerializerMethodField(read_only=True)
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
        return 'Packages_Discount'
        
    def get_service_duration(self, obj):
        try:
            ser = ServiceDurationForSpecificTime.objects.filter(package = obj)
            return ServiceDurationForSpecificTimeSerializers(ser, many = True).data
        except Exception as err:
            return str(err)
            pass
        
    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(package = obj)
            return BlockDateSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(package = obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(package = obj)
            return DayRestrictionsSerializers(ser, many = True).data
        except Exception as err:
            pass
    class Meta:
        model = PackagesDiscount
        fields = '__all__'

#1
class AvailOfferPackagesDiscountSerializers(serializers.ModelSerializer):
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    service_duration = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)

    
    def get_type(self, obj):
        return 'Packages Discount'
        
    def get_service_duration(self, obj):
        try:
            ser = ServiceDurationForSpecificTime.objects.filter(package = obj)
            return AvailServiceDurationForSpecificTimeSerializers(ser, many = True).data
        except Exception as err:
            return str(err)
            pass
        
    def get_block_date(self, obj):
        ser = BlockDate.objects.filter(package = obj)
        return AvailBlockDateSerializers(ser, many = True).data

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(package = obj)
            return AvailDateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    def get_day_restrictions(self, obj):
        ser = DayRestrictions.objects.filter(package = obj)
        return AvailDayRestrictionsSerializers(ser, many = True).data
    class Meta:
        model = PackagesDiscount
        fields = ['type','block_date', 'service_duration' , 'date_restrictions' , 'day_restrictions']

#2
class AvailOfferComplimentaryDiscountSerializers(serializers.ModelSerializer):
    # services = serializers.SerializerMethodField(read_only=True)
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)
    
    def get_type(self, obj):
        return 'Complimentary Discount'
        
    # def get_services(self, obj):
    #     ser = ComplimentaryDiscount.objects.filter(complimentary = obj)
    #     return AvailComplimentaryDiscountSerializers(ser, many = True).data
        
    def get_block_date(self, obj):
        ser = BlockDate.objects.filter(complimentary = obj)
        return AvailBlockDateSerializers(ser, many = True).data
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(complimentary = obj)
            return AvailDateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    def get_day_restrictions(self, obj):
        ser = DayRestrictions.objects.filter(complimentary = obj)
        return AvailDayRestrictionsSerializers(ser, many = True).data

    class Meta:
        model = ComplimentaryDiscount
        fields = ['type','block_date', 'date_restrictions' , 'day_restrictions']
        # 'services' 

#3
class AvailOfferUserRestrictedDiscountSerializers(serializers.ModelSerializer):
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)

    def get_type(self, obj):
        return 'User Restricted discount'
        
    def get_block_date(self, obj):
        ser = BlockDate.objects.filter(userrestricteddiscount = obj)
        return AvailBlockDateSerializers(ser, many = True).data


    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(complimentary = obj)
            return AvailDateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    def get_day_restrictions(self, obj):
        ser = DayRestrictions.objects.filter(complimentary = obj)
        return AvailDayRestrictionsSerializers(ser, many = True).data

    class Meta:
        model = UserRestrictedDiscount
        fields = ['type','block_date','discount_percentage','date_restrictions','day_restrictions']

#4
class AvailOfferRetailAndGetServiceSerializers(serializers.ModelSerializer):
    # promotion = serializers.SerializerMethodField(read_only=True)
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)

    def get_type(self, obj):
        return 'Retail and Get Service'
        
    # def get_promotion(self, obj):
    #     ser = RetailAndGetService.objects.filter(retailandservice = obj)
    #     return AvailRetailAndGetServiceSerializers(ser, many = True).data
        
    def get_block_date(self, obj):
        ser = BlockDate.objects.filter(retailandservice = obj)
        return AvailBlockDateSerializers(ser, many = True).data


    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(retailandservice = obj)
            return AvailDateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    def get_day_restrictions(self, obj):
        ser = DayRestrictions.objects.filter(retailandservice = obj)
        return AvailDayRestrictionsSerializers(ser, many = True).data
    class Meta:
        model = RetailAndGetService
        fields = ['type','block_date', 'date_restrictions' , 'day_restrictions']
        # 'promotion' ,

#5
class AvailOfferBundleFixedSerializers(serializers.ModelSerializer):
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)
    # bundle_fixed = serializers.SerializerMethodField(read_only=True)
    
    def get_type(self, obj):
        return 'Bundle Fixed Service'

    
    # def get_bundle_fixed(self, obj):
    #     return {}
        
    
    def get_block_date(self, obj):
        ser = BlockDate.objects.filter(bundlefixed = obj)
        return AvailBlockDateSerializers(ser, many = True).data

        
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(bundlefixed = obj)
            return AvailDateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    def get_day_restrictions(self, obj):
        ser = DayRestrictions.objects.filter(bundlefixed = obj)
        return AvailDayRestrictionsSerializers(ser, many = True).data

    class Meta:
        model = BundleFixed
        fields = ['type','block_date' , 'date_restrictions' , 'day_restrictions']

#6
class AvailOfferFixedPriceServiceSerializers(serializers.ModelSerializer):
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)
    # duration = serializers.SerializerMethodField(read_only=True)
    
    # def get_duration(self, obj):
    #     try:
    #         ser = FixedPriceService.objects.filter(fixedpriceservice = obj)
    #         return AvailFixedPriceServiceSerializers(ser, many = True).data
    #     except Exception as err:
    #         pass


    def get_type(self, obj):
        return 'Fixed Price Service'
        
    def get_block_date(self, obj):
        ser = BlockDate.objects.filter(fixedpriceservice = obj)
        return AvailBlockDateSerializers(ser, many = True).data


    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(fixedpriceservice = obj)
            return AvailDateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    def get_day_restrictions(self, obj):
        ser = DayRestrictions.objects.filter(fixedpriceservice = obj)
        return AvailDayRestrictionsSerializers(ser, many = True).data
    class Meta:
        model = FixedPriceService
        fields = ['type','block_date' , 'date_restrictions' , 'day_restrictions']

class FreeServiceSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    priceservice = serializers.SerializerMethodField(read_only=True)
    
    def get_priceservice(self, obj):
        try:
            ser = PriceService.objects.filter(service = obj.service)
            return PriceServiceSerializers(ser, many = True).data
        except Exception as err:
            return str(err)
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    class Meta:
        model = FreeService
        fields = ['discount','priceservice']

class AvailServiceSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    priceservice = serializers.SerializerMethodField(read_only=True)
    
    def get_priceservice(self, obj):
        try:
            ser = PriceService.objects.filter(service = obj.service)
            return AvailPriceServiceSerializers(ser, many = True).data
        except Exception as err:
            return str(err)
    
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'
    class Meta:
        model = FreeService
        fields = ['discount','priceservice']

#7
class AvailOfferMentionedNumberServiceSerializers(serializers.ModelSerializer):
    # service = serializers.SerializerMethodField(read_only=True)
    services = serializers.SerializerMethodField(read_only=True)
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)

    
    def get_type(self, obj):
        return 'Mentioned Number Service'
        
    # def get_free_services(self, obj):
    #     try:
    #         ser = FreeService.objects.filter(mentionnumberservice = obj)
    #         return AvailFreeServiceSerializers(ser, many = True).data
    #     except Exception as err:
    #         return err
    #         pass
    
    def get_services(self, obj):
        ser = Service.objects.filter(service_mentionednumberservice__id = obj.id)
        return AvailServiceSerializers(ser, many = True).data
        
    def get_block_date(self, obj):
        ser = BlockDate.objects.filter(mentionednumberservice = obj)
        return AvailBlockDateSerializers(ser, many = True).data


    def get_date_restrictions(self, obj):
        ser = DateRestrictions.objects.get(mentionednumberservice = obj)
        return AvailDateRestrictionsSerializers(ser).data

    def get_day_restrictions(self, obj):
        ser = DayRestrictions.objects.filter(mentionednumberservice = obj)
        return AvailDayRestrictionsSerializers(ser, many = True).data

    class Meta:
        model = MentionedNumberService
        fields = ['type','block_date','services' , 'date_restrictions' , 'day_restrictions']

#8
class AvailOfferSpendSomeAmountSerializers(serializers.ModelSerializer):
    spend_service = serializers.SerializerMethodField(read_only=True)
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)

    
    def get_type(self, obj):
        return 'Spend Some Amount'
    
    def get_spend_service(self, obj):
        ser = SpendSomeAmount.objects.filter(spandsomeamount = obj)
        return AvailSpendSomeAmountAndGetDiscountSerializers(ser, many = True).data
    
    def get_block_date(self, obj):
        ser = BlockDate.objects.filter(spendsomeamount = obj)
        return AvailBlockDateSerializers(ser, many = True).data

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(spendsomeamount = obj)
            return AvailDateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    def get_day_restrictions(self, obj):
        ser = DayRestrictions.objects.filter(spendsomeamount = obj)
        return AvailDayRestrictionsSerializers(ser, many = True).data
    class Meta:
        model = SpendSomeAmount
        fields = ['type','block_date' ,'spend_service', 'date_restrictions' , 'day_restrictions']

#9
class AvailOfferSpendDiscountSerializers(serializers.ModelSerializer):
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)
    spend_discount =  serializers.SerializerMethodField(read_only=True)

    def get_type(self, obj):
        return 'Spend Discount'
    
    def get_spend_discount(self, obj):
        ser = SpendDiscount.objects.filter(specificbrand = obj)
        return AvailSpendDiscountSerializers(ser, many = True).data

    def get_block_date(self, obj):
        ser = BlockDate.objects.filter(specificbrand = obj)
        return AvailBlockDateSerializers(ser, many = True).data

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(specificbrand = obj)
            return AvailDateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
    
    def get_day_restrictions(self, obj):
        ser = DayRestrictions.objects.filter(specificbrand = obj)
        return AvailDayRestrictionsSerializers(ser, many = True).data
        
    class Meta:
        model = SpendDiscount
        fields = ['spend_discount','discount_service','discount_product','discount_value','type','block_date' , 'date_restrictions' , 'day_restrictions']
        
#10
class AvailCategoryDiscountSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = CategoryDiscount
        fields = ['category_type','discount']

class AvailOfferDirectOrFlatDiscountSerializers(serializers.ModelSerializer):
    category_discount = serializers.SerializerMethodField(read_only=True)
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)
    
    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'

    def get_type(self, obj):
        return 'Direct Or Flat Discount'
    
    def get_block_date(self, obj):
        ser = BlockDate.objects.filter(directorflat = obj)
        return AvailBlockDateSerializers(ser, many = True).data
        
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(directorflat = obj)
            return AvailDateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    
    def get_day_restrictions(self, obj):
        ser = DayRestrictions.objects.filter(directorflat = obj)
        return AvailDayRestrictionsSerializers(ser, many = True).data

    def get_category_discount(self, obj):
        ser = CategoryDiscount.objects.filter(directorflat = obj)
        return AvailCategoryDiscountSerializers(ser, many = True).data


    class Meta:
        model = DirectOrFlatDiscount
        fields = ['type','category_discount','day_restrictions','date_restrictions','block_date']

#11
class AvailOfferSpecificGroupDiscountSerializers(serializers.ModelSerializer):
    servicegroup_discount = serializers.SerializerMethodField(read_only=True)
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)
    
    def get_type(self, obj):
        return 'Specific Group Discount'
    
    def get_block_date(self, obj):
        ser = BlockDate.objects.filter(specificgroupdiscount = obj)
        return AvailBlockDateSerializers(ser, many = True).data


    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(specificgroupdiscount = obj)
            return AvailDateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    
    def get_day_restrictions(self, obj):
        ser = DayRestrictions.objects.filter(specificgroupdiscount = obj)
        return AvailDayRestrictionsSerializers(ser, many = True).data
    
    def get_servicegroup_discount(self, obj):
        ser = ServiceGroupDiscount.objects.filter(specificgroupdiscount = obj)
        return AvailServiceGroupDiscountSerializers(ser, many = True).data


    class Meta:
        model = SpecificGroupDiscount
        fields = ['type','servicegroup_discount','day_restrictions','date_restrictions','block_date']

#12
class AvailOfferPurchaseDiscountSerializers(serializers.ModelSerializer):
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)
    discount_product = serializers.SerializerMethodField(read_only=True)
    discount_service = serializers.SerializerMethodField(read_only=True)

    def get_type(self, obj):
        return 'Purchase Discount'
    
    def get_discount_product(self, obj):
        try:
            ser = PurchaseDiscount.objects.filter(purchasediscount = obj)
            return AvailPurchaseDiscountSerializers(ser, many = True).data
        except Exception as err:
            pass

    def get_discount_service(self, obj):
        try:
            ser = PurchaseDiscount.objects.filter(purchasediscount = obj)
            return AvailPurchaseDiscountSerializers(ser, many = True).data
        except Exception as err:
            pass

    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(purchasediscount = obj)
            return AvailBlockDateSerializers(ser, many = True).data
        except Exception as err:
            pass
    
    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(purchasediscount = obj)
            return AvailDateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
   
    
    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(purchasediscount = obj)
            return AvailDayRestrictionsSerializers(ser, many = True).data
        except Exception as err:
            pass
    class Meta:
        model = PurchaseDiscount
        fields = ['type','block_date' ,'discount_product','discount_service', 'date_restrictions','day_restrictions']

#13
class AvailOfferSpecificBrandSerializers(serializers.ModelSerializer):
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)
    specific_brand = serializers.SerializerMethodField(read_only=True)
    
    def get_type(self, obj):
        return 'Specific Brand Discount'
    
    def get_specific_brand(self, obj):
        ser = SpecificBrand.objects.filter(specificgroupdiscount = obj)
        return AvailSpecificBrandSerializers(ser, many = True).data

    def get_block_date(self, obj):
        ser = BlockDate.objects.filter(specificbrand = obj)
        return AvailBlockDateSerializers(ser, many = True).data

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(specificbrand = obj)
            return AvailDateRestrictionsSerializers(ser).data
        except Exception as err:
            pass
    
    def get_day_restrictions(self, obj):
        ser = DayRestrictions.objects.filter(specificbrand = obj)
        return AvailDayRestrictionsSerializers(ser, many = True).data
    class Meta:
        model = SpecificBrand
        fields = ['id','type' ,'specific_brand','day_restrictions','date_restrictions','block_date']