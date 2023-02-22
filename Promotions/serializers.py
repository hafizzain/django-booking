from Sale.serializers import PriceServiceSerializers
from Service.models import PriceService
from rest_framework import serializers

from Business.models import BusinessAddress, BusinessTax
from Product.Constants.index import tenant_media_base_url
from django_tenants.utils import tenant_context

from Promotions.models import BundleFixed, ComplimentaryDiscount, DirectOrFlatDiscount , CategoryDiscount , DateRestrictions , DayRestrictions, BlockDate, DiscountOnFreeService, FixedPriceService, FreeService, MentionedNumberService, PackagesDiscount, ProductAndGetSpecific, PurchaseDiscount, RetailAndGetService, ServiceDurationForSpecificTime, ServiceGroupDiscount, SpecificBrand, SpecificGroupDiscount, SpendDiscount, SpendSomeAmount, SpendSomeAmountAndGetDiscount, UserRestrictedDiscount

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
class FreeServiceSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    priceservice = serializers.SerializerMethodField(read_only=True)
    
    def get_priceservice(self, obj):
        try:
            ser = PriceService.objects.filter(service = obj)
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
            return err
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
            return err
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
            return err
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
            return err
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