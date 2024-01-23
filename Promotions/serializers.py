from rest_framework.fields import empty

from Appointment.serializers import ClientSerializerresponse
from Sale.serializers import AvailPriceServiceSerializers, PriceServiceSerializers, ClientSerializer
from Service.models import PriceService
from rest_framework import serializers

from Business.models import BusinessAddress, BusinessTax, Business
from Product.Constants.index import tenant_media_base_url
from django_tenants.utils import tenant_context
from Product.models import Product, Brand
from Product.serializers import BrandSerializer
from Promotions.models import BundleFixed, ComplimentaryDiscount, DirectOrFlatDiscount, CategoryDiscount, \
    DateRestrictions, DayRestrictions, BlockDate, DiscountOnFreeService, FixedPriceService, FreeService, \
    MentionedNumberService, PackagesDiscount, ProductAndGetSpecific, PurchaseDiscount, RetailAndGetService, \
    ServiceDurationForSpecificTime, ServiceGroupDiscount, SpecificBrand, SpecificGroupDiscount, SpendDiscount, \
    SpendSomeAmount, SpendSomeAmountAndGetDiscount, UserRestrictedDiscount, Service, ServiceGroup, \
    PromotionExcludedItem, Coupon, CouponBlockDays, CouponBrand, CouponServiceGroup
from Client.models import Vouchers, Client

from Utility.models import Currency, ExceptionRecord


class ServiceGroupDiscountSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    brand = BrandSerializer(read_only=True)

    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'

    class Meta:
        model = ServiceGroupDiscount
        fields = '__all__'

    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)

        self.fields['brand'].context.update(self.context)


class AvailOfferServiceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceGroup
        fields = ['id', 'name', 'services']


class AvailOffer_PriceService_Serializers(serializers.ModelSerializer):
    # currency_name = serializers.SerializerMethodField(read_only=True)

    # def get_currency_name(self, obj):
    #     try:
    #         currency = Currency.objects.get(id  = obj.currency.id)
    #         return currency.code
    #     except Exception as err:
    #         return str(err)
    class Meta:
        model = PriceService
        fields = ['id', 'price', 'currency', 'duration']
        #  'currency_name',


class AvailOfferService_Serializer(serializers.ModelSerializer):
    prices = serializers.SerializerMethodField(read_only=True)

    def get_prices(self, service):
        request = self.context.get('request', None)
        if request is not None:
            location_id = request.GET.get('selected_location', None)
        else:
            location_id = None

        queries = {}
        if location_id is not None:
            try:
                location = BusinessAddress.objects.get(id=location_id)
            except:
                pass
            else:
                queries['currency'] = location.currency

        prices = PriceService.objects.filter(service=service, **queries).order_by('-created_at')

        return AvailOffer_PriceService_Serializers(prices, many=True).data

    class Meta:
        model = Service
        fields = ['id', 'name', 'arabic_name', 'slot_availible_for_online', 'prices', 'client_can_book']


class AvailOfferProduct_Serializer(serializers.ModelSerializer):
    prices = serializers.SerializerMethodField(read_only=True)

    def get_prices(self, service):
        request = self.context.get('request', None)
        if request is not None:
            location_id = request.GET.get('selected_location', None)
        else:
            location_id = None

        queries = {}
        if location_id is not None:
            try:
                location = BusinessAddress.objects.get(id=location_id)
            except:
                pass
            else:
                queries['currency'] = location.currency

        prices = PriceService.objects.filter(service=service, **queries).order_by('-created_at')

        return AvailOffer_PriceService_Serializers(prices, many=True).data

    class Meta:
        model = Product
        fields = ['id', 'name', 'arabic_name', 'slot_availible_for_online', 'prices', 'client_can_book']


class AvailServiceGroupDiscountSerializers(serializers.ModelSerializer):
    services = serializers.SerializerMethodField(read_only=True)
    group_name = serializers.SerializerMethodField(read_only=True)

    def get_services(self, service_grp_discount):
        services = service_grp_discount.servicegroup.services.all()
        serialized = AvailOfferService_Serializer(services, many=True, context=self.context)
        return serialized.data

    def get_group_name(self, service_grp_discount):
        group_name = service_grp_discount.servicegroup.name
        return str(group_name)

    # def get_is_deleted(self, obj):
    #     if obj.is_deleted == True:
    #         return 'True'
    #     else:
    #         return 'False'
    class Meta:
        model = ServiceGroupDiscount
        fields = ['group_name', 'services', 'discount']


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
    # is_deleted = serializers.SerializerMethodField(read_only=True)

    # def get_is_deleted(self, obj):
    #     if obj.is_deleted == True:
    #         return 'True'
    #     else:
    #         return 'False'
    class Meta:
        model = ServiceDurationForSpecificTime
        fields = ['service']


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
    # is_deleted = serializers.SerializerMethodField(read_only=True)

    # def get_is_deleted(self, obj):
    #     if obj.is_deleted == True:
    #         return 'True'
    #     else:
    #         return 'False'
    class Meta:
        model = SpendSomeAmountAndGetDiscount
        fields = ['spendandgetdiscount']


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
    # def get_is_deleted(self, obj):
    #     if obj.is_deleted == True:
    #         return 'True'
    #     else:
    #         return 'False'
    class Meta:
        model = BlockDate
        fields = ['date', 'id']


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
        fields = ['id', 'day', 'is_deleted']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        fields = ['id', 'address_name']


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
            address = BusinessAddress.objects.get(id=obj.business_address)
            return LocationSerializer(address).data
        except Exception as err:
            pass

    class Meta:
        model = DateRestrictions
        fields = '__all__'


class AvailDateRestrictionsSerializers(serializers.ModelSerializer):
    # address = serializers.SerializerMethodField()

    # def get_address(self, obj):
    #     try:
    #         address = BusinessAddress.objects.get(id =obj.business_address)
    #         return LocationSerializer(address).data
    #     except Exception as err:
    #         pass

    class Meta:
        model = DateRestrictions
        fields = ['id', 'start_date', 'end_date']


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
            address = BusinessAddress.objects.get(id=obj.business_address)
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
            ser = PriceService.objects.filter(service=obj.service).order_by('-created_at')
            return PriceServiceSerializers(ser, many=True).data
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
    brand = BrandSerializer()

    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'

    class Meta:
        model = ProductAndGetSpecific
        fields = '__all__'


class AvailProduct_Serializers(serializers.ModelSerializer):
    # prices = serializers.SerializerMethodField(read_only=True)

    # def get_prices(self, product):
    #     request = self.context.get('request', None)
    #     if request is not None:
    #         location_id = request.GET.get('selected_location', None)
    #     else:
    #         location_id = None

    #     queries = {}
    #     if location_id is not None:
    #         try:
    #             location = BusinessAddress.objects.get(id = location_id)
    #         except:
    #             pass
    #         else:
    #             queries['currency'] = location.currency

    #     prices = PriceService.objects.filter(product = product, **queries)

    #     return AvailOffer_PriceService_Serializers(prices, many = True).data
    class Meta:
        model = Product
        fields = ['id', 'cost_price', 'arabic_name']


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

    excluded_products = serializers.SerializerMethodField(read_only=True)
    excluded_services = serializers.SerializerMethodField(read_only=True)
    excluded_vouchers = serializers.SerializerMethodField(read_only=True)

    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'

    def get_type(self, obj):
        return 'Direct Or Flat'

    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(directorflat=obj)
            return BlockDateSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(directorflat=obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass

    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(directorflat=obj)
            return DayRestrictionsSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_category_discount(self, obj):
        try:
            ser = CategoryDiscount.objects.filter(directorflat=obj)
            return CategoryDiscountSerializers(ser, many=True).data
        except Exception as err:
            return []

    def get_excluded_products(self, obj):
        excluded_proms = PromotionExcludedItem.objects.filter(
            is_deleted=False,
            is_active=True,
            object_type='Direct Or Flat',
            object_id=f'{obj.id}',
            excluded_type='Product',
        ).values_list('excluded_id', flat=True)

        prods = Product.objects.filter(
            id__in=list(excluded_proms),
            # is_active = True,
            is_deleted=False
        ).values('id', 'name')

        return prods

    def get_excluded_services(self, obj):
        excluded_proms = PromotionExcludedItem.objects.filter(
            is_deleted=False,
            is_active=True,
            object_type='Direct Or Flat',
            object_id=f'{obj.id}',
            excluded_type='Service',
        ).values_list('excluded_id', flat=True)

        servs = Service.objects.filter(
            id__in=list(excluded_proms),
            # is_active = True,
            is_deleted=False
        ).values('id', 'name')

        return servs

    def get_excluded_vouchers(self, obj):
        excluded_proms = PromotionExcludedItem.objects.filter(
            is_deleted=False,
            is_active=True,
            object_type='Direct Or Flat',
            object_id=f'{obj.id}',
            excluded_type='Voucher',
        ).values_list('excluded_id', flat=True)

        vouchers = Vouchers.objects.filter(
            id__in=list(excluded_proms),
            is_active=True,
            is_deleted=False
        ).values('id', 'name')

        return vouchers

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

    excluded_products = serializers.SerializerMethodField(read_only=True)
    excluded_services = serializers.SerializerMethodField(read_only=True)
    excluded_vouchers = serializers.SerializerMethodField(read_only=True)

    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'

    def get_type(self, obj):
        return 'Specific Group Discount'

    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(specificgroupdiscount=obj)
            return BlockDateSerializers(ser, many=True).data
        except Exception as err:
            return []

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(specificgroupdiscount=obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass

    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(specificgroupdiscount=obj)
            return DayRestrictionsSerializers(ser, many=True).data
        except Exception as err:
            return []

    def get_servicegroup_discount(self, obj):
        try:
            ser = ServiceGroupDiscount.objects.filter(specificgroupdiscount=obj)
            return ServiceGroupDiscountSerializers(ser, many=True, context=self.context).data
        except Exception as err:
            return []

    def get_excluded_products(self, obj):
        try:
            excluded_proms = PromotionExcludedItem.objects.filter(
                is_deleted=False,
                is_active=True,
                object_type='Specific Group Discount',
                object_id=f'{obj.id}',
                excluded_type='Product',
            ).values_list('excluded_id', flat=True)

            prods = Product.objects.filter(
                id__in=list(excluded_proms),
                # is_active = True,
                is_deleted=False
            ).values('id', 'name')

            return list(prods)
        except Exception as err:
            return [{'error': str(err)}]

    def get_excluded_services(self, obj):
        try:
            excluded_proms = PromotionExcludedItem.objects.filter(
                is_deleted=False,
                is_active=True,
                object_type='Specific Group Discount',
                object_id=f'{obj.id}',
                excluded_type='Service',
            ).values_list('excluded_id', flat=True)

            servs = Service.objects.filter(
                id__in=list(excluded_proms),
                # is_active = True,
                is_deleted=False
            ).values('id', 'name')

            return list(servs)
        except Exception as err:
            return [{'error': str(err)}]

    def get_excluded_vouchers(self, obj):
        try:
            excluded_proms = PromotionExcludedItem.objects.filter(
                is_deleted=False,
                is_active=True,
                object_type='Specific Group Discount',
                object_id=f'{obj.id}',
                excluded_type='Voucher',
            ).values_list('excluded_id', flat=True)

            vouchers = Vouchers.objects.filter(
                id__in=list(excluded_proms),
                is_active=True,
                is_deleted=False
            ).values('id', 'name')

            return list(vouchers)
        except Exception as err:
            return [{'error': str(err)}]

    class Meta:
        model = SpecificGroupDiscount
        fields = '__all__'
        # ['id', 'promotion_name', 'is_deleted', 'is_active', 'created_at', 'servicegroup_discount']
        # day_restrictions
        # date_restrictions
        # block_date
        # item_type

        # excluded_products
        # excluded_services
        # excluded_vouchers


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
            ser = BlockDate.objects.filter(purchasediscount=obj)
            return BlockDateSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(purchasediscount=obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass

    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(purchasediscount=obj)
            return DayRestrictionsSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    class Meta:
        model = PurchaseDiscount
        fields = '__all__'


class AvailPurchaseDiscountSerializers(serializers.ModelSerializer):
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)
    # block_date = serializers.SerializerMethodField(read_only=True)
    # type = serializers.SerializerMethodField(read_only=True)
    discount_product = serializers.SerializerMethodField(read_only=True)
    discount_service = serializers.SerializerMethodField(read_only=True)

    def get_discount_product(self, obj):
        try:
            ser = PurchaseDiscount.objects.filter(purchase_discount=obj)
            return AvailPurchaseDiscountSerializers(ser, many=True).data
        except Exception as err:
            pass

    def get_discount_service(self, obj):
        try:
            ser = PurchaseDiscount.objects.filter(purchase_discount=obj)
            return AvailPurchaseDiscountSerializers(ser, many=True).data
        except Exception as err:
            pass

    # def get_type(self, obj):
    #     return 'Purchase Discount'

    # def get_block_date(self, obj):
    #     try:
    #         ser = BlockDate.objects.filter(purchasediscount = obj)
    #         return BlockDateSerializers(ser, many = True).data
    #     except Exception as err:
    #         pass

    # def get_date_restrictions(self, obj):
    #     try:
    #         ser = DateRestrictions.objects.get(purchasediscount = obj)
    #         return DateRestrictionsSerializers(ser).data
    #     except Exception as err:
    #         pass

    # def get_day_restrictions(self, obj):
    #     try:
    #         ser = DayRestrictions.objects.filter(purchasediscount = obj)
    #         return DayRestrictionsSerializers(ser, many = True).data
    #     except Exception as err:
    #         pass

    class Meta:
        model = PurchaseDiscount
        fields = ['discount_product', 'discount_service']


# 'type','block_date','day_restrictions','date_restrictions',

class SpecificBrandSerializers(serializers.ModelSerializer):
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    is_deleted = serializers.SerializerMethodField(read_only=True)

    excluded_products = serializers.SerializerMethodField(read_only=True)
    excluded_services = serializers.SerializerMethodField(read_only=True)
    excluded_vouchers = serializers.SerializerMethodField(read_only=True)

    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'

    def get_type(self, obj):
        return 'Specific Brand Discount'

    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(specificbrand=obj)
            return BlockDateSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(specificbrand=obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass

    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(specificbrand=obj)
            return DayRestrictionsSerializers(ser, many=True).data
        except Exception as err:
            return []

    def get_excluded_products(self, obj):
        excluded_proms = PromotionExcludedItem.objects.filter(
            is_deleted=False,
            is_active=True,
            object_type='Specific Brand Discount',
            object_id=f'{obj.id}',
            excluded_type='Product',
        ).values_list('excluded_id', flat=True)

        prods = Product.objects.filter(
            id__in=list(excluded_proms),
            # is_active = True,
            is_deleted=False
        ).values('id', 'name')

        return prods

    def get_excluded_services(self, obj):
        excluded_proms = PromotionExcludedItem.objects.filter(
            is_deleted=False,
            is_active=True,
            object_type='Specific Brand Discount',
            object_id=f'{obj.id}',
            excluded_type='Service',
        ).values_list('excluded_id', flat=True)

        servs = Service.objects.filter(
            id__in=list(excluded_proms),
            # is_active = True,
            is_deleted=False
        ).values('id', 'name')

        return servs

    def get_excluded_vouchers(self, obj):
        excluded_proms = PromotionExcludedItem.objects.filter(
            is_deleted=False,
            is_active=True,
            object_type='Specific Brand Discount',
            object_id=f'{obj.id}',
            excluded_type='Voucher',
        ).values_list('excluded_id', flat=True)

        vouchers = Vouchers.objects.filter(
            id__in=list(excluded_proms),
            is_active=True,
            is_deleted=False
        ).values('id', 'name')

        return vouchers

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
            ser = BlockDate.objects.filter(specificbrand=obj)
            return BlockDateSerializers(ser, many=True).data
        except Exception as err:
            pass

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(specificbrand=obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass

    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(specificbrand=obj)
            return DayRestrictionsSerializers(ser, many=True).data
        except Exception as err:
            pass

    class Meta:
        model = SpecificBrand
        fields = ['id', 'type', 'brand', 'block_date', 'day_restrictions', 'date_restrictions']


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
            ser = BlockDate.objects.filter(specificbrand=obj)
            return BlockDateSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(specificbrand=obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass

    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(specificbrand=obj)
            return DayRestrictionsSerializers(ser, many=True).data
        except Exception as err:
            return []
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
            ser = BlockDate.objects.filter(specificbrand=obj)
            return BlockDateSerializers(ser, many=True).data
        except Exception as err:
            pass

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(specificbrand=obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass

    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(specificbrand=obj)
            return DayRestrictionsSerializers(ser, many=True).data
        except Exception as err:
            pass

    class Meta:
        model = SpendDiscount
        fields = ['type', 'day_restrictions', 'date_restrictions', 'block_date']


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
            ser = SpendSomeAmountAndGetDiscount.objects.filter(spandsomeamount=obj)
            return SpendSomeAmountAndGetDiscountSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(spendsomeamount=obj)
            return BlockDateSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(spendsomeamount=obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass

    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(spendsomeamount=obj)
            return DayRestrictionsSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    class Meta:
        model = SpendSomeAmount
        fields = '__all__'


class FixedPriceServiceSerializers(serializers.ModelSerializer):
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    # spend_service = serializers.SerializerMethodField(read_only=True)
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
            ser = BlockDate.objects.filter(fixedpriceservice=obj)
            return BlockDateSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(fixedpriceservice=obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass

    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(fixedpriceservice=obj)
            return DayRestrictionsSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    class Meta:
        model = FixedPriceService
        fields = '__all__'


class AvailFixedPriceServiceSerializers(serializers.ModelSerializer):
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    spend_services = serializers.SerializerMethodField(read_only=True)

    # date_restrictions = serializers.SerializerMethodField(read_only=True)
    # block_date = serializers.SerializerMethodField(read_only=True)
    # type = serializers.SerializerMethodField(read_only=True)
    # is_deleted = serializers.SerializerMethodField(read_only=True)

    # def get_is_deleted(self, obj):
    #     if obj.is_deleted == True:
    #         return 'True'
    #     else:
    #         return 'False'

    def get_spend_services(self, obj):
        return {}

    class Meta:
        model = FixedPriceService
        fields = ['spend_services']


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
            ser = FreeService.objects.filter(mentionnumberservice=obj)
            return FreeServiceSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(mentionednumberservice=obj)
            return BlockDateSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(mentionednumberservice=obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass

    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(mentionednumberservice=obj)
            return DayRestrictionsSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    class Meta:
        model = MentionedNumberService
        fields = '__all__'


class AvailMentionedNumberServiceSerializers(serializers.ModelSerializer):
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    free_service = serializers.SerializerMethodField(read_only=True)

    # date_restrictions = serializers.SerializerMethodField(read_only=True)
    # block_date = serializers.SerializerMethodField(read_only=True)
    # type = serializers.SerializerMethodField(read_only=True)
    # is_deleted = serializers.SerializerMethodField(read_only=True)

    # def get_is_deleted(self, obj):
    #     if obj.is_deleted == True:
    #         return 'True'
    #     else:
    #         return 'False'

    # def get_type(self, obj):
    #     return 'Mentioned_Number_Service'

    def get_free_service(self, obj):
        try:
            ser = FreeService.objects.filter(mentionnumberservice=obj)
            return AvailFreeServiceSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    # def get_block_date(self, obj):
    #     try:
    #         ser = BlockDate.objects.filter(mentionednumberservice = obj)
    #         return BlockDateSerializers(ser, many = True).data
    #     except Exception as err:
    #         return []
    #         pass

    # def get_date_restrictions(self, obj):
    #     try:
    #         ser = DateRestrictions.objects.get(mentionednumberservice = obj)
    #         return DateRestrictionsSerializers(ser).data
    #     except Exception as err:
    #         pass

    # def get_day_restrictions(self, obj):
    #     try:
    #         ser = DayRestrictions.objects.filter(mentionednumberservice = obj)
    #         return DayRestrictionsSerializers(ser, many = True).data
    #     except Exception as err:
    #         return []
    #         pass
    class Meta:
        model = MentionedNumberService
        fields = 'free_service'


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
            ser = BlockDate.objects.filter(bundlefixed=obj)
            return BlockDateSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(bundlefixed=obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass

    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(bundlefixed=obj)
            return DayRestrictionsSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    class Meta:
        model = BundleFixed
        fields = '__all__'


class AvailBundleFixedSerializers(serializers.ModelSerializer):
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)
    # block_date = serializers.SerializerMethodField(read_only=True)
    # type = serializers.SerializerMethodField(read_only=True)
    # is_deleted = serializers.SerializerMethodField(read_only=True)

    # def get_type(self, obj):
    #     return 'Bundle_Fixed_Service'

    class Meta:
        model = BundleFixed
        fields = ['id', 'service']


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
            ser = ProductAndGetSpecific.objects.filter(retailandservice=obj)
            return ProductAndGetSpecificSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(retailandservice=obj)
            return BlockDateSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(retailandservice=obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass

    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(retailandservice=obj)
            return DayRestrictionsSerializers(ser, many=True).data
        except Exception as err:
            return []
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
            ser = ProductAndGetSpecific.objects.filter(retailandservice=obj)
            return ProductAndGetSpecificSerializers(ser, many=True).data
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
        fields = ['id', 'promotion', 'type']


class UserRestrictedDiscountSerializers(serializers.ModelSerializer):
    day_restrictions = serializers.SerializerMethodField(read_only=True)
    date_restrictions = serializers.SerializerMethodField(read_only=True)
    block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    is_deleted = serializers.SerializerMethodField(read_only=True)

    excluded_products = serializers.SerializerMethodField(read_only=True)
    excluded_services = serializers.SerializerMethodField(read_only=True)
    excluded_vouchers = serializers.SerializerMethodField(read_only=True)

    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'

    def get_type(self, obj):
        return 'User_Restricted_discount'

    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(userrestricteddiscount=obj)
            return BlockDateSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(userrestricteddiscount=obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass

    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(userrestricteddiscount=obj)
            return DayRestrictionsSerializers(ser, many=True).data
        except Exception as err:
            return []

    def get_excluded_products(self, obj):
        excluded_proms = PromotionExcludedItem.objects.filter(
            is_deleted=False,
            is_active=True,
            object_type='User_Restricted_discount',
            object_id=f'{obj.id}',
            excluded_type='Product',
        ).values_list('excluded_id', flat=True)

        prods = Product.objects.filter(
            id__in=list(excluded_proms),
            # is_active = True,
            is_deleted=False
        ).values('id', 'name')

        return prods

    def get_excluded_services(self, obj):
        excluded_proms = PromotionExcludedItem.objects.filter(
            is_deleted=False,
            is_active=True,
            object_type='User_Restricted_discount',
            object_id=f'{obj.id}',
            excluded_type='Service',
        ).values_list('excluded_id', flat=True)

        servs = Service.objects.filter(
            id__in=list(excluded_proms),
            # is_active = True,
            is_deleted=False
        ).values('id', 'name')

        return servs

    def get_excluded_vouchers(self, obj):
        excluded_proms = PromotionExcludedItem.objects.filter(
            is_deleted=False,
            is_active=True,
            object_type='User_Restricted_discount',
            object_id=f'{obj.id}',
            excluded_type='Voucher',
        ).values_list('excluded_id', flat=True)

        vouchers = Vouchers.objects.filter(
            id__in=list(excluded_proms),
            is_active=True,
            is_deleted=False
        ).values('id', 'name')

        return vouchers

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
        fields = ['id', 'type', 'discount_percentage']


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
            ser = DiscountOnFreeService.objects.filter(complimentary=obj)
            return DiscountOnFreeServiceSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(complimentary=obj)
            return BlockDateSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(complimentary=obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass

    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(complimentary=obj)
            return DayRestrictionsSerializers(ser, many=True).data
        except Exception as err:
            return []
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
            ser = DiscountOnFreeService.objects.filter(complimentary=obj)
            return DiscountOnFreeServiceSerializers(ser, many=True).data
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
        fields = ['id', 'type', 'service']


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
            ser = ServiceDurationForSpecificTime.objects.filter(package=obj)
            return ServiceDurationForSpecificTimeSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_block_date(self, obj):
        try:
            ser = BlockDate.objects.filter(package=obj)
            return BlockDateSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    def get_date_restrictions(self, obj):
        try:
            ser = DateRestrictions.objects.get(package=obj)
            return DateRestrictionsSerializers(ser).data
        except Exception as err:
            pass

    def get_day_restrictions(self, obj):
        try:
            ser = DayRestrictions.objects.filter(package=obj)
            return DayRestrictionsSerializers(ser, many=True).data
        except Exception as err:
            return []
            pass

    class Meta:
        model = PackagesDiscount
        fields = '__all__'


# 1
class AvailOfferPackagesDiscountSerializers(serializers.ModelSerializer):
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    service_duration = serializers.SerializerMethodField(read_only=True)

    # date_restrictions = serializers.SerializerMethodField(read_only=True)
    # block_date = serializers.SerializerMethodField(read_only=True)
    # type = serializers.SerializerMethodField(read_only=True)

    # def get_type(self, obj):
    #     return 'Packages Discount'

    def get_service_duration(self, obj):
        return {}

    # def get_block_date(self, obj):
    #     ser = BlockDate.objects.filter(package = obj)
    #     return AvailBlockDateSerializers(ser, many = True).data

    # def get_date_restrictions(self, obj):
    #     try:
    #         ser = DateRestrictions.objects.get(package = obj)
    #         return AvailDateRestrictionsSerializers(ser).data
    #     except Exception as err:
    #         pass

    # def get_day_restrictions(self, obj):
    #     ser = DayRestrictions.objects.filter(package = obj)
    #     return AvailDayRestrictionsSerializers(ser, many = True).data
    class Meta:
        model = PackagesDiscount
        fields = ['id', 'service_duration']
        # 'block_date','date_restrictions' , 'day_restrictions'


# 2
class AvailOfferComplimentaryDiscountSerializers(serializers.ModelSerializer):
    services = serializers.SerializerMethodField(read_only=True)

    # block_date = serializers.SerializerMethodField(read_only=True)
    # type = serializers.SerializerMethodField(read_only=True)
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)

    def get_services(self, obj):
        return {}

    # def get_block_date(self, obj):
    #     ser = BlockDate.objects.filter(complimentary = obj)
    #     return AvailBlockDateSerializers(ser, many = True).data

    # def get_date_restrictions(self, obj):
    #     try:
    #         ser = DateRestrictions.objects.get(complimentary = obj)
    #         return AvailDateRestrictionsSerializers(ser).data
    #     except Exception as err:
    #         pass

    # def get_day_restrictions(self, obj):
    #     ser = DayRestrictions.objects.filter(complimentary = obj)
    #     return AvailDayRestrictionsSerializers(ser, many = True).data

    class Meta:
        model = ComplimentaryDiscount
        fields = ['id', 'services']
        # 'block_date', 'date_restrictions' , 'day_restrictions'
        # 'services' 


# 3
class AvailOfferUserRestrictedDiscountSerializers(serializers.ModelSerializer):
    # block_date = serializers.SerializerMethodField(read_only=True)
    # type = serializers.SerializerMethodField(read_only=True)
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)
    discount_percentage = serializers.SerializerMethodField(read_only=True)

    # def get_type(self, obj):
    #     return 'User Restricted discount'

    def get_discount_percentage(self, obj):
        return {}

    # def get_block_date(self, obj):
    #     ser = BlockDate.objects.filter(userrestricteddiscount = obj)
    #     return AvailBlockDateSerializers(ser, many = True).data

    # def get_date_restrictions(self, obj):
    #     try:
    #         ser = DateRestrictions.objects.get(userrestricteddiscount = obj)
    #         return AvailDateRestrictionsSerializers(ser).data
    #     except Exception as err:
    #         pass

    # def get_day_restrictions(self, obj):
    #     ser = DayRestrictions.objects.filter(userrestricteddiscount = obj)
    #     return AvailDayRestrictionsSerializers(ser, many = True).data

    class Meta:
        model = UserRestrictedDiscount
        fields = ['id', 'discount_percentage']
        # 'block_date','date_restrictions','day_restrictions'


# 4
class AvailOfferRetailAndGetServiceSerializers(serializers.ModelSerializer):
    promotion = serializers.SerializerMethodField(read_only=True)

    # block_date = serializers.SerializerMethodField(read_only=True)
    # type = serializers.SerializerMethodField(read_only=True)
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)

    # def get_type(self, obj):
    #     return 'Retail and Get Service'

    # def get_block_date(self, obj):
    #     ser = BlockDate.objects.filter(retailandservice = obj)
    #     return AvailBlockDateSerializers(ser, many = True).data

    def get_promotion(self, obj):
        return {}

    # def get_date_restrictions(self, obj):
    #     try:
    #         ser = DateRestrictions.objects.get(retailandservice = obj)
    #         return AvailDateRestrictionsSerializers(ser).data
    #     except Exception as err:
    #         pass

    # def get_day_restrictions(self, obj):
    #     ser = DayRestrictions.objects.filter(retailandservice = obj)
    #     return AvailDayRestrictionsSerializers(ser, many = True).data
    class Meta:
        model = RetailAndGetService
        fields = ['id', 'promotion']
        # 'block_date', 'date_restrictions' , 'day_restrictions'
        # 'promotion' ,


# 5
class AvailOfferBundleFixedSerializers(serializers.ModelSerializer):
    # block_date = serializers.SerializerMethodField(read_only=True)
    # type = serializers.SerializerMethodField(read_only=True)
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)
    services = serializers.SerializerMethodField(read_only=True)

    # def get_type(self, obj):
    #     return 'Bundle Fixed Service'

    def get_services(self, obj):
        try:
            ser = BundleFixed.objects.filter(bundlefixed=obj.services)
            return AvailBundleFixedSerializers(ser, many=True).data
        except Exception as err:
            return str(err)

    # def get_block_date(self, obj):
    #     ser = BlockDate.objects.filter(bundlefixed = obj)
    #     return AvailBlockDateSerializers(ser, many = True).data

    # def get_date_restrictions(self, obj):
    #     try:
    #         ser = DateRestrictions.objects.get(bundlefixed = obj)
    #         return AvailDateRestrictionsSerializers(ser).data
    #     except Exception as err:
    #         pass

    # def get_day_restrictions(self, obj):
    #     ser = DayRestrictions.objects.filter(bundlefixed = obj)
    #     return AvailDayRestrictionsSerializers(ser, many = True).data

    class Meta:
        model = BundleFixed
        fields = ['id', 'services']
        # 'block_date' , 'date_restrictions' , 'day_restrictions'


# 6
class AvailOfferFixedPriceServiceSerializers(serializers.ModelSerializer):
    # block_date = serializers.SerializerMethodField(read_only=True)
    # type = serializers.SerializerMethodField(read_only=True)
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)
    services = serializers.SerializerMethodField(read_only=True)

    def get_services(self, obj):
        try:
            ser = FixedPriceService.objects.filter(fixedpriceservice=obj)
            return AvailFixedPriceServiceSerializers(ser, many=True).data
        except Exception as err:
            pass

    # def get_type(self, obj):
    #     return 'Fixed Price Service'

    # def get_block_date(self, obj):
    #     ser = BlockDate.objects.filter(fixedpriceservice = obj)
    #     return AvailBlockDateSerializers(ser, many = True).data

    # def get_date_restrictions(self, obj):
    #     try:
    #         ser = DateRestrictions.objects.get(fixedpriceservice = obj)
    #         return AvailDateRestrictionsSerializers(ser).data
    #     except Exception as err:
    #         pass

    # def get_day_restrictions(self, obj):
    #     ser = DayRestrictions.objects.filter(fixedpriceservice = obj)
    #     return AvailDayRestrictionsSerializers(ser, many = True).data
    class Meta:
        model = FixedPriceService
        fields = ['id', 'services']
        # 'block_date' , 'date_restrictions' , 'day_restrictions'


class AvailFreeServiceSerializers(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField(read_only=True)
    priceservice = serializers.SerializerMethodField(read_only=True)

    def get_priceservice(self, obj):
        try:
            ser = PriceService.objects.filter(service=obj.service).order_by('-created_at')
            return PriceServiceSerializers(ser, many=True).data
        except Exception as err:
            return str(err)

    def get_is_deleted(self, obj):
        if obj.is_deleted == True:
            return 'True'
        else:
            return 'False'

    class Meta:
        model = FreeService
        fields = ['discount', 'priceservice', 'is_deleted']


class AvailServiceSerializers(serializers.ModelSerializer):
    # is_deleted = serializers.SerializerMethodField(read_only=True)
    priceservice = serializers.SerializerMethodField(read_only=True)
    discount = serializers.SerializerMethodField(read_only=True)

    def get_priceservice(self, obj):
        try:
            ser = PriceService.objects.filter(service=obj.service).order_by('-created_at')
            return AvailPriceServiceSerializers(ser, many=True).data
        except Exception as err:
            return str(err)

    # def get_is_deleted(self, obj):
    #     if obj.is_deleted == True:
    #         return 'True'
    #     else:
    #         return 'False'

    def get_discount(self, obj):
        return None

    class Meta:
        model = FreeService
        fields = ['discount', 'priceservice']


# 7
class AvailOfferMentionedNumberServiceSerializers(serializers.ModelSerializer):
    # service = serializers.SerializerMethodField(read_only=True)
    services = serializers.SerializerMethodField(read_only=True)

    # block_date = serializers.SerializerMethodField(read_only=True)
    # type = serializers.SerializerMethodField(read_only=True)
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)

    # def get_type(self, obj):
    #     return 'Mentioned Number Service'

    # def get_free_services(self, obj):
    #     try:
    #         ser = FreeService.objects.filter(mentionnumberservice = obj)
    #         return AvailFreeServiceSerializers(ser, many = True).data
    #     except Exception as err:
    #         return err
    #         pass

    def get_services(self, obj):
        try:
            ser = MentionedNumberService.objects.filter(mentionednumberservice=obj.service)
            return MentionedNumberServiceSerializers(ser, many=True).data
        except Exception as err:
            return str(err)

    # def get_block_date(self, obj):
    #     ser = BlockDate.objects.filter(mentionednumberservice = obj)
    #     return AvailBlockDateSerializers(ser, many = True).data

    # def get_date_restrictions(self, obj):
    #     ser = DateRestrictions.objects.get(mentionednumberservice = obj)
    #     return AvailDateRestrictionsSerializers(ser).data

    # def get_day_restrictions(self, obj):
    #     ser = DayRestrictions.objects.filter(mentionednumberservice = obj)
    #     return AvailDayRestrictionsSerializers(ser, many = True).data

    class Meta:
        model = MentionedNumberService
        fields = ['id', 'services']
        # 'block_date','date_restrictions' , 'day_restrictions'


# 8
class AvailOfferSpendSomeAmountSerializers(serializers.ModelSerializer):
    business = serializers.SerializerMethodField(read_only=True)

    # block_date = serializers.SerializerMethodField(read_only=True)
    # type = serializers.SerializerMethodField(read_only=True)
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)

    # def get_type(self, obj):
    #     return 'Spend Some Amount'

    def get_business(self, obj):
        ser = SpendSomeAmount.objects.filter(spandsomeamount=obj)
        return AvailSpendSomeAmountAndGetDiscountSerializers(ser, many=True).data

    # def get_block_date(self, obj):
    #     ser = BlockDate.objects.filter(spendsomeamount = obj)
    #     return AvailBlockDateSerializers(ser, many = True).data

    # def get_date_restrictions(self, obj):
    #     try:
    #         ser = DateRestrictions.objects.get(spendsomeamount = obj)
    #         return AvailDateRestrictionsSerializers(ser).data
    #     except Exception as err:
    #         pass

    # def get_day_restrictions(self, obj):
    #     ser = DayRestrictions.objects.filter(spendsomeamount = obj)
    #     return AvailDayRestrictionsSerializers(ser, many = True).data
    class Meta:
        model = SpendSomeAmount
        fields = ['id', 'business']
        # 'block_date' ,'date_restrictions' , 'day_restrictions'
        # 'spend_service', 


# 9
class AvailOfferSpendDiscountSerializers(serializers.ModelSerializer):
    # block_date = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)

    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)
    # spend_discount =  serializers.SerializerMethodField(read_only=True)

    def get_type(self, obj):
        return 'Spend_Discount'

    # def get_spend_discount(self, obj):
    #     ser = SpendDiscount.objects.filter(specificbrand = obj)
    #     return AvailSpendDiscountSerializers(ser, many = True).data

    # def get_block_date(self, obj):
    #     ser = BlockDate.objects.filter(specificbrand = obj)
    #     return AvailBlockDateSerializers(ser, many = True).data

    # def get_date_restrictions(self, obj):
    #     try:
    #         ser = DateRestrictions.objects.get(specificbrand = obj)
    #         return AvailDateRestrictionsSerializers(ser).data
    #     except Exception as err:
    #         pass

    # def get_day_restrictions(self, obj):
    #     ser = DayRestrictions.objects.filter(specificbrand = obj)
    #     return AvailDayRestrictionsSerializers(ser, many = True).data

    class Meta:
        model = SpendDiscount
        fields = ['discount_service', 'discount_product', 'discount_value', 'type', ]
        # 'spend_discount', 'block_date' , 'date_restrictions' , 'day_restrictions'


# 10
class AvailCategoryDiscountSerializers(serializers.ModelSerializer):
    class Meta:
        model = CategoryDiscount
        fields = ['category_type', 'discount']


class AvailOfferDirectOrFlatDiscountSerializers(serializers.ModelSerializer):
    category_discount = serializers.SerializerMethodField(read_only=True)

    # block_date = serializers.SerializerMethodField(read_only=True)
    # type = serializers.SerializerMethodField(read_only=True)
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)

    # def get_is_deleted(self, obj):
    #     if obj.is_deleted == True:
    #         return 'True'
    #     else:
    #         return 'False'

    # def get_type(self, obj):
    #     return 'Direct Or Flat Discount'

    # def get_block_date(self, obj):
    #     ser = BlockDate.objects.filter(directorflat = obj)
    #     return AvailBlockDateSerializers(ser, many = True).data

    # def get_date_restrictions(self, obj):
    #     try:
    #         ser = DateRestrictions.objects.get(directorflat = obj)
    #         return AvailDateRestrictionsSerializers(ser).data
    #     except Exception as err:
    #         pass

    # def get_day_restrictions(self, obj):
    #     ser = DayRestrictions.objects.filter(directorflat = obj)
    #     return AvailDayRestrictionsSerializers(ser, many = True).data

    def get_category_discount(self, obj):
        ser = CategoryDiscount.objects.filter(directorflat=obj)
        return AvailCategoryDiscountSerializers(ser, many=True, context=self.context).data

    class Meta:
        model = DirectOrFlatDiscount
        fields = ['id', 'category_discount', ]
        # 'day_restrictions',
        # 'date_restrictions',
        # 'block_date',
        # 'type',


# 11
class AvailOfferSpecificGroupDiscountSerializers(serializers.ModelSerializer):
    servicegroup_discount = serializers.SerializerMethodField(read_only=True)

    # block_date = serializers.SerializerMethodField(read_only=True)
    # type = serializers.SerializerMethodField(read_only=True)
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)

    # def get_type(self, obj):
    #     return 'Specific Group Discount'

    # def get_block_date(self, obj):
    #     ser = BlockDate.objects.filter(specificgroupdiscount = obj)
    #     return AvailBlockDateSerializers(ser, many = True).data

    # def get_date_restrictions(self, obj):
    #     try:
    #         ser = DateRestrictions.objects.get(specificgroupdiscount = obj)
    #         return AvailDateRestrictionsSerializers(ser).data
    #     except Exception as err:
    #         pass

    # def get_day_restrictions(self, obj):
    #     ser = DayRestrictions.objects.filter(specificgroupdiscount = obj)
    #     return AvailDayRestrictionsSerializers(ser, many = True).data

    def get_servicegroup_discount(self, obj):
        ser = ServiceGroupDiscount.objects.filter(specificgroupdiscount=obj)
        return AvailServiceGroupDiscountSerializers(ser, many=True, context=self.context).data

    class Meta:
        model = SpecificGroupDiscount
        fields = ['id', 'servicegroup_discount', ]
        # 'day_restrictions','date_restrictions','block_date', 'type',


# 12
class AvailOfferPurchaseDiscountSerializers(serializers.ModelSerializer):
    # block_date = serializers.SerializerMethodField(read_only=True)
    # type = serializers.SerializerMethodField(read_only=True)
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)
    # product = AvailProductAndGetSpecificSerializers()
    # ": "b0315b17-df09-4101-b46a-b361c70d02ee
    service = AvailOfferService_Serializer()
    product = AvailProduct_Serializers()

    # def get_type(self, obj):
    #     return 'Purchase Discount'

    # def get_product(self, obj):
    #     try:
    #         ser = PurchaseDiscount.objects.filter(purchasediscount = obj)
    #         return AvailPurchaseDiscountSerializers(ser, many = True).data
    #     except Exception as err:
    #         pass

    # def get_service(self, obj):
    #     try:
    #         ser = PurchaseDiscount.objects.filter(purchasediscount = obj)
    #         return AvailPurchaseDiscountSerializers(ser, many = True).data
    #     except Exception as err:
    #         pass

    # def get_block_date(self, obj):
    #     try:
    #         ser = BlockDate.objects.filter(purchasediscount = obj)
    #         return AvailBlockDateSerializers(ser, many = True).data
    #     except Exception as err:
    #         pass

    # def get_date_restrictions(self, obj):
    #     try:
    #         ser = DateRestrictions.objects.get(purchasediscount = obj)
    #         return AvailDateRestrictionsSerializers(ser).data
    #     except Exception as err:
    #         pass

    # def get_day_restrictions(self, obj):
    #     try:
    #         ser = DayRestrictions.objects.filter(purchasediscount = obj)
    #         return AvailDayRestrictionsSerializers(ser, many = True).data
    #     except Exception as err:
    #         pass
    class Meta:
        model = PurchaseDiscount
        fields = ['id', 'product', 'service', ]
        # 'block_date' ,'date_restrictions','day_restrictions'


# 13
class AvailOfferSpecificBrandSerializers(serializers.ModelSerializer):
    # block_date = serializers.SerializerMethodField(read_only=True)
    # type = serializers.SerializerMethodField(read_only=True)
    # day_restrictions = serializers.SerializerMethodField(read_only=True)
    # date_restrictions = serializers.SerializerMethodField(read_only=True)
    service_group = serializers.SerializerMethodField(read_only=True)

    # def get_type(self, obj):
    #     return 'Specific Brand Discount'

    def get_service_group(self, obj):
        # ser = SpecificBrand.objects.filter(specificgroupdiscount = obj)
        # return AvailSpecificBrandSerializers(ser, many = True).data
        return {}

    # def get_block_date(self, obj):
    #     ser = BlockDate.objects.filter(specificbrand = obj)
    #     return AvailBlockDateSerializers(ser, many = True).data

    # def get_date_restrictions(self, obj):
    #     try:
    #         ser = DateRestrictions.objects.get(specificbrand = obj)
    #         return AvailDateRestrictionsSerializers(ser).data
    #     except Exception as err:
    #         pass

    # def get_day_restrictions(self, obj):
    #     ser = DayRestrictions.objects.filter(specificbrand = obj)
    #     return AvailDayRestrictionsSerializers(ser, many = True).data
    class Meta:
        model = SpecificBrand
        fields = ['id', 'service_group']
        # 'specific_brand', 'day_restrictions','date_restrictions','block_date'


class PromotionExcludedItemSerializer(serializers.ModelSerializer):
    excluded_item = serializers.SerializerMethodField(read_only=True)

    def get_excluded_item(self, obj):
        return obj.excluded_id

    class Meta:
        model = PromotionExcludedItem
        fields = ['id', 'excluded_item']


class CouponBrandresponse(serializers.ModelSerializer):
    class Meta:
        model = CouponBrand
        fields = "__all__"


class Clientcouponresponse(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class Brandcouponresponse(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


class Servicecouponresponse(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"


class ServiceGroupcouponresponse(serializers.ModelSerializer):
    class Meta:
        model = ServiceGroup
        fields = "__all__"


class CouponServiceGroupcouponserializerresponse(serializers.ModelSerializer):
    class Meta:
        model = CouponServiceGroup
        fields = "__all__"


class Productcouponresponse(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class CouponBlockDaysresponse(serializers.ModelSerializer):
    class Meta:
        model = CouponBlockDays
        fields = "__all__"


class Couponbusinessresponse(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = "__all__"


class BusinessAddressresponse(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        fields = "__all__"


class CouponSerializer(serializers.ModelSerializer):
    # clients = Clientcouponresponse(many=True)
    servicegroup_discount = serializers.SerializerMethodField(read_only=True)
    brands = Brandcouponresponse(many=True)
    # coupons_services = Servicecouponresponse(many=True)
    coupon_service_groups = ServiceGroupcouponresponse(many=True)
    # excluded_products = Productcouponresponse(many=True)
    coupon_blockdays = CouponBlockDaysresponse(many=True)
    business = Couponbusinessresponse(many=True)
    aval_coupon_brands = CouponBrandresponse(many=True)

    # locations = BusinessAddressresponse(many=True)

    def get_servicegroup_discount(self, obj):
        try:
            coupon_brand_queryset = CouponBrand.objects.filter(coupon=obj)
            brand_serializer = CouponBrandresponse(coupon_brand_queryset, many=True).data
            coupon_service_group_queryset = CouponServiceGroup.objects.filter(coupon=obj)
            coupon_service = CouponServiceGroupcouponserializerresponse(coupon_service_group_queryset, many=True).data

            return [{
                'id': obj.id,
                'brand': brand_serializer,
                'service_group': coupon_service,
            }]
        except Exception as err:
            err = str(err)
            return {err}

    class Meta:
        model = Coupon
        fields = ['id', 'name', 'buy_one_type', 'requested_status', 'status', 'code', 'short_description', 'start_date',
                  'end_date', 'coupon_type',
                  'user_limit', 'usage_limit', 'clients', 'brands', 'excluded_services', 'coupon_service_groups',
                  'client_type',
                  'locations', 'business', 'amount_spent', 'discounted_percentage', 'type', 'aval_coupon_brands',
                  'coupon_type_value',
                  'excluded_products', 'coupon_blockdays', 'buy_one_get_one_product', 'buy_one_get_one_service',
                  'servicegroup_discount'
                  ]
