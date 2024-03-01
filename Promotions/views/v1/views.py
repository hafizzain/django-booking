from datetime import datetime
import email
import sys
from django.conf import settings
from operator import ge
from django.utils import timezone
import Promotions.serializers as PromtoionsSerializers
# from Promotions.serializers import AvailOfferDirectOrFlatDiscountSerializers,AvailOfferSpecificGroupDiscountSerializers,AvailOfferPurchaseDiscountSerializers,AvailOfferSpecificBrandSerializers,AvailOfferSpendDiscountSerializers,AvailOfferSpendSomeAmountSerializers,AvailOfferFixedPriceServiceSerializers,AvailOfferMentionedNumberServiceSerializers,AvailOfferBundleFixedSerializers,AvailOfferRetailAndGetServiceSerializers,AvailOfferUserRestrictedDiscountSerializers,AvailOfferComplimentaryDiscountSerializers,AvailOfferPackagesDiscountSerializers,NewServiceSerializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Authentication.serializers import UserTenantLoginSerializer
from Business.models import BusinessAddressMedia, BusinessType
from Business.serializers.v1_serializers import EmployeTenatSerializer, OpeningHoursSerializer, \
    AdminNotificationSettingSerializer, BookingSettingSerializer, BusinessTypeSerializer, Business_GetSerializer, \
    Business_PutSerializer, BusinessAddress_GetSerializer, BusinessThemeSerializer, BusinessVendorSerializer, \
    ClientNotificationSettingSerializer, StaffNotificationSettingSerializer, StockNotificationSettingSerializer, \
    BusinessTaxSerializer, PaymentMethodSerializer
from Client.models import Client, Vouchers
from Employee.models import Employee

from NStyle.Constants import StatusCodes

from Appointment.models import AppointmentService
from Authentication.models import User
from Business.models import Business, BusinessSocial, BusinessAddress, BusinessOpeningHour, BusinessTheme, \
    StaffNotificationSetting, ClientNotificationSetting, AdminNotificationSetting, StockNotificationSetting, \
    BookingSetting, BusinessPaymentMethod, BusinessTax, BusinessVendor
from Product.models import Brand, Product, ProductStock
from Profile.models import UserLanguage
from Profile.serializers import UserLanguageSerializer
from Promotions.models import BlockDate, BundleFixed, CategoryDiscount, ComplimentaryDiscount, DateRestrictions, \
    DayRestrictions, DirectOrFlatDiscount, DiscountOnFreeService, FixedPriceService, FreeService, \
    MentionedNumberService, PackagesDiscount, ProductAndGetSpecific, PurchaseDiscount, RetailAndGetService, \
    ServiceDurationForSpecificTime, ServiceGroupDiscount, SpecificBrand, SpecificGroupDiscount, SpendDiscount, \
    SpendSomeAmount, SpendSomeAmountAndGetDiscount, UserRestrictedDiscount, PromotionExcludedItem, Coupon, \
    CouponDetails, CouponBlockDays, CouponBrand, CouponServiceGroup
from Promotions.serializers import BundleFixedSerializers, ComplimentaryDiscountSerializers, \
    DirectOrFlatDiscountSerializers, FixedPriceServiceSerializers, MentionedNumberServiceSerializers, \
    PackagesDiscountSerializers, PurchaseDiscountSerializers, RetailAndGetServiceSerializers, SpecificBrandSerializers, \
    SpecificGroupDiscountSerializers, SpendDiscountSerializers, SpendSomeAmountSerializers, \
    UserRestrictedDiscountSerializers, CouponSerializer
from Service.models import Service, ServiceGroup
from Tenants.models import Domain, Tenant
from Utility.models import Country, Currency, ExceptionRecord, Language, NstyleFile, Software, State, City
from Utility.serializers import LanguageSerializer
import json
from django.db.models import Q

from django_tenants.utils import tenant_context
from django.db import transaction
from Finance.models import RefundCoupon
from Finance.serializers import RefundCouponSerializer

@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_directorflat(request):
    user = request.user
    business_id = request.data.get('business', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    promotion_name = request.data.get('promotion_name', '')

    dayrestrictions = request.data.get('dayrestrictions', None)
    categorydiscount = request.data.get('categorydiscount', None)
    blockdate = request.data.get('blockdate', None)

    products = request.data.get('product', [])
    services = request.data.get('services', [])
    vouchers = request.data.get('voucher', [])

    error = []

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    flatordirect = DirectOrFlatDiscount.objects.create(
        user=user,
        business=business,
        promotion_name=promotion_name
    )
    date_res = DateRestrictions.objects.create(
        directorflat=flatordirect,
        start_date=start_date,
        end_date=end_date,
    )
    if location is not None:
        if type(location) == str:
            location = json.loads(location)

        elif type(location) == list:
            pass

        for loc in location:
            try:
                address = BusinessAddress.objects.get(id=loc)
                date_res.business_address.add(address)
            except Exception as err:
                error.append(str(err))

    if categorydiscount is not None:
        if type(categorydiscount) == str:
            categorydiscount = categorydiscount.replace("'", '"')
            categorydiscount = json.loads(categorydiscount)
        else:
            pass
        for cat in categorydiscount:
            try:
                category = cat.get('category', None)
                discount = cat.get('discount', None)

                category_discount = CategoryDiscount.objects.create(
                    directorflat=flatordirect,

                    category_type=category,
                    discount=discount,
                )

            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            try:
                day = dayres.get('day', None)

                DayRestrictions.objects.create(
                    directorflat=flatordirect,
                    day=day,
                )

            except Exception as err:
                error.append(str(err))

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:

            try:
                date = bl_date.get('date', None)
                BlockDate.objects.create(
                    directorflat=flatordirect,
                    date=date,
                )

            except Exception as err:
                error.append(str(err))

    if type(products) == str:
        try:
            products = json.loads(products)
        except:
            products = []

    if type(products) == list:
        for product_id in products:
            try:
                product_instance = Product.objects.get(id=product_id)
            except:
                pass
            else:
                PromotionExcludedItem.objects.create(
                    object_type='Direct Or Flat',
                    object_id=f'{flatordirect.id}',
                    excluded_type='Product',
                    excluded_id=f'{product_instance.id}',
                    is_active=True,
                )

    if type(services) == str:
        try:
            services = json.loads(services)
        except:
            services = []

    if type(services) == list:
        for service_id in services:
            try:
                service_instance = Service.objects.get(id=service_id)
            except:
                pass
            else:
                PromotionExcludedItem.objects.create(
                    object_type='Direct Or Flat',
                    object_id=f'{flatordirect.id}',
                    excluded_type='Service',
                    excluded_id=f'{service_instance.id}',
                    is_active=True,
                )

    if type(vouchers) == str:
        try:
            vouchers = json.loads(vouchers)
        except:
            vouchers = []

    if type(vouchers) == list:
        for voucher_id in vouchers:
            try:
                voucher_instance = Vouchers.objects.get(id=voucher_id)
            except:
                pass
            else:
                PromotionExcludedItem.objects.create(
                    object_type='Direct Or Flat',
                    object_id=f'{flatordirect.id}',
                    excluded_type='Voucher',
                    excluded_id=f'{voucher_instance.id}',
                    is_active=True,
                )

    serializers = PromtoionsSerializers.DirectOrFlatDiscountSerializers(flatordirect, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Direct or Flat Created Successfully!',
                'error_message': None,
                'errors': error,
                'flatordirect': serializers.data,

            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_directorflat(request):
    data = []

    flatordirect = DirectOrFlatDiscount.objects.filter(is_deleted=False).order_by('-created_at').distinct()
    serialized = PromtoionsSerializers.DirectOrFlatDiscountSerializers(flatordirect, many=True,
                                                                       context={'request': request})
    data.extend(serialized.data)

    specific_group = SpecificGroupDiscount.objects.filter(is_deleted=False).order_by('-created_at').distinct()
    serialized = PromtoionsSerializers.SpecificGroupDiscountSerializers(specific_group, many=True,
                                                                        context={'request': request})
    data.extend(serialized.data)

    purchase_discount = PurchaseDiscount.objects.filter(is_deleted=False).order_by('-created_at').distinct()
    serialized = PromtoionsSerializers.PurchaseDiscountSerializers(purchase_discount, many=True,
                                                                   context={'request': request})
    data.extend(serialized.data)

    specificbrand = SpecificBrand.objects.filter(is_deleted=False).order_by('-created_at').distinct()
    serialized = PromtoionsSerializers.SpecificBrandSerializers(specificbrand, many=True, context={'request': request})
    data.extend(serialized.data)

    spend_discount = SpendDiscount.objects.filter(is_deleted=False).order_by('-created_at').distinct()
    serialized = PromtoionsSerializers.SpendDiscountSerializers(spend_discount, many=True, context={'request': request})
    data.extend(serialized.data)

    spend_discount = SpendSomeAmount.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = PromtoionsSerializers.SpendSomeAmountSerializers(spend_discount, many=True,
                                                                  context={'request': request})
    data.extend(serialized.data)

    fixed_price = FixedPriceService.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = PromtoionsSerializers.FixedPriceServiceSerializers(fixed_price, many=True,
                                                                    context={'request': request})
    data.extend(serialized.data)

    free_price = MentionedNumberService.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = PromtoionsSerializers.MentionedNumberServiceSerializers(free_price, many=True,
                                                                         context={'request': request})
    data.extend(serialized.data)

    bundle = BundleFixed.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = PromtoionsSerializers.BundleFixedSerializers(bundle, many=True, context={'request': request})
    data.extend(serialized.data)

    retail = RetailAndGetService.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = PromtoionsSerializers.RetailAndGetServiceSerializers(retail, many=True, context={'request': request})
    data.extend(serialized.data)

    restricted = UserRestrictedDiscount.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = PromtoionsSerializers.UserRestrictedDiscountSerializers(restricted, many=True,
                                                                         context={'request': request})
    data.extend(serialized.data)

    complimentry = ComplimentaryDiscount.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = PromtoionsSerializers.ComplimentaryDiscountSerializers(complimentry, many=True,
                                                                        context={'request': request})
    data.extend(serialized.data)

    package = PackagesDiscount.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = PromtoionsSerializers.PackagesDiscountSerializers(package, many=True, context={'request': request})
    data.extend(serialized.data)

    coupon = Coupon.objects.all()
    serialized = CouponSerializer(coupon, many=True, context={'request': request})
    data.extend(serialized.data)
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Discount',
                'error_message': None,
                'flatordirect': data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_directorflat(request):
    directorflat_id = request.data.get('id', None)

    if directorflat_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        directorflat = DirectOrFlatDiscount.objects.get(id=directorflat_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Direct Or Flat Discount Service Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    directorflat.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Direct or Flat deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_directorflat(request):
    directorflat_id = request.data.get('id', None)

    location = request.data.get('location', None)

    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    promotion_name = request.data.get('promotion_name', '')

    dayrestrictions = request.data.get('dayrestrictions', None)
    categorydiscount = request.data.get('categorydiscount', None)
    blockdate = request.data.get('blockdate', None)

    products = request.data.get('product', [])
    services = request.data.get('services', [])
    vouchers = request.data.get('voucher', [])

    error = []

    if directorflat_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        directorflat = DirectOrFlatDiscount.objects.get(id=directorflat_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Direct Or Flat Discount Service Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        datetestriction = DateRestrictions.objects.get(directorflat=directorflat.id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Direct Or Flat Discount datetestriction Service Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if start_date:
        datetestriction.start_date = start_date
    if end_date:
        datetestriction.end_date = end_date

    directorflat.promotion_name = promotion_name
    directorflat.save()

    datetestriction.save()

    if location is not None:
        if type(location) == str:
            location = json.loads(location)
        elif type(location) == list:
            pass
        datetestriction.business_address.clear()
        for loc in location:
            try:
                loca = BusinessAddress.objects.get(id=loc)
                datetestriction.business_address.add(loca)
            except Exception as err:
                error.append(str(err))

    if categorydiscount is not None:
        if type(categorydiscount) == str:
            categorydiscount = categorydiscount.replace("'", '"')
            categorydiscount = json.loads(categorydiscount)
        else:
            pass
        for cat in categorydiscount:
            id = cat.get('id', None)
            category = cat.get('category', None)
            discount = cat.get('discount', None)
            is_deleted = cat.get('is_deleted', None)
            if id is not None:
                try:
                    category_id = CategoryDiscount.objects.get(id=str(id))
                    if str(is_deleted) == "True":
                        category_id.delete()
                        continue
                    category_id.category_type = category
                    category_id.discount = discount
                    category_id.save()
                except Exception as err:
                    error.append(str(err))
            else:
                CategoryDiscount.objects.create(
                    directorflat=directorflat,

                    category_type=category,
                    discount=discount
                )

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id=str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()

                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text=f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    directorflat=directorflat,
                    day=day,
                )

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:
            date = bl_date.get('date', None)
            is_deleted = bl_date.get('is_deleted', None)
            id = bl_date.get('id', None)
            if id is not None:
                try:
                    block_date = BlockDate.objects.get(id=str(id))
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date = date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
                BlockDate.objects.create(
                    directorflat=directorflat,
                    date=date,
                )
    if type(products) == str:
        try:
            products = json.loads(products)
        except:
            products = []

    PromotionExcludedItem.objects.filter(
        object_type='Direct Or Flat',
        object_id=f'{directorflat.id}',
        excluded_type='Product',
        is_active=True,
    ).exclude(
        excluded_id__in=products,
    ).delete()

    if type(products) == list:
        for product_id in products:
            PromotionExcludedItem.objects.get_or_create(
                object_type='Direct Or Flat',
                object_id=f'{directorflat.id}',
                excluded_type='Product',
                excluded_id=product_id,
                is_active=True,
            )

    if type(services) == str:
        try:
            services = json.loads(services)
        except:
            services = []

    PromotionExcludedItem.objects.filter(
        object_type='Direct Or Flat',
        object_id=f'{directorflat.id}',
        excluded_type='Service',
        is_active=True,
    ).exclude(
        excluded_id__in=services,
    ).delete()

    if type(services) == list:
        for service_id in services:
            PromotionExcludedItem.objects.get_or_create(
                object_type='Direct Or Flat',
                object_id=f'{directorflat.id}',
                excluded_type='Service',
                excluded_id=service_id,
                is_active=True,
            )

    if type(vouchers) == str:
        try:
            vouchers = json.loads(vouchers)
        except:
            vouchers = []

    PromotionExcludedItem.objects.filter(
        object_type='Direct Or Flat',
        object_id=f'{directorflat.id}',
        excluded_type='Voucher',
        is_active=True,
    ).exclude(
        excluded_id__in=vouchers,
    ).delete()

    if type(vouchers) == list:
        for voucher_id in vouchers:
            PromotionExcludedItem.objects.get_or_create(
                object_type='Direct Or Flat',
                object_id=f'{directorflat.id}',
                excluded_type='Voucher',
                excluded_id=voucher_id,
                is_active=True,
            )

    serializers = PromtoionsSerializers.DirectOrFlatDiscountSerializers(directorflat, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Direct or Flat Updated Successfully!',
                'error_message': None,
                'error': error,
                'flatordirect': serializers.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_discount_and_promotions(request):
    time_now = datetime.now()

    data = {}

    filter_queries = {
        'normal_queries': {
            'is_deleted': False,
        },
    }

    selected_date = request.GET.get('selected_date', '2023-01-19')
    selected_day = request.GET.get('selected_day', None)
    selected_location = request.GET.get('selected_location', None)

    if not selected_day or selected_day is None:
        # selected_day = 'Nothing_Found'
        selected_day = datetime.now().strftime('%A')

    ##Done VERIFIED
    flatordirect = DirectOrFlatDiscount.objects.filter(
        directorflat_daterestrictions__start_date__lte=selected_date,
        directorflat_daterestrictions__end_date__gte=selected_date,
        directorflat_daterestrictions__business_address__id=selected_location,
        # directorflat_dayrestrictions__day__in = [None]
        **filter_queries['normal_queries'],
        # ).distinct()
    ).exclude(
        Q(directorflat_dayrestrictions__day__icontains=selected_day) |
        Q(directorflat_blockdate__date=selected_date)
        # Q(directorflat_daterestrictions__business_address__id = selected_location)
    ).distinct()
    # serialized = PromtoionsSerializers.AvailOfferDirectOrFlatDiscountSerializers(flatordirect,  many=True, context={'request' : request,})
    serialized = PromtoionsSerializers.DirectOrFlatDiscountSerializers(flatordirect, many=True,
                                                                       context={'request': request})
    data['directFlat'] = serialized.data

    # Done
    specific_group = SpecificGroupDiscount.objects.filter(
        **filter_queries['normal_queries'],
        specificgroupdiscount_daterestrictions__start_date__lte=selected_date,
        specificgroupdiscount_daterestrictions__end_date__gte=selected_date,
        specificgroupdiscount_daterestrictions__business_address__id=selected_location,
    ).exclude(
        Q(specificgroupdiscount_dayrestrictions__day__icontains=selected_day) |
        Q(specificgroupdiscount_blockdate__date=selected_date, )
        # Q(specificgroupdiscount_daterestrictions__business_address__id = selected_location)
    ).distinct()
    # serialized = PromtoionsSerializers.AvailOfferSpecificGroupDiscountSerializers(specific_group,  many=True, context={'request' : request})
    serialized = PromtoionsSerializers.SpecificGroupDiscountSerializers(specific_group, many=True,
                                                                        context={'request': request})
    data['specificCategoryGroup'] = serialized.data

    # __date = selected_date,

    # Done
    purchase_discount = PurchaseDiscount.objects.filter(
        **filter_queries['normal_queries'],
        purchasediscount_daterestrictions__start_date__lte=selected_date,
        purchasediscount_daterestrictions__end_date__gte=selected_date,
        purchasediscount_daterestrictions__business_address__id=selected_location,
    ).exclude(
        Q(purchasediscount_dayrestrictions__day__icontains=selected_day, ) |
        Q(purchasediscount_blockdate__date=selected_date, )
        # Q(purchasediscount_daterestrictions__business_address__id = selected_location)
    ).distinct()
    # serialized = PromtoionsSerializers.AvailOfferPurchaseDiscountSerializers(purchase_discount,  many=True, context={'request' : request})
    serialized = PromtoionsSerializers.PurchaseDiscountSerializers(purchase_discount, many=True,
                                                                   context={'request': request})
    data['purchase'] = serialized.data

    # Done
    specificbrand = SpecificBrand.objects.filter(
        **filter_queries['normal_queries'],
        specificbrand_daterestrictions__start_date__lte=selected_date,
        specificbrand_daterestrictions__end_date__gte=selected_date,
        specificbrand_daterestrictions__business_address__id=selected_location,
    ).exclude(
        Q(specificbrand_dayrestrictions__day__icontains=selected_day, ) |
        Q(specificbrand_blockdate__date=selected_date, )
        # Q(specificbrand_daterestrictions__business_address__id = selected_location)
    ).distinct()
    # serialized = PromtoionsSerializers.AvailOfferSpecificBrandSerializers(specificbrand,  many=True, context={'request' : request})
    serialized = PromtoionsSerializers.SpecificBrandSerializers(specificbrand, many=True, context={'request': request})
    data['specificBrandServiceGroup'] = serialized.data

    # Done
    # spend_discount = SpendDiscount.objects.filter(
    #     **filter_queries['normal_queries'],
    #     spenddiscount_daterestrictions__start_date__lte = selected_date,
    #     spenddiscount_daterestrictions__end_date__gte = selected_date,
    # ).exclude(
    #     Q(spenddiscount_dayrestrictions__day__icontains = selected_day,) |
    #     Q(spenddiscount_blockdate__date = selected_date,)
    # ).distinct()
    # serialized = PromtoionsSerializers.AvailOfferSpendDiscountSerializers(spend_discount,  many=True, context={'request' : request})
    # data['spend_discount'] = serialized.data

    # Done
    spend_discount = SpendSomeAmount.objects.filter(
        **filter_queries['normal_queries'],
        spendsomeamount_daterestrictions__start_date__lte=selected_date,
        spendsomeamount_daterestrictions__end_date__gte=selected_date,
        spendsomeamount_daterestrictions__business_address__id=selected_location,
    ).exclude(
        Q(spendsomeamount_dayrestrictions__day__icontains=selected_day, ) |
        Q(spendsomeamount_blockdate__date=selected_date, )
        # Q(spendsomeamount_daterestrictions__business_address__id = selected_location)
    ).distinct()
    # serialized = PromtoionsSerializers.AvailOfferSpendSomeAmountSerializers(spend_discount,  many=True, context={'request' : request})
    serialized = PromtoionsSerializers.SpendSomeAmountSerializers(spend_discount, many=True,
                                                                  context={'request': request})
    data['spendSomeAmount'] = serialized.data

    # Done
    fixed_price = FixedPriceService.objects.filter(
        **filter_queries['normal_queries'],
        fixedpriceservice_daterestrictions__start_date__lte=selected_date,
        fixedpriceservice_daterestrictions__end_date__gte=selected_date,
        fixedpriceservice_daterestrictions__business_address__id=selected_location,
    ).exclude(
        Q(fixedpriceservice_dayrestrictions__day__icontains=selected_day, ) |
        Q(fixedpriceservice_blockdate__date=selected_date, )
        # Q(fixedpriceservice_daterestrictions__business_address__id = selected_location)
    ).distinct()
    # serialized = PromtoionsSerializers.AvailOfferFixedPriceServiceSerializers(fixed_price,  many=True, context={'request' : request})
    serialized = PromtoionsSerializers.FixedPriceServiceSerializers(fixed_price, many=True,
                                                                    context={'request': request})
    data['fixedPrice'] = serialized.data

    ##Done
    free_price = MentionedNumberService.objects.filter(
        **filter_queries['normal_queries'],
        mentionednumberservice_daterestrictions__start_date__lte=selected_date,
        mentionednumberservice_daterestrictions__end_date__gte=selected_date,
        mentionednumberservice_daterestrictions__business_address__id=selected_location,
    ).exclude(
        Q(mentionednumberservice_dayrestrictions__day__icontains=selected_day, ) |
        Q(mentionednumberservice_blockdate__date=selected_date, )
        # Q(mentionednumberservice_daterestrictions__business_address__id = selected_location)
    ).distinct()
    # serialized = PromtoionsSerializers.AvailOfferMentionedNumberServiceSerializers(free_price,  many=True, context={'request' : request})
    serialized = PromtoionsSerializers.MentionedNumberServiceSerializers(free_price, many=True,
                                                                         context={'request': request})
    data['get_free_item_for_other_purchase'] = serialized.data

    # Done
    bundle = BundleFixed.objects.filter(
        **filter_queries['normal_queries'],
        bundlefixed_daterestrictions__start_date__lte=selected_date,
        bundlefixed_daterestrictions__end_date__gte=selected_date,
        bundlefixed_daterestrictions__business_address__id=selected_location,
    ).exclude(
        Q(bundlefixed_dayrestrictions__day__icontains=selected_day, ) |
        Q(bundlefixed_blockdate__date=selected_date, )
        # Q(bundlefixed_daterestrictions__business_address__id = selected_location)
    ).distinct()
    # serialized = PromtoionsSerializers.AvailOfferBundleFixedSerializers(bundle,  many=True, context={'request' : request})
    serialized = PromtoionsSerializers.BundleFixedSerializers(bundle, many=True, context={'request': request})
    data['bundleDiscount'] = serialized.data

    # Done
    retail = RetailAndGetService.objects.filter(
        **filter_queries['normal_queries'],
        retailandservice_daterestrictions__start_date__lte=selected_date,
        retailandservice_daterestrictions__end_date__gte=selected_date,
        retailandservice_daterestrictions__business_address__id=selected_location,
    ).exclude(
        Q(retailandservice_dayrestrictions__day__icontains=selected_day, ) |
        Q(retailandservice_blockdate__date=selected_date, )
        # Q(retailandservice_daterestrictions__business_address__id = selected_location)
    ).distinct()
    # serialized = PromtoionsSerializers.AvailOfferRetailAndGetServiceSerializers(retail, many=True, context={'request' : request})
    serialized = PromtoionsSerializers.RetailAndGetServiceSerializers(retail, many=True, context={'request': request})
    data['retailPromotion'] = serialized.data

    # Done
    restricted = UserRestrictedDiscount.objects.filter(
        **filter_queries['normal_queries'],
        userrestricteddiscount_daterestrictions__start_date__lte=selected_date,
        userrestricteddiscount_daterestrictions__end_date__gte=selected_date,
        userrestricteddiscount_daterestrictions__business_address__id=selected_location,
    ).exclude(
        Q(userrestricteddiscount_dayrestrictions__day__icontains=selected_day, ) |
        Q(userrestricteddiscount_blockdate__date=selected_date, )
        # Q(userrestricteddiscount_daterestrictions__business_address__id = selected_location)
    ).distinct()
    # serialized = PromtoionsSerializers.AvailOfferUserRestrictedDiscountSerializers(restricted, many=True, context={'request' : request})
    serialized = PromtoionsSerializers.UserRestrictedDiscountSerializers(restricted, many=True,
                                                                         context={'request': request})
    data['userRestricted'] = serialized.data

    # Done
    complimentry = ComplimentaryDiscount.objects.filter(
        **filter_queries['normal_queries'],
        complimentary_daterestrictions__start_date__lte=selected_date,
        complimentary_daterestrictions__end_date__gte=selected_date,
        complimentary_daterestrictions__business_address__id=selected_location,
    ).exclude(
        Q(complimentary_dayrestrictions__day__icontains=selected_day, ) |
        Q(complimentary_blockdate__date=selected_date, )
        # Q(complimentary_daterestrictions__business_address__id = selected_location)
    ).distinct()
    # serialized = PromtoionsSerializers.AvailOfferComplimentaryDiscountSerializers(complimentry, many=True, context={'request' : request})
    serialized = PromtoionsSerializers.ComplimentaryDiscountSerializers(complimentry, many=True,
                                                                        context={'request': request})
    data['complimentaryVoucher'] = serialized.data

    ##Done
    package = PackagesDiscount.objects.filter(
        package_daterestrictions__start_date__lte=selected_date,
        package_daterestrictions__end_date__gte=selected_date,
        package_daterestrictions__business_address__id=selected_location,
        **filter_queries['normal_queries'],
    ).exclude(
        Q(package_dayrestrictions__day__icontains=selected_day, ) |
        Q(package_blockdate__date=selected_date)
        # Q(package_daterestrictions__business_address__id = selected_location)
    ).distinct()
    # serialized = PromtoionsSerializers.AvailOfferPackagesDiscountSerializers(package, many=True, context={'request' : request})
    serialized = PromtoionsSerializers.PackagesDiscountSerializers(package, many=True, context={'request': request})
    data['packages'] = serialized.data

    end_time = datetime.now()

    difference = end_time - time_now
    difference = difference.total_seconds()

    response = {
        'status': 200,
        'status_code': '200',
        'request': {
            'request_time': difference,
            'size': f'{(sys.getsizeof(data)) / 1024} kb'
        },
        'response': {
            'message': 'All Discounts & Promotions',
            'error_message': None,
            'count': len(data),
            'avail_offers': data
        }
    }

    return Response(response, status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_specificgroupdiscount(request):
    user = request.user
    business_id = request.data.get('business', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    promotion_name = request.data.get('promotion_name', '')

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    servicegroup = request.data.get('servicegroup', None)

    # brand = request.data.get('brand', None)
    # brand_discount = request.data.get('brand_discount', None)

    products = request.data.get('product', [])
    services = request.data.get('services', [])
    vouchers = request.data.get('voucher', [])

    error = []

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    sp_grp = SpecificGroupDiscount.objects.create(
        user=user,
        business=business,
        promotion_name=promotion_name
    )
    date_res = DateRestrictions.objects.create(
        specificgroupdiscount=sp_grp,
        start_date=start_date,
        end_date=end_date,
    )
    if location is not None:
        if type(location) == str:
            location = json.loads(location)

        elif type(location) == list:
            pass

        for loc in location:
            try:
                address = BusinessAddress.objects.get(id=loc)
                date_res.business_address.add(address)
            except Exception as err:
                error.append(str(err))

    if servicegroup is not None:
        if type(servicegroup) == str:
            servicegroup = servicegroup.replace("'", '"')
            servicegroup = json.loads(servicegroup)
        else:
            pass
        for cat in servicegroup:
            try:
                service_group = cat.get('service_group', None)
                discount = cat.get('discount', None)
                brand = cat.get('brand', None)
                brand_discount = cat.get('brand_discount', None)
                try:
                    service_grp = ServiceGroup.objects.get(id=str(service_group))
                    brand = Brand.objects.get(id=str(brand))
                except:
                    pass
                ServiceGroupDiscount.objects.create(
                    specificgroupdiscount=sp_grp,
                    brand=brand,
                    brand_discount=brand_discount,
                    servicegroup=service_grp,
                    discount=discount
                )

            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            try:
                day = dayres.get('day', None)

                DayRestrictions.objects.create(
                    specificgroupdiscount=sp_grp,
                    day=day,
                )

            except Exception as err:
                error.append(str(err))

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:

            try:
                date = bl_date.get('date', None)
                BlockDate.objects.create(
                    specificgroupdiscount=sp_grp,
                    date=date,
                )

            except Exception as err:
                error.append(str(err))
    if type(products) == str:
        try:
            products = json.loads(products)
        except:
            products = []

    if type(products) == list:
        for product_id in products:
            PromotionExcludedItem.objects.create(
                object_type='Specific Group Discount',
                object_id=f'{sp_grp.id}',
                excluded_type='Product',
                excluded_id=product_id,
                is_active=True,
            )

    if type(services) == str:
        try:
            services = json.loads(services)
        except:
            services = []

    if type(services) == list:
        for service_id in services:
            PromotionExcludedItem.objects.create(
                object_type='Specific Group Discount',
                object_id=f'{sp_grp.id}',
                excluded_type='Service',
                excluded_id=service_id,
                is_active=True,
            )

    if type(vouchers) == str:
        try:
            vouchers = json.loads(vouchers)
        except:
            vouchers = []

    if type(vouchers) == list:
        for voucher_id in vouchers:
            PromotionExcludedItem.objects.create(
                object_type='Specific Group Discount',
                object_id=f'{sp_grp.id}',
                excluded_type='Voucher',
                excluded_id=voucher_id,
                is_active=True,
            )
    serializers = PromtoionsSerializers.SpecificGroupDiscountSerializers(sp_grp, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Specific Group Discount Created Successfully!',
                'error_message': None,
                'errors': error,
                'specificgroup': serializers.data,

            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_specificgroupdiscount(request):
    user = request.user

    specificgroup_id = request.data.get('id', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    promotion_name = request.data.get('promotion_name', '')

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    servicegroup = request.data.get('servicegroup', None)

    products = request.data.get('product', [])
    services = request.data.get('services', [])
    vouchers = request.data.get('voucher', [])

    error = []

    if specificgroup_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        specific_group = SpecificGroupDiscount.objects.get(id=specificgroup_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Direct Or Flat Discount Service Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    specific_group.promotion_name = promotion_name
    specific_group.save()

    if servicegroup is not None:
        if type(servicegroup) == str:
            servicegroup = servicegroup.replace("'", '"')
            servicegroup = json.loads(servicegroup)
        else:
            pass
        for cat in servicegroup:
            id = cat.get('id', None)
            service_group = cat.get('service_group', None)
            discount = cat.get('discount', None)
            is_deleted = cat.get('is_deleted', None)
            try:
                service_grp = ServiceGroup.objects.get(id=str(service_group))
            except:
                pass
            if id is not None:
                try:
                    ser_grp = ServiceGroupDiscount.objects.get(id=str(id))
                    if str(is_deleted) == "True":
                        ser_grp.delete()
                        continue
                    ser_grp.servicegroup = service_grp
                    ser_grp.discount = discount
                    ser_grp.save()
                except Exception as err:
                    error.append(str(err))
            else:
                ServiceGroupDiscount.objects.create(
                    specificgroupdiscount=specific_group,
                    servicegroup=service_grp,
                    discount=discount
                )

    try:
        daterestriction = DateRestrictions.objects.get(specificgroupdiscount=specific_group.id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'daterestriction Service Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if start_date:
        daterestriction.start_date = start_date
    if end_date:
        daterestriction.end_date = end_date
    daterestriction.save()

    if location is not None:
        if type(location) == str:
            location = json.loads(location)
        elif type(location) == list:
            pass
        daterestriction.business_address.clear()
        for loc in location:
            try:
                loca = BusinessAddress.objects.get(id=loc)
                daterestriction.business_address.add(loca)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id=str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()

                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text=f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    specificgroupdiscount=specific_group,
                    day=day,
                )

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:
            date = bl_date.get('date', None)
            is_deleted = bl_date.get('is_deleted', None)
            id = bl_date.get('id', None)
            if id is not None:
                try:
                    block_date = BlockDate.objects.get(id=str(id))
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date = date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
                BlockDate.objects.create(
                    specificgroupdiscount=specific_group,
                    date=date,
                )

    if type(products) == str:
        try:
            products = json.loads(products)
        except:
            products = []

    PromotionExcludedItem.objects.filter(
        object_type='Specific Group Discount',
        object_id=f'{specific_group.id}',
        excluded_type='Product',
        is_active=True,
    ).exclude(
        excluded_id__in=products,
    ).delete()

    if type(products) == list:
        for product_id in products:
            PromotionExcludedItem.objects.get_or_create(
                object_type='Specific Group Discount',
                object_id=f'{specific_group.id}',
                excluded_type='Product',
                excluded_id=product_id,
                is_active=True,
            )

    if type(services) == str:
        try:
            services = json.loads(services)
        except:
            services = []

    PromotionExcludedItem.objects.filter(
        object_type='Specific Group Discount',
        object_id=f'{specific_group.id}',
        excluded_type='Service',
        is_active=True,
    ).exclude(
        excluded_id__in=services,
    ).delete()

    if type(services) == list:
        for service_id in services:
            PromotionExcludedItem.objects.get_or_create(
                object_type='Specific Group Discount',
                object_id=f'{specific_group.id}',
                excluded_type='Service',
                excluded_id=service_id,
                is_active=True,
            )

    if type(vouchers) == str:
        try:
            vouchers = json.loads(vouchers)
        except:
            vouchers = []

    PromotionExcludedItem.objects.filter(
        object_type='Specific Group Discount',
        object_id=f'{specific_group.id}',
        excluded_type='Voucher',
        is_active=True,
    ).exclude(
        excluded_id__in=vouchers,
    ).delete()

    if type(vouchers) == list:
        for voucher_id in vouchers:
            PromotionExcludedItem.objects.get_or_create(
                object_type='Specific Group Discount',
                object_id=f'{specific_group.id}',
                excluded_type='Voucher',
                excluded_id=voucher_id,
                is_active=True,
            )

    serializers = PromtoionsSerializers.SpecificGroupDiscountSerializers(specific_group, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Specific Group Discount Updated Successfully!',
                'error_message': None,
                'error': error,
                'specificgroup': serializers.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_specificgroupdiscount(request):
    specific_id = request.data.get('id', None)

    if specific_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        specific_grp = SpecificGroupDiscount.objects.get(id=specific_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Specific group Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    specific_grp.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Specific Group Discount deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_specificgroupdiscount(request):
    specific_group = SpecificGroupDiscount.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = PromtoionsSerializers.SpecificGroupDiscountSerializers(specific_group, many=True,
                                                                        context={'request': request})

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Specific Group Discount',
                'error_message': None,
                'specificgroup': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_purchasediscount(request):
    user = request.user
    business_id = request.data.get('business', None)

    select_type = request.data.get('select_type', None)
    product = request.data.get('product', None)
    service = request.data.get('service', None)

    purchase = request.data.get('purchase', None)
    discount_product = request.data.get('discount_product', None)
    discount_service = request.data.get('discount_service', None)
    promotion_name = request.data.get('promotion_name', '')

    discount_value = request.data.get('discount_value', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    error = []

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    purchase_discount = PurchaseDiscount.objects.create(
        user=user,
        business=business,
        select_type=select_type,
        purchase=purchase,
        discount_value=discount_value,
        promotion_name=promotion_name,
    )
    if select_type == 'Product':
        try:
            product_id = Product.objects.get(id=product)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.PRODUCT_NOT_FOUND_4037,
                    'response': {
                        'message': 'Product not found',
                        'error_message': str(err),
                    }
                }

            )

        try:
            discount_product_id = Product.objects.get(id=discount_product)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.PRODUCT_NOT_FOUND_4037,
                    'response': {
                        'message': 'Discount Product not found',
                        'error_message': str(err),

                    }
                }
            )
        purchase_discount.product = product_id
        purchase_discount.discount_product = discount_product_id
        purchase_discount.save()

    else:
        try:
            service_id = Service.objects.get(id=service)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.SERVICE_NOT_FOUND_4035,
                    'response': {
                        'message': 'Product not found',
                        'error_message': str(err),
                    }
                }

            )

        try:
            discount_service_id = Service.objects.get(id=discount_service)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.SERVICE_NOT_FOUND_4035,
                    'response': {
                        'message': 'Discount Product not found',
                        'error_message': str(err),
                    }
                }

            )
        purchase_discount.service = service_id
        purchase_discount.discount_service = discount_service_id
        purchase_discount.save()

    date_res = DateRestrictions.objects.create(
        purchasediscount=purchase_discount,
        start_date=start_date,
        end_date=end_date,
    )

    if location is not None:
        if type(location) == str:
            location = json.loads(location)

        elif type(location) == list:
            pass

        for loc in location:
            try:
                address = BusinessAddress.objects.get(id=loc)
                date_res.business_address.add(address)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            try:
                day = dayres.get('day', None)

                DayRestrictions.objects.create(
                    purchasediscount=purchase_discount,
                    day=day,
                )

            except Exception as err:
                error.append(str(err))

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:

            try:
                date = bl_date.get('date', None)
                BlockDate.objects.create(
                    purchasediscount=purchase_discount,
                    date=date,
                )

            except Exception as err:
                error.append(str(err))

    serializers = PromtoionsSerializers.PurchaseDiscountSerializers(purchase_discount, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Purchase Discount Created Successfully!',
                'error_message': None,
                'errors': error,
                'purchasediscount': serializers.data,

            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_purchasediscount(request):
    purchase_id = request.data.get('id', None)

    select_type = request.data.get('select_type', None)
    product = request.data.get('product', None)
    service = request.data.get('service', None)

    purchase = request.data.get('purchase', None)
    discount_product = request.data.get('discount_product', None)
    discount_service = request.data.get('discount_service', None)

    promotion_name = request.data.get('promotion_name', '')

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    error = []

    if purchase_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        purchase_discount = PurchaseDiscount.objects.get(id=purchase_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Purchase Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    purchase_discount.promotion_name = promotion_name
    purchase_discount.save()

    try:
        daterestriction = DateRestrictions.objects.get(purchasediscount=purchase_discount.id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'daterestriction Service Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if start_date:
        daterestriction.start_date = start_date
    if end_date:
        daterestriction.end_date = end_date
    daterestriction.save()

    if location is not None:
        if type(location) == str:
            location = json.loads(location)
        elif type(location) == list:
            pass
        daterestriction.business_address.clear()
        for loc in location:
            try:
                loca = BusinessAddress.objects.get(id=loc)
                daterestriction.business_address.add(loca)
            except Exception as err:
                error.append(str(err))
    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id=str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()

                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text=f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    purchasediscount=purchase_discount,
                    day=day,
                )

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:
            date = bl_date.get('date', None)
            is_deleted = bl_date.get('is_deleted', None)
            id = bl_date.get('id', None)
            if id is not None:
                try:
                    block_date = BlockDate.objects.get(id=str(id))
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date = date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
                BlockDate.objects.create(
                    purchasediscount=purchase_discount,
                    date=date,
                )
    serializers = PromtoionsSerializers.PurchaseDiscountSerializers(purchase_discount, data=request.data, partial=True,
                                                                    context={'request': request})
    if serializers.is_valid():
        serializers.save()
    else:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'response': {
                    'message': 'Invialid Data',
                    'error_message': str(serializers.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Purchase Discount Updated Successfully!',
                'error_message': None,
                'error': error,
                'purchasediscount': serializers.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_purchasediscount(request):
    purchase_id = request.data.get('id', None)

    if purchase_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        purchase_dicount = PurchaseDiscount.objects.get(id=purchase_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Purchase Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    purchase_dicount.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Purchase Discount deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_purchasediscount(request):
    purchase_discount = SpecificGroupDiscount.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = PromtoionsSerializers.PurchaseDiscountSerializers(purchase_discount, many=True,
                                                                   context={'request': request})

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Purchase Discount',
                'error_message': None,
                'purchasediscount': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_specificbrand_discount(request):
    user = request.user
    business_id = request.data.get('business', None)

    service_group = request.data.get('service_group', None)
    brand = request.data.get('brand', None)

    discount_brand = request.data.get('discount_brand', None)
    discount_service_group = request.data.get('discount_service_group', None)
    promotion_name = request.data.get('promotion_name', '')

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    products = request.data.get('product', [])
    services = request.data.get('services', [])
    vouchers = request.data.get('voucher', [])

    error = []

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        service_grp = ServiceGroup.objects.get(id=str(service_group))
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.SERVICEGROUP_NOT_FOUND_4042,
                'response': {
                    'message': 'Service Group not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        brand_id = Brand.objects.get(id=str(brand))
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_CATEGORY_BRAND_4020,
                'response': {
                    'message': 'Brand not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    specific_brand = SpecificBrand.objects.create(
        user=user,
        business=business,

        servicegroup=service_grp,
        brand=brand_id,
        discount_brand=discount_brand,
        discount_service_group=discount_service_group,

        promotion_name=promotion_name,
    )

    date_res = DateRestrictions.objects.create(
        specificbrand=specific_brand,
        start_date=start_date,
        end_date=end_date,
    )
    if location is not None:
        if type(location) == str:
            location = json.loads(location)

        elif type(location) == list:
            pass

        for loc in location:
            try:
                address = BusinessAddress.objects.get(id=loc)
                date_res.business_address.add(address)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            try:
                day = dayres.get('day', None)

                DayRestrictions.objects.create(
                    specificbrand=specific_brand,
                    day=day,
                )

            except Exception as err:
                error.append(str(err))

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:

            try:
                date = bl_date.get('date', None)
                BlockDate.objects.create(
                    specificbrand=specific_brand,
                    date=date,
                )

            except Exception as err:
                error.append(str(err))

    if type(products) == str:
        try:
            products = json.loads(products)
        except:
            products = []

    if type(products) == list:
        for product_id in products:
            PromotionExcludedItem.objects.create(
                object_type='Specific Brand Discount',
                object_id=f'{specific_brand.id}',
                excluded_type='Product',
                excluded_id=product_id,
                is_active=True,
            )

    if type(services) == str:
        try:
            services = json.loads(services)
        except:
            services = []

    if type(services) == list:
        for service_id in services:
            PromotionExcludedItem.objects.create(
                object_type='Specific Brand Discount',
                object_id=f'{specific_brand.id}',
                excluded_type='Service',
                excluded_id=service_id,
                is_active=True,
            )

    if type(vouchers) == str:
        try:
            vouchers = json.loads(vouchers)
        except:
            vouchers = []

    if type(vouchers) == list:
        for voucher_id in vouchers:
            PromotionExcludedItem.objects.create(
                object_type='Specific Brand Discount',
                object_id=f'{specific_brand.id}',
                excluded_type='Voucher',
                excluded_id=voucher_id,
                is_active=True,
            )

    serializers = PromtoionsSerializers.SpecificBrandSerializers(specific_brand, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Specific Brand Discount Created Successfully!',
                'error_message': None,
                'errors': error,
                'specificbrand': serializers.data,

            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_specificbrand_discount(request):
    id = request.data.get('id', None)

    if id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        specific_dicount = SpecificBrand.objects.get(id=id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Specific Brand Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    specific_dicount.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Specific Brand Discount deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_specificbrand_discount(request):
    specificbrand = SpecificBrand.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = PromtoionsSerializers.SpecificBrandSerializers(specificbrand, many=True, context={'request': request})

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Purchase Discount',
                'error_message': None,
                'specificbrand': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_specificbrand_discount(request):
    specific_id = request.data.get('id', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)
    promotion_name = request.data.get('promotion_name', '')

    products = request.data.get('product', [])
    services = request.data.get('services', [])
    vouchers = request.data.get('voucher', [])

    error = []

    if specific_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        specific_discount = SpecificBrand.objects.get(id=specific_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Specific Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    specific_discount.promotion_name = promotion_name
    specific_discount.save()

    try:
        daterestriction = DateRestrictions.objects.get(specificbrand=specific_discount.id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'daterestriction Service Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if start_date:
        daterestriction.start_date = start_date
    if end_date:
        daterestriction.end_date = end_date
    daterestriction.save()

    if location is not None:
        if type(location) == str:
            location = json.loads(location)
        elif type(location) == list:
            pass
        daterestriction.business_address.clear()
        for loc in location:
            try:
                loca = BusinessAddress.objects.get(id=loc)
                daterestriction.business_address.add(loca)
            except Exception as err:
                error.append(str(err))
    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id=str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()

                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text=f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    specificbrand=specific_discount,
                    day=day,
                )

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:
            date = bl_date.get('date', None)
            is_deleted = bl_date.get('is_deleted', None)
            id = bl_date.get('id', None)
            if id is not None:
                try:
                    block_date = BlockDate.objects.get(id=str(id))
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date = date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
                BlockDate.objects.create(
                    specificbrand=specific_discount,
                    date=date,
                )

    serializers = PromtoionsSerializers.SpecificBrandSerializers(specific_discount, data=request.data, partial=True,
                                                                 context={'request': request})
    if serializers.is_valid():
        serializers.save()
    else:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'response': {
                    'message': 'Invialid Data',
                    'error_message': str(serializers.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if type(products) == str:
        try:
            products = json.loads(products)
        except:
            products = []

    PromotionExcludedItem.objects.filter(
        object_type='Specific Brand Discount',
        object_id=f'{specific_discount.id}',
        excluded_type='Product',
        is_active=True,
    ).exclude(
        excluded_id__in=products,
    ).delete()

    if type(products) == list:
        for product_id in products:
            PromotionExcludedItem.objects.get_or_create(
                object_type='Specific Brand Discount',
                object_id=f'{specific_discount.id}',
                excluded_type='Product',
                excluded_id=product_id,
                is_active=True,
            )

    if type(services) == str:
        try:
            services = json.loads(services)
        except:
            services = []

    PromotionExcludedItem.objects.filter(
        object_type='Specific Brand Discount',
        object_id=f'{specific_discount.id}',
        excluded_type='Service',
        is_active=True,
    ).exclude(
        excluded_id__in=services,
    ).delete()

    if type(services) == list:
        for service_id in services:
            PromotionExcludedItem.objects.get_or_create(
                object_type='Specific Brand Discount',
                object_id=f'{specific_discount.id}',
                excluded_type='Service',
                excluded_id=service_id,
                is_active=True,
            )

    if type(vouchers) == str:
        try:
            vouchers = json.loads(vouchers)
        except:
            vouchers = []

    PromotionExcludedItem.objects.filter(
        object_type='Specific Brand Discount',
        object_id=f'{specific_discount.id}',
        excluded_type='Voucher',
        is_active=True,
    ).exclude(
        excluded_id__in=vouchers,
    ).delete()

    if type(vouchers) == list:
        for voucher_id in vouchers:
            PromotionExcludedItem.objects.get_or_create(
                object_type='Specific Brand Discount',
                object_id=f'{specific_discount.id}',
                excluded_type='Voucher',
                excluded_id=voucher_id,
                is_active=True,
            )

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Specific Brand Discount Updated Successfully!',
                'error_message': None,
                'error': error,
                'specificbrand': serializers.data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_spend_discount(request):
    user = request.user
    business_id = request.data.get('business', None)

    spend_amount = request.data.get('spend_amount', None)
    select_type = request.data.get('select_type', None)
    service = request.data.get('service', None)

    discount_product = request.data.get('discount_product', None)
    discount_service = request.data.get('discount_service', None)

    discount_value = request.data.get('discount_value', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    error = []

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        service_id = Service.objects.get(id=service)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.SERVICE_NOT_FOUND_4035,
                'response': {
                    'message': 'Service not found',
                    'error_message': str(err),
                }
            }

        )

    spend_discount = SpendDiscount.objects.create(
        user=user,
        business=business,
        select_type=select_type,
        spend_amount=spend_amount,
        discount_value=discount_value,
        service=service_id,
    )

    if discount_product:
        try:
            discount_product_id = Product.objects.get(id=discount_product)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.PRODUCT_NOT_FOUND_4037,
                    'response': {
                        'message': 'Discount Product not found',
                        'error_message': str(err),

                    }
                }
            )
        spend_discount.discount_product = discount_product_id
        spend_discount.save()
    if discount_service:
        try:
            discount_service_id = Service.objects.get(id=discount_service)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.SERVICE_NOT_FOUND_4035,
                    'response': {
                        'message': 'Discount Service not found',
                        'error_message': str(err),
                    }
                }

            )
        spend_discount.discount_service = discount_service_id
        spend_discount.save()

    date_res = DateRestrictions.objects.create(
        spenddiscount=spend_discount,
        start_date=start_date,
        end_date=end_date,
    )

    if location is not None:
        if type(location) == str:
            location = json.loads(location)

        elif type(location) == list:
            pass

        for loc in location:
            try:
                address = BusinessAddress.objects.get(id=loc)
                date_res.business_address.add(address)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            try:
                day = dayres.get('day', None)

                DayRestrictions.objects.create(
                    spenddiscount=spend_discount,
                    day=day,
                )

            except Exception as err:
                error.append(str(err))

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:

            try:
                date = bl_date.get('date', None)
                BlockDate.objects.create(
                    spenddiscount=spend_discount,
                    date=date,
                )

            except Exception as err:
                error.append(str(err))

    serializers = PromtoionsSerializers.SpendDiscountSerializers(spend_discount, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Spend Discount Created Successfully!',
                'error_message': None,
                'errors': error,
                'spenddiscount': serializers.data,

            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_spend_discount(request):
    spend_id = request.data.get('id', None)

    select_type = request.data.get('select_type', None)
    product = request.data.get('product', None)
    service = request.data.get('service', None)

    purchase = request.data.get('purchase', None)
    discount_product = request.data.get('discount_product', None)
    discount_service = request.data.get('discount_service', None)

    discount_value = request.data.get('discount_value', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    error = []

    if spend_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        spend_discount = PurchaseDiscount.objects.get(id=spend_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Purchase Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        daterestriction = DateRestrictions.objects.get(spenddiscount=spend_discount.id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'daterestriction Service Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if start_date:
        daterestriction.start_date = start_date
    if end_date:
        daterestriction.end_date = end_date
    daterestriction.save()

    if location is not None:
        if type(location) == str:
            location = json.loads(location)
        elif type(location) == list:
            pass
        daterestriction.business_address.clear()
        for loc in location:
            try:
                loca = BusinessAddress.objects.get(id=loc)
                daterestriction.business_address.add(loca)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id=str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()

                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text=f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    spenddiscount=spend_discount,
                    day=day,
                )

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:
            date = bl_date.get('date', None)
            is_deleted = bl_date.get('is_deleted', None)
            id = bl_date.get('id', None)
            if id is not None:
                try:
                    block_date = BlockDate.objects.get(id=str(id))
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date = date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
                BlockDate.objects.create(
                    spenddiscount=spend_discount,
                    date=date,
                )

    serializers = PromtoionsSerializers.PurchaseDiscountSerializers(spend_discount, data=request.data, partial=True,
                                                                    context={'request': request})
    if serializers.is_valid():
        serializers.save()
    else:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'response': {
                    'message': 'Invialid Data',
                    'error_message': str(serializers.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Purchase Discount Updated Successfully!',
                'error_message': None,
                'error': error,
                'purchasediscount': serializers.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_spend_discount(request):
    spend_id = request.data.get('id', None)

    if spend_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        spend_discount = SpendDiscount.objects.get(id=spend_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Spend Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    spend_discount.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Spend Discount deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_spend_discount(request):
    spend_discount = SpendDiscount.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = PromtoionsSerializers.SpendDiscountSerializers(spend_discount, many=True, context={'request': request})

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Spend Discount',
                'error_message': None,
                'spenddiscount': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_spend_some_amount(request):
    user = request.user
    business_id = request.data.get('business', None)

    # spend_amount = request.data.get('spend_amount', None)
    # service = request.data.get('service', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    promotion_name = request.data.get('promotion_name', '')

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    spend_service = request.data.get('spend_service', None)

    error = []

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # try:
    #     service_id=Service.objects.get(id=service)
    # except Exception as err:
    #     return Response(
    #         {
    #                 'status' : False,
    #                 'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
    #                 'response' : {
    #                 'message' : 'Service not found',
    #                 'error_message' : str(err),
    #             }
    #         }

    #     )

    spend_some_amount = SpendSomeAmount.objects.create(
        user=user,
        business=business,
        promotion_name=promotion_name,
        # service = service_id,
        # spend_amount = spend_amount,
    )

    if spend_service is not None:
        if type(spend_service) == str:
            spend_service = spend_service.replace("'", '"')
            spend_service = json.loads(spend_service)
        else:
            pass
        for cat in spend_service:
            try:
                service = cat.get('service', None)
                discount = cat.get('spend_amount', None)

                try:
                    service_id = Service.objects.get(id=str(service))
                except:
                    pass
                SpendSomeAmountAndGetDiscount.objects.create(
                    # user = user,
                    # business = business,

                    spandsomeamount=spend_some_amount,
                    service=service_id,
                    spend_amount=discount
                )

            except Exception as err:
                error.append(str(err))

    date_res = DateRestrictions.objects.create(
        spendsomeamount=spend_some_amount,
        start_date=start_date,
        end_date=end_date,
    )

    if location is not None:
        if type(location) == str:
            location = json.loads(location)

        elif type(location) == list:
            pass

        for loc in location:
            try:
                address = BusinessAddress.objects.get(id=loc)
                date_res.business_address.add(address)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            try:
                day = dayres.get('day', None)

                DayRestrictions.objects.create(
                    spendsomeamount=spend_some_amount,
                    day=day,
                )

            except Exception as err:
                error.append(str(err))

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:

            try:
                date = bl_date.get('date', None)
                BlockDate.objects.create(
                    spendsomeamount=spend_some_amount,
                    date=date,
                )

            except Exception as err:
                error.append(str(err))

    serializers = PromtoionsSerializers.SpendSomeAmountSerializers(spend_some_amount, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Spend Amount Created Successfully!',
                'error_message': None,
                'errors': error,
                'spendamount': serializers.data,

            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_spend_some_amount(request):
    spend_id = request.data.get('id', None)

    spend_service = request.data.get('spend_service', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    promotion_name = request.data.get('promotion_name', '')

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    error = []

    if spend_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        spend_some = SpendSomeAmount.objects.get(id=spend_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Spend Some Amount Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    spend_some.promotion_name = promotion_name
    spend_some.save()

    try:
        daterestriction = DateRestrictions.objects.get(spendsomeamount=spend_some.id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'daterestriction Service Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if start_date:
        daterestriction.start_date = start_date
    if end_date:
        daterestriction.end_date = end_date
    daterestriction.save()

    if location is not None:
        if type(location) == str:
            location = json.loads(location)
        elif type(location) == list:
            pass
        daterestriction.business_address.clear()
        for loc in location:
            try:
                loca = BusinessAddress.objects.get(id=loc)
                daterestriction.business_address.add(loca)
            except Exception as err:
                error.append(str(err))

    if spend_service is not None:
        if type(spend_service) == str:
            spend_service = spend_service.replace("'", '"')
            spend_service = json.loads(spend_service)
        else:
            pass
        for cat in spend_service:
            id = cat.get('id', None)
            service_group = cat.get('service', None)
            discount = cat.get('spend_amount', None)
            is_deleted = cat.get('is_deleted', None)
            try:
                service_grp = Service.objects.get(id=str(service_group))
            except:
                pass
            if id is not None:
                try:
                    ser_grp = SpendSomeAmountAndGetDiscount.objects.get(id=str(id))
                    if str(is_deleted) == "True":
                        ser_grp.delete()
                        continue
                    ser_grp.service = service_grp
                    ser_grp.spend_amount = discount
                    ser_grp.save()
                except Exception as err:
                    error.append(str(err))
            else:
                SpendSomeAmountAndGetDiscount.objects.create(
                    spandsomeamount=spend_some,

                    service=service_grp,
                    spend_amount=discount
                )

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id=str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()

                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text=f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    spendsomeamount=spend_some,
                    day=day,
                )

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:
            date = bl_date.get('date', None)
            is_deleted = bl_date.get('is_deleted', None)
            id = bl_date.get('id', None)
            if id is not None:
                try:
                    block_date = BlockDate.objects.get(id=str(id))
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date = date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
                BlockDate.objects.create(
                    spendsomeamount=spend_some,
                    date=date,
                )
    serializers = PromtoionsSerializers.SpendSomeAmountSerializers(spend_some, data=request.data, partial=True,
                                                                   context={'request': request})
    if serializers.is_valid():
        serializers.save()
    else:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'response': {
                    'message': 'Invialid Data',
                    'error_message': str(serializers.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Spend Some Discount Updated Successfully!',
                'error_message': None,
                'error': error,
                'spendsome': serializers.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_spend_some_amount(request):
    spend_id = request.data.get('id', None)

    if spend_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        spend_discount = SpendSomeAmount.objects.get(id=spend_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Spend Some Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    spend_discount.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Spend Some Discount deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_spend_some_amount(request):
    spend_discount = SpendSomeAmount.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = PromtoionsSerializers.SpendSomeAmountSerializers(spend_discount, many=True,
                                                                  context={'request': request})

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Spend Some Discount',
                'error_message': None,
                'spendsome': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_fixed_price_service(request):
    user = request.user
    business_id = request.data.get('business', None)

    spend_amount = request.data.get('spendAmount', None)
    duration = request.data.get('duration', None)
    service = request.data.get('service', None)
    promotion_name = request.data.get('promotion_name', '')

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    error = []

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    fixed_price = FixedPriceService.objects.create(
        user=user,
        business=business,

        # duration = duration,
        spend_amount=spend_amount,
        promotion_name=promotion_name,
    )
    if service is not None:
        if type(service) == str:
            service = json.loads(service)

        elif type(service) == list:
            pass

        for ser in service:
            try:
                service_id = Service.objects.get(id=ser)
                fixed_price.service.add(service_id)
            except Exception as err:
                error.append(str(err))

    date_res = DateRestrictions.objects.create(
        fixedpriceservice=fixed_price,
        start_date=start_date,
        end_date=end_date,
    )

    if location is not None:
        if type(location) == str:
            location = json.loads(location)

        elif type(location) == list:
            pass

        for loc in location:
            try:
                address = BusinessAddress.objects.get(id=loc)
                date_res.business_address.add(address)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            try:
                day = dayres.get('day', None)

                DayRestrictions.objects.create(
                    fixedpriceservice=fixed_price,
                    day=day,
                )

            except Exception as err:
                error.append(str(err))

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:

            try:
                date = bl_date.get('date', None)
                BlockDate.objects.create(
                    fixedpriceservice=fixed_price,
                    date=date,
                )

            except Exception as err:
                error.append(str(err))

    serializers = PromtoionsSerializers.FixedPriceServiceSerializers(fixed_price, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Fixed Price Service Created Successfully!',
                'error_message': None,
                'errors': error,
                'fixedprice': serializers.data,

            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_fixed_price_service(request):
    fixed_id = request.data.get('id', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)
    promotion_name = request.data.get('promotion_name', '')

    spend_amount = request.data.get('spendAmount', None)
    duration = request.data.get('duration', None)
    service = request.data.get('service', None)

    error = []

    if fixed_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        fixed_price = FixedPriceService.objects.get(id=fixed_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Fixed Service Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    fixed_price.promotion_name = promotion_name
    fixed_price.save()

    if service is not None:
        if type(service) == str:
            service = json.loads(service)
        elif type(service) == list:
            pass
        fixed_price.service.clear()
        for ser in service:
            try:
                service_id = Service.objects.get(id=ser)
                fixed_price.service.add(service_id)
            except Exception as err:
                error.append(str(err))

    try:
        daterestriction = DateRestrictions.objects.get(fixedpriceservice=fixed_price.id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'daterestriction Service Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if start_date:
        daterestriction.start_date = start_date
    if end_date:
        daterestriction.end_date = end_date
    daterestriction.save()

    if location is not None:
        if type(location) == str:
            location = json.loads(location)
        elif type(location) == list:
            pass
        daterestriction.business_address.clear()
        for loc in location:
            try:
                loca = BusinessAddress.objects.get(id=loc)
                daterestriction.business_address.add(loca)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id=str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()

                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text=f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    fixedpriceservice=fixed_price,
                    day=day,
                )

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:
            date = bl_date.get('date', None)
            is_deleted = bl_date.get('is_deleted', None)
            id = bl_date.get('id', None)
            if id is not None:
                try:
                    block_date = BlockDate.objects.get(id=str(id))
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date = date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
                BlockDate.objects.create(
                    fixedpriceservice=fixed_price,
                    date=date,
                )

    serializers = PromtoionsSerializers.FixedPriceServiceSerializers(fixed_price, data=request.data, partial=True,
                                                                     context={'request': request})
    if serializers.is_valid():
        serializers.save()
    else:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'response': {
                    'message': 'Invialid Data',
                    'error_message': str(serializers.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Fixed Price Service Updated Successfully!',
                'error_message': None,
                'error': error,
                'fixedprice': serializers.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_fixed_price_service(request):
    fixed_id = request.data.get('id', None)

    if fixed_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        fixed_price = FixedPriceService.objects.get(id=fixed_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Fixed Price Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    fixed_price.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Fixed Price Service deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_free_service(request):
    user = request.user
    business_id = request.data.get('business', None)

    # spend_amount = request.data.get('spendAmount', None)
    # duration = request.data.get('duration', None)
    freeservice = request.data.get('freeService', None)
    service = request.data.get('service', None)
    promotion_name = request.data.get('promotion_name', '')

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    error = []

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        freeservice_id = Service.objects.get(id=str(freeservice))
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.SERVICE_NOT_FOUND_4035,
                'response': {
                    'message': 'Free Service not found',
                    'error_message': str(err),
                }
            }
        )

    mention_number = MentionedNumberService.objects.create(
        user=user,
        business=business,

        service=freeservice_id,
        promotion_name=promotion_name,
        # duration = duration,
        # spend_amount = spend_amount,
    )
    if service is not None:
        if type(service) == str:
            service = service.replace("'", '"')
            service = json.loads(service)

        elif type(service) == list:
            pass

        for ser in service:
            try:
                id = ser.get('service', None)
                quantity = ser.get('quantity', None)

                try:
                    service_id = Service.objects.get(id=str(id))
                except Exception as err:
                    error.append(str(err))

                FreeService.objects.create(
                    mentionnumberservice=mention_number,
                    quantity=quantity,
                    service=service_id
                )

            except Exception as err:
                error.append(str(err))

    date_res = DateRestrictions.objects.create(
        mentionednumberservice=mention_number,
        start_date=start_date,
        end_date=end_date,
    )

    if location is not None:
        if type(location) == str:
            location = json.loads(location)

        elif type(location) == list:
            pass

        for loc in location:
            try:
                address = BusinessAddress.objects.get(id=loc)
                date_res.business_address.add(address)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            try:
                day = dayres.get('day', None)

                DayRestrictions.objects.create(
                    mentionednumberservice=mention_number,
                    day=day,
                )

            except Exception as err:
                error.append(str(err))

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:

            try:
                date = bl_date.get('date', None)
                BlockDate.objects.create(
                    mentionednumberservice=mention_number,
                    date=date,
                )

            except Exception as err:
                error.append(str(err))

    serializers = PromtoionsSerializers.MentionedNumberServiceSerializers(mention_number, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Free Service Created Successfully!',
                'error_message': None,
                'errors': error,
                'freservice': serializers.data,

            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_free_service(request):
    mention_price_id = request.data.get('id', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)
    promotion_name = request.data.get('promotion_name', None)

    service = request.data.get('service', None)
    freeService = request.data.get('freeService', None)

    error = []

    if mention_price_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        mention_service = MentionedNumberService.objects.get(id=mention_price_id)

    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Mention number Service Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    mention_service.promotion_name = promotion_name
    mention_service.save()

    if freeService:
        try:
            services = Service.objects.get(id=str(freeService))
            mention_service.service = services
            mention_service.save()
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.SERVICE_NOT_FOUND_4035,
                    'response': {
                        'message': 'Free Service not found',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

    try:
        daterestriction = DateRestrictions.objects.get(mentionednumberservice=mention_service.id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'daterestriction Service Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if start_date:
        daterestriction.start_date = start_date
    if end_date:
        daterestriction.end_date = end_date
    daterestriction.save()

    if location is not None:
        if type(location) == str:
            location = json.loads(location)
        elif type(location) == list:
            pass
        daterestriction.business_address.clear()
        for loc in location:
            try:
                loca = BusinessAddress.objects.get(id=loc)
                daterestriction.business_address.add(loca)
            except Exception as err:
                error.append(str(err))

    if service is not None:
        if type(service) == str:
            service = service.replace("'", '"')
            service = json.loads(service)
        else:
            pass
        for ser in service:
            id_service = ser.get('id', None)
            service_id = ser.get('service', None)
            quantity = ser.get('quantity', None)

            try:
                services = Service.objects.get(id=service_id)
            except Exception as err:
                error.append(str(err))

            if id_service is not None:
                try:
                    free_service = FreeService.objects.get(id=str(id_service))
                    is_deleted = ser.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        free_service.delete()
                        continue
                    free_service.quantity = quantity
                    free_service.service = services
                    free_service.save()

                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text=f'{str(err)}')
            else:
                FreeService.objects.create(
                    mentionnumberservice=mention_service,

                    quantity=quantity,
                    service=services

                )

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id=str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()

                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text=f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    mentionednumberservice=mention_service,
                    day=day,
                )

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:
            date = bl_date.get('date', None)
            is_deleted = bl_date.get('is_deleted', None)
            id = bl_date.get('id', None)
            if id is not None:
                try:
                    block_date = BlockDate.objects.get(id=str(id))
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date = date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
                BlockDate.objects.create(
                    mentionednumberservice=mention_service,
                    date=date,
                )

    serializers = PromtoionsSerializers.MentionedNumberServiceSerializers(
        mention_service, )  # data=request.data, partial=True, context={'request' : request})

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Free Price Service Updated Successfully!',
                'error_message': None,
                'error': error,
                'freservice': serializers.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_free_service(request):
    mention_id = request.data.get('id', None)

    if mention_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        mention_price = MentionedNumberService.objects.get(id=mention_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Free Price Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    mention_price.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Free Price Service deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_bundle_fixed_price(request):
    user = request.user
    business_id = request.data.get('business', None)

    spend_amount = request.data.get('spend_amount', None)
    # duration = request.data.get('duration', None)
    service = request.data.get('service', None)
    promotion_name = request.data.get('promotion_name', None)
    # service = request.data.get('service', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    error = []

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    bundle_fixed = BundleFixed.objects.create(
        user=user,
        business=business,

        spend_amount=spend_amount,
        promotion_name=promotion_name,
    )
    if service is not None:
        if type(service) == str:
            service = json.loads(service)

        elif type(service) == list:
            pass

        for ser in service:
            try:
                servic = Service.objects.get(id=str(ser))
                bundle_fixed.service.add(servic)
            except Exception as err:
                error.append(str(err))

    date_res = DateRestrictions.objects.create(
        bundlefixed=bundle_fixed,
        start_date=start_date,
        end_date=end_date,
    )

    if location is not None:
        if type(location) == str:
            location = json.loads(location)

        elif type(location) == list:
            pass

        for loc in location:
            try:
                address = BusinessAddress.objects.get(id=loc)
                date_res.business_address.add(address)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            try:
                day = dayres.get('day', None)

                DayRestrictions.objects.create(
                    bundlefixed=bundle_fixed,
                    day=day,
                )

            except Exception as err:
                error.append(str(err))

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:

            try:
                date = bl_date.get('date', None)
                BlockDate.objects.create(
                    bundlefixed=bundle_fixed,
                    date=date,
                )

            except Exception as err:
                error.append(str(err))

    serializers = PromtoionsSerializers.BundleFixedSerializers(bundle_fixed, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Bundle fixed Services Created Successfully!',
                'error_message': None,
                'errors': error,
                'bundlefixed': serializers.data,

            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_bundle_fixed_price(request):
    bundle_id = request.data.get('id', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)
    promotion_name = request.data.get('promotion_name', '')

    service = request.data.get('service', None)
    spend_amount = request.data.get('spend_amount', None)

    error = []

    if bundle_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        bundle_fixed = BundleFixed.objects.get(id=bundle_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Mention number Service Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    bundle_fixed.promotion_name = promotion_name
    bundle_fixed.save()
    if spend_amount:
        bundle_fixed.spend_amount = spend_amount
        bundle_fixed.save()

    if service is not None:
        if type(service) == str:
            service = json.loads(service)
        elif type(service) == list:
            pass
        bundle_fixed.service.clear()
        for ser in service:
            try:
                servic = Service.objects.get(id=ser)
                bundle_fixed.service.add(servic)
            except Exception as err:
                error.append(str(err))

    try:
        daterestriction = DateRestrictions.objects.get(bundlefixed=bundle_fixed.id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'daterestriction Service Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if start_date:
        daterestriction.start_date = start_date
    if end_date:
        daterestriction.end_date = end_date
    daterestriction.save()

    if location is not None:
        if type(location) == str:
            location = json.loads(location)
        elif type(location) == list:
            pass
        daterestriction.business_address.clear()
        for loc in location:
            try:
                loca = BusinessAddress.objects.get(id=loc)
                daterestriction.business_address.add(loca)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id=str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()

                except Exception as err:
                    error.append(str(err))
                    # ExceptionRecord.objects.create(text = f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    bundlefixed=bundle_fixed,
                    day=day,
                )

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:
            date = bl_date.get('date', None)
            is_deleted = bl_date.get('is_deleted', None)
            id = bl_date.get('id', None)
            if id is not None:
                try:
                    block_date = BlockDate.objects.get(id=str(id))
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date = date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
                BlockDate.objects.create(
                    bundlefixed=bundle_fixed,
                    date=date,
                )

    serializers = PromtoionsSerializers.BundleFixedSerializers(
        bundle_fixed, )  # data=request.data, partial=True, context={'request' : request})

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Bundle Fixed Service Updated Successfully!',
                'error_message': None,
                'error': error,
                'bundlefixed': serializers.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_bundle_fixed_price(request):
    bundle_id = request.data.get('id', None)

    if bundle_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        bundle_fixed = BundleFixed.objects.get(id=bundle_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Bundle Fixed Price Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    bundle_fixed.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Bundle Fixed Service deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_retail_get_service(request):
    user = request.user
    business_id = request.data.get('business', None)

    promotion = request.data.get('promotion', None)
    promotion_name = request.data.get('promotion_name', '')

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    error = []

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    retail_service = RetailAndGetService.objects.create(
        user=user,
        business=business,
        promotion_name=promotion_name,
    )

    if promotion is not None:
        if type(promotion) == str:
            promotion = promotion.replace("'", '"')
            promotion = json.loads(promotion)
        else:
            pass
        for pro in promotion:
            try:
                product = pro.get('product', None)
                brand = pro.get('brand', None)
                service = pro.get('service', None)
                pro_type = pro.get('type', 'Product')

                try:
                    product_id = Product.objects.get(id=product)
                except Exception as err:
                    product_id = None
                    pass

                try:
                    brand = Brand.objects.get(id=brand)
                except Exception as err:
                    brand = None
                    pass

                try:
                    service_id = Service.objects.get(id=service)
                except Exception as err:
                    pass

                ProductAndGetSpecific.objects.create(
                    retailandservice=retail_service,
                    product=product_id,
                    brand=brand,
                    service=service_id,
                    promotion_type=pro_type
                )

            except Exception as err:
                error.append(str(err))

    date_res = DateRestrictions.objects.create(
        retailandservice=retail_service,
        start_date=start_date,
        end_date=end_date,
    )

    if location is not None:
        if type(location) == str:
            location = json.loads(location)

        elif type(location) == list:
            pass

        for loc in location:
            try:
                address = BusinessAddress.objects.get(id=loc)
                date_res.business_address.add(address)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            try:
                day = dayres.get('day', None)

                DayRestrictions.objects.create(
                    retailandservice=retail_service,
                    day=day,
                )

            except Exception as err:
                error.append(str(err))

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:

            try:
                date = bl_date.get('date', None)
                BlockDate.objects.create(
                    retailandservice=retail_service,
                    date=date,
                )

            except Exception as err:
                error.append(str(err))

    serializers = PromtoionsSerializers.RetailAndGetServiceSerializers(retail_service, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Retail and get Service Created Successfully!',
                'error_message': None,
                'errors': error,
                'retail': serializers.data,

            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_retail_get_service(request):
    retail_id = request.data.get('id', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)
    promotion_name = request.data.get('promotion_name', '')

    promotion = request.data.get('promotion', None)

    error = []

    if retail_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        retail_price = RetailAndGetService.objects.get(id=retail_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Retail Service Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    retail_price.promotion_name = promotion_name
    retail_price.save()

    if promotion is not None:
        if type(promotion) == str:
            promotion = promotion.replace("'", '"')
            promotion = json.loads(promotion)
        else:
            pass
        for pro in promotion:
            id = pro.get('id', None)
            product = pro.get('product', None)
            brand = pro.get('brand', None)
            promotion_type = pro.get('type', None)
            service = pro.get('service', None)

            try:
                product_id = Product.objects.get(id=product)
            except Exception as err:
                product_id = None

            try:
                brand = Brand.objects.get(id=brand)
            except Exception as err:
                brand = None

            try:
                service_id = Service.objects.get(id=service)
            except Exception as err:
                pass

            if id is not None:
                try:
                    productandget = ProductAndGetSpecific.objects.get(id=str(id))
                    is_deleted = pro.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        productandget.delete()
                        continue
                    productandget.product = product_id
                    if promotion_type:
                        productandget.promotion_type = promotion_type
                    productandget.brand = brand
                    productandget.service = service_id
                    productandget.save()

                except Exception as err:
                    error.append(str(err))
            else:
                ProductAndGetSpecific.objects.create(
                    retailandservice=retail_price,
                    brand=brand,
                    promotion_type=promotion_type,
                    product=product_id,
                    service=service_id,
                )

    try:
        daterestriction = DateRestrictions.objects.get(retailandservice=retail_price.id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'daterestriction Service Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if start_date:
        daterestriction.start_date = start_date
    if end_date:
        daterestriction.end_date = end_date
    daterestriction.save()

    if location is not None:
        if type(location) == str:
            location = json.loads(location)
        elif type(location) == list:
            pass
        daterestriction.business_address.clear()
        for loc in location:
            try:
                loca = BusinessAddress.objects.get(id=loc)
                daterestriction.business_address.add(loca)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id=str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()

                except Exception as err:
                    error.append(str(err))
            else:
                DayRestrictions.objects.create(
                    retailandservice=retail_price,
                    day=day,
                )

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:
            date = bl_date.get('date', None)
            is_deleted = bl_date.get('is_deleted', None)
            id = bl_date.get('id', None)
            if id is not None:
                try:
                    block_date = BlockDate.objects.get(id=str(id))
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date = date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
                BlockDate.objects.create(
                    retailandservice=retail_price,
                    date=date,
                )

    serializers = PromtoionsSerializers.RetailAndGetServiceSerializers(
        retail_price)  # data=request.data, partial=True, context={'request' : request})
    # if serializers.is_valid():
    #     serializers.save()
    # else:
    #     return Response(
    #     {
    #         'status' : False,
    #         'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
    #         'response' : {
    #             'message' : 'Invialid Data',
    #             'error_message' : str(serializers.errors),
    #         }
    #     },
    #     status=status.HTTP_404_NOT_FOUND
    # )
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Retail Service Updated Successfully!',
                'error_message': None,
                'error': error,
                'retail': serializers.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_retail_get_service(request):
    retail_id = request.data.get('id', None)

    if retail_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        retail_price = RetailAndGetService.objects.get(id=retail_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Retail Service Price Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    retail_price.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Retail Service deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user_restricted_discount(request):
    user = request.user
    business_id = request.data.get('business', None)

    corporate_type = request.data.get('corporate_type', None)
    discount_percentage = request.data.get('discount_percentage', None)
    clients = request.data.get('client', None)
    promotion_name = request.data.get('promotion_name', '')

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    products = request.data.get('product', [])
    services = request.data.get('services', [])
    vouchers = request.data.get('voucher', [])

    error = []

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    usr_res = UserRestrictedDiscount.objects.create(
        user=user,
        business=business,
        promotion_name=promotion_name,
        corporate_type=corporate_type,
        discount_percentage=discount_percentage
    )
    if clients is not None:
        if type(clients) == str:
            clients = json.loads(clients)

        elif type(clients) == list:
            pass

        for cl in clients:
            try:
                cli = Client.objects.get(id=str(cl))
                usr_res.client.add(cli)
            except Exception as err:
                error.append(str(err))

    date_res = DateRestrictions.objects.create(
        userrestricteddiscount=usr_res,
        start_date=start_date,
        end_date=end_date,
    )

    if location is not None:
        if type(location) == str:
            location = json.loads(location)

        elif type(location) == list:
            pass

        for loc in location:
            try:
                address = BusinessAddress.objects.get(id=loc)
                date_res.business_address.add(address)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            try:
                day = dayres.get('day', None)

                DayRestrictions.objects.create(
                    userrestricteddiscount=usr_res,
                    day=day,
                )

            except Exception as err:
                error.append(str(err))

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:

            try:
                date = bl_date.get('date', None)
                BlockDate.objects.create(
                    userrestricteddiscount=usr_res,
                    date=date,
                )

            except Exception as err:
                error.append(str(err))

    if type(products) == str:
        try:
            products = json.loads(products)
        except:
            products = []

    if type(products) == list:
        for product_id in products:
            PromotionExcludedItem.objects.create(
                object_type='User_Restricted_discount',
                object_id=f'{usr_res.id}',
                excluded_type='Product',
                excluded_id=product_id,
                is_active=True,
            )

    if type(services) == str:
        try:
            services = json.loads(services)
        except:
            services = []

    if type(services) == list:
        for service_id in services:
            PromotionExcludedItem.objects.create(
                object_type='User_Restricted_discount',
                object_id=f'{usr_res.id}',
                excluded_type='Service',
                excluded_id=service_id,
                is_active=True,
            )

    if type(vouchers) == str:
        try:
            vouchers = json.loads(vouchers)
        except:
            vouchers = []

    if type(vouchers) == list:
        for voucher_id in vouchers:
            PromotionExcludedItem.objects.create(
                object_type='User_Restricted_discount',
                object_id=f'{usr_res.id}',
                excluded_type='Voucher',
                excluded_id=voucher_id,
                is_active=True,
            )

    serializers = PromtoionsSerializers.UserRestrictedDiscountSerializers(usr_res, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'User Restricted Discount Created Successfully!',
                'error_message': None,
                'errors': error,
                'userRestricted': serializers.data,

            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_restricted_discount(request):
    res_id = request.data.get('id', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    clients = request.data.get('client', None)
    corporate_type = request.data.get('corporate_type', None)
    discount_percentage = request.data.get('discount_percentage', None)
    promotion_name = request.data.get('promotion_name', '')

    products = request.data.get('product', [])
    services = request.data.get('services', [])
    vouchers = request.data.get('voucher', [])

    error = []

    if res_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usr_res = UserRestrictedDiscount.objects.get(id=res_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'User Restricted Discount Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    usr_res.promotion_name = promotion_name
    usr_res.save()

    if corporate_type:
        usr_res.corporate_type = corporate_type
        usr_res.save()

    if discount_percentage:
        usr_res.discount_percentage = discount_percentage
        usr_res.save()

    if clients is not None:
        if type(clients) == str:
            clients = json.loads(clients)
        elif type(clients) == list:
            pass
        usr_res.client.clear()
        for cl in clients:
            try:
                cli = Client.objects.get(id=str(cl))
                usr_res.client.add(cli)
            except Exception as err:
                error.append(str(err))

    try:
        daterestriction = DateRestrictions.objects.get(userrestricteddiscount=usr_res.id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'daterestriction Service Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if start_date:
        daterestriction.start_date = start_date
    if end_date:
        daterestriction.end_date = end_date
    daterestriction.save()

    if location is not None:
        if type(location) == str:
            location = json.loads(location)
        elif type(location) == list:
            pass
        daterestriction.business_address.clear()
        for loc in location:
            try:
                loca = BusinessAddress.objects.get(id=loc)
                daterestriction.business_address.add(loca)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id=str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()

                except Exception as err:
                    error.append(str(err))
                    # ExceptionRecord.objects.create(text = f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    userrestricteddiscount=usr_res,
                    day=day,
                )

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:
            date = bl_date.get('date', None)
            is_deleted = bl_date.get('is_deleted', None)
            id = bl_date.get('id', None)
            if id is not None:
                try:
                    block_date = BlockDate.objects.get(id=str(id))
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date = date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
                BlockDate.objects.create(
                    userrestricteddiscount=usr_res,
                    date=date,
                )
    if type(products) == str:
        try:
            products = json.loads(products)
        except:
            products = []

    PromotionExcludedItem.objects.filter(
        object_type='User_Restricted_discount',
        object_id=f'{usr_res.id}',
        excluded_type='Product',
        is_active=True,
    ).exclude(
        excluded_id__in=products,
    ).delete()

    if type(products) == list:
        for product_id in products:
            PromotionExcludedItem.objects.get_or_create(
                object_type='User_Restricted_discount',
                object_id=f'{usr_res.id}',
                excluded_type='Product',
                excluded_id=product_id,
                is_active=True,
            )

    if type(services) == str:
        try:
            services = json.loads(services)
        except:
            services = []

    PromotionExcludedItem.objects.filter(
        object_type='User_Restricted_discount',
        object_id=f'{usr_res.id}',
        excluded_type='Service',
        is_active=True,
    ).exclude(
        excluded_id__in=services,
    ).delete()

    if type(services) == list:
        for service_id in services:
            PromotionExcludedItem.objects.get_or_create(
                object_type='User_Restricted_discount',
                object_id=f'{usr_res.id}',
                excluded_type='Service',
                excluded_id=service_id,
                is_active=True,
            )

    if type(vouchers) == str:
        try:
            vouchers = json.loads(vouchers)
        except:
            vouchers = []

    PromotionExcludedItem.objects.filter(
        object_type='User_Restricted_discount',
        object_id=f'{usr_res.id}',
        excluded_type='Voucher',
        is_active=True,
    ).exclude(
        excluded_id__in=vouchers,
    ).delete()

    if type(vouchers) == list:
        for voucher_id in vouchers:
            PromotionExcludedItem.objects.get_or_create(
                object_type='User_Restricted_discount',
                object_id=f'{usr_res.id}',
                excluded_type='Voucher',
                excluded_id=voucher_id,
                is_active=True,
            )

    serializers = PromtoionsSerializers.UserRestrictedDiscountSerializers(
        usr_res)  # data=request.data, partial=True, context={'request' : request})

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'User Restricted Discount Updated Successfully!',
                'error_message': None,
                'error': error,
                'userRestricted': serializers.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_restricted_discount(request):
    res_id = request.data.get('id', None)

    if res_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user_res = UserRestrictedDiscount.objects.get(id=res_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'User Restricted Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    user_res.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'User Restricted Discount deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_complimentrydiscount(request):
    user = request.user
    business_id = request.data.get('business', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    promotion_name = request.data.get('promotion_name', '')

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    freeservice = request.data.get('freeservice', None)

    error = []

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    complimentry_discount = ComplimentaryDiscount.objects.create(
        user=user,
        business=business,
        promotion_name=promotion_name,
    )

    date_res = DateRestrictions.objects.create(
        complimentary=complimentry_discount,
        start_date=start_date,
        end_date=end_date,
    )

    if location is not None:
        if type(location) == str:
            location = json.loads(location)

        elif type(location) == list:
            pass

        for loc in location:
            try:
                address = BusinessAddress.objects.get(id=loc)
                date_res.business_address.add(address)
            except Exception as err:
                error.append(str(err))

    if freeservice is not None:
        if type(freeservice) == str:
            freeservice = freeservice.replace("'", '"')
            freeservice = json.loads(freeservice)
        else:
            pass
        for ser in freeservice:
            try:
                service_id = ser.get('service', None)
                discount_percentage = ser.get('discount_percentage', None)
                discount_duration = ser.get('discount_duration', None)

                try:
                    service = Service.objects.get(id=str(service_id))
                except:
                    pass
                DiscountOnFreeService.objects.create(
                    complimentary=complimentry_discount,

                    service=service,
                    discount_percentage=discount_percentage,
                    discount_duration=discount_duration,
                )

            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            try:
                day = dayres.get('day', None)

                DayRestrictions.objects.create(
                    complimentary=complimentry_discount,
                    day=day,
                )

            except Exception as err:
                error.append(str(err))

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:

            try:
                date = bl_date.get('date', None)
                BlockDate.objects.create(
                    complimentary=complimentry_discount,
                    date=date,
                )

            except Exception as err:
                error.append(str(err))

    serializers = PromtoionsSerializers.ComplimentaryDiscountSerializers(complimentry_discount,
                                                                         context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Complimentary Discount Created Successfully!',
                'error_message': None,
                'errors': error,
                'complimentry': serializers.data,

            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_complimentrydiscount(request):
    complimentry_id = request.data.get('id', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    freeservice = request.data.get('freeservice', None)
    promotion_name = request.data.get('promotion_name', '')

    error = []

    if complimentry_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        complimentry_discount = ComplimentaryDiscount.objects.get(id=complimentry_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Complimentry Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    complimentry_discount.promotion_name = promotion_name
    complimentry_discount.save()

    if freeservice is not None:
        if type(freeservice) == str:
            freeservice = freeservice.replace("'", '"')
            freeservice = json.loads(freeservice)
        else:
            pass
        for ser in freeservice:
            id = ser.get('id', None)
            discount_percentage = ser.get('discount_percentage', None)
            discount_duration = ser.get('discount_duration', None)
            service = ser.get('service', None)
            is_deleted = ser.get('is_deleted', None)
            try:
                service_id = Service.objects.get(id=str(service))
            except:
                pass
            if id is not None:
                try:
                    free_ser = DiscountOnFreeService.objects.get(id=str(id))
                    if str(is_deleted) == "True":
                        free_ser.delete()
                        continue
                    free_ser.discount_percentage = discount_percentage
                    free_ser.discount_duration = discount_duration
                    free_ser.service = service_id
                    free_ser.save()
                except Exception as err:
                    error.append(str(err))
            else:
                DiscountOnFreeService.objects.create(
                    complimentary=complimentry_discount,

                    service=service_id,
                    discount_percentage=discount_percentage,
                    discount_duration=discount_duration,
                )

    try:
        daterestriction = DateRestrictions.objects.get(complimentary=complimentry_discount.id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'daterestriction Service Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if start_date:
        daterestriction.start_date = start_date
    if end_date:
        daterestriction.end_date = end_date
    daterestriction.save()

    if location is not None:
        if type(location) == str:
            location = json.loads(location)
        elif type(location) == list:
            pass
        daterestriction.business_address.clear()
        for loc in location:
            try:
                loca = BusinessAddress.objects.get(id=loc)
                daterestriction.business_address.add(loca)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id=str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()

                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text=f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    complimentary=complimentry_discount,
                    day=day,
                )

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:
            date = bl_date.get('date', None)
            is_deleted = bl_date.get('is_deleted', None)
            id = bl_date.get('id', None)
            if id is not None:
                try:
                    block_date = BlockDate.objects.get(id=str(id))
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date = date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
                BlockDate.objects.create(
                    complimentary=complimentry_discount,
                    date=date,
                )

    serializers = PromtoionsSerializers.ComplimentaryDiscountSerializers(complimentry_discount,
                                                                         context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Complimentry Discount Updated Successfully!',
                'error_message': None,
                'error': error,
                'complimentry': serializers.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_complimentrydiscount(request):
    complimentry_id = request.data.get('id', None)

    if complimentry_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        complimentry = ComplimentaryDiscount.objects.get(id=complimentry_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Complimentry Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    complimentry.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Complimentry Discount deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_packagesdiscount(request):
    user = request.user
    business_id = request.data.get('business', None)

    service_duration = request.data.get('packages', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    error = []

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    package_discount = PackagesDiscount.objects.create(
        user=user,
        business=business,
    )

    if service_duration is not None:
        if type(service_duration) == str:
            service_duration = service_duration.replace("'", '"')
            service_duration = json.loads(service_duration)
        else:
            pass
        for pro in service_duration:
            try:
                service_duration = pro.get('service_duration', None)
                package_duration = pro.get('package_duration', None)
                total_amount = pro.get('total_amount', None)
                service = pro.get('service', None)
                # try:
                #     service_id = Service.objects.get(id = service)
                # except Exception as err:
                #     pass

                durationservice = ServiceDurationForSpecificTime.objects.create(
                    package=package_discount,
                    # service = service_id,

                    service_duration=service_duration,
                    package_duration=package_duration,
                    total_amount=total_amount

                )
                if service is not None:
                    if type(service) == str:
                        service = json.loads(service)

                    elif type(service) == list:
                        pass

                    for ser in service:
                        try:
                            service_id = Service.objects.get(id=ser)
                            durationservice.service.add(service_id)
                        except Exception as err:
                            error.append(str(err))

            except Exception as err:
                error.append(str(err))

    date_res = DateRestrictions.objects.create(
        package=package_discount,
        start_date=start_date,
        end_date=end_date,
    )

    if location is not None:
        if type(location) == str:
            location = json.loads(location)

        elif type(location) == list:
            pass

        for loc in location:
            try:
                address = BusinessAddress.objects.get(id=loc)
                date_res.business_address.add(address)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            try:
                day = dayres.get('day', None)

                DayRestrictions.objects.create(
                    package=package_discount,
                    day=day,
                )

            except Exception as err:
                error.append(str(err))

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:

            try:
                date = bl_date.get('date', None)
                BlockDate.objects.create(
                    package=package_discount,
                    date=date,
                )

            except Exception as err:
                error.append(str(err))

    serializers = PromtoionsSerializers.PackagesDiscountSerializers(package_discount, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Packages Discount Created Successfully!',
                'error_message': None,
                'errors': error,
                'packages': serializers.data,

            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_packagesdiscount(request):
    package_id = request.data.get('id', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)

    service_duration = request.data.get('packages', None)

    error = []

    if package_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        package_discount = PackagesDiscount.objects.get(id=package_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Packages Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if service_duration is not None:
        if type(service_duration) == str:
            service_duration = service_duration.replace("'", '"')
            service_duration = json.loads(service_duration)
        else:
            pass
        for pro in service_duration:
            id = pro.get('id', None)
            service_duration = pro.get('service_duration', None)
            package_duration = pro.get('package_duration', None)
            total_amount = pro.get('total_amount', None)
            service = pro.get('service', None)

            # try:
            #     service_id = Service.objects.get(id = service)
            # except Exception as err:
            #     pass

            if id is not None:
                try:
                    productandget = ServiceDurationForSpecificTime.objects.get(id=str(id))
                    is_deleted = pro.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        productandget.delete()
                        continue
                    productandget.service_duration = service_duration
                    productandget.package_duration = package_duration
                    productandget.total_amount = total_amount
                    # productandget.service = service_id
                    productandget.save()
                    if service is not None:
                        if type(service) == str:
                            service = json.loads(service)

                        elif type(service) == list:
                            pass
                        productandget.service.clear()
                        for ser in service:
                            try:
                                service_id = Service.objects.get(id=ser)
                                productandget.service.add(service_id)
                            except Exception as err:
                                error.append(str(err))

                except Exception as err:
                    error.append(str(err))
            else:
                durationservice = ServiceDurationForSpecificTime.objects.create(
                    package=package_discount,
                    # service = service_id,

                    service_duration=service_duration,
                    package_duration=package_duration,
                    total_amount=total_amount
                )
                if service is not None:
                    if type(service) == str:
                        service = json.loads(service)

                    elif type(service) == list:
                        pass
                    # daterestriction.business_address.clear()
                    for ser in service:
                        try:
                            service_id = Service.objects.get(id=ser)
                            durationservice.service.add(service_id)
                        except Exception as err:
                            error.append(str(err))

    try:
        daterestriction = DateRestrictions.objects.get(package=package_discount.id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'daterestriction Service Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if start_date:
        daterestriction.start_date = start_date
    if end_date:
        daterestriction.end_date = end_date
    daterestriction.save()

    if location is not None:
        if type(location) == str:
            location = json.loads(location)
        elif type(location) == list:
            pass
        daterestriction.business_address.clear()
        for loc in location:
            try:
                loca = BusinessAddress.objects.get(id=loc)
                daterestriction.business_address.add(loca)
            except Exception as err:
                error.append(str(err))

    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'", '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id=str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()

                except Exception as err:
                    error.append(str(err))
            else:
                DayRestrictions.objects.create(
                    package=package_discount,
                    day=day,
                )

    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'", '"')
            blockdate = json.loads(blockdate)
        else:
            pass

        for bl_date in blockdate:
            date = bl_date.get('date', None)
            is_deleted = bl_date.get('is_deleted', None)
            id = bl_date.get('id', None)
            if id is not None:
                try:
                    block_date = BlockDate.objects.get(id=str(id))
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date = date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
                BlockDate.objects.create(
                    package=package_discount,
                    date=date,
                )

    serializers = PromtoionsSerializers.PackagesDiscountSerializers(
        package_discount)  # data=request.data, partial=True, context={'request' : request})
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Packages Discount Updated Successfully!',
                'error_message': None,
                'error': error,
                'packages': serializers.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_packagesdiscount(request):
    packages_id = request.data.get('id', None)

    if packages_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        packages = PackagesDiscount.objects.get(id=packages_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Packages Discount Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    packages.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Packages Discount deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def get_availability_date(request):


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def create_coupon(request):
    detail = None
    name = request.data.get('coupon_name', None)
    business = request.data.get('business', None)
    short_description = request.data.get('coupon_description', None)
    coupon_type_value = request.data.get('couponTypeValue', None)
    product_brand = request.data.get('product_brand', [])
    product_brand_discount_percentage = request.data.get('product_brand_discount_percentage', None)
    service_ids = request.data.get('excludedServices', [])
    service_group = request.data.get('service_group', [])
    service_group_brand = request.data.get('specificServiceGroupBrandDiscount', [])
    start_date = request.data.get('startDate', None)
    end_date = request.data.get('endDate', None)
    block_day = request.data.get('block_day', None)
    store_restriction = request.data.get('storeRestrictions', [])
    excluded_products = request.data.get('excludedProducts', [])
    usage_limit = request.data.get('usageLimit', None)
    code = request.data.get('coupon_code', None)
    user_limit = request.data.get('userLimit', None)
    coupon_type = request.data.get('couponType', None)
    days_restriction = request.data.get('dayRestrictions', [])
    amount_spent = request.data.get('amount_spent', None)
    buy_one_type = request.data.get('type', None)
    discounted_percentage = request.data.get('discounted_percentage', None)
    client = request.data.get('clients', 'all')
    location = request.data.get('location', [])
    requested_status = request.data.get('status', False)
    buyOneGetOne = request.data.get('buyOneGetOne', [])
    fixedAmount = request.data.get('fixedAmount', [])
    selectedType = request.data.get('selectedType', None)
    client_type = request.data.get('client_type', None)
    test_data1 = 0
    test_data2 = 0
    error = []
    # try:
    if requested_status == 'true':
        requested_status = True
    else:
        requested_status = False
    code_check = Coupon.objects.filter(code__icontains=code)
    if code_check:
        return Response({"msg": "Coupon already exists"}, status=status.HTTP_400_BAD_REQUEST)
    coupon = Coupon.objects.create(
        name=name,
        amount_spent=amount_spent,
        discounted_percentage=discounted_percentage,
        coupon_type_value=coupon_type_value,
        short_description=short_description,
        buy_one_type=buy_one_type,
        start_date=start_date,
        end_date=end_date,
        coupon_type=coupon_type,
        block_day=block_day,
        usage_limit=usage_limit,
        user_limit=user_limit,
        code=code,
        type='Coupons_Discount',
        requested_status=requested_status,
        client_type=client_type
    )
    if buy_one_type == 'Service':
        coupon.buy_one_get_one_service.set([selectedType])
    if buy_one_type == 'Product':
        coupon.buy_one_get_one_product.set([selectedType])
    if len(buyOneGetOne) > 0:
        buyOneGetOne = json.loads(buyOneGetOne)
    if len(fixedAmount) > 0:
        fixedAmount = json.loads(fixedAmount)
    if len(location) > 0:
        location = json.loads(location)
        coupon.locations.set(location)
        # coupon.business.set(location)
    if len(service_group_brand) > 0:
        service_group_brand = json.loads(service_group_brand)
        for item in service_group_brand:
            service_group = item.get("service_group", None)
            test_data1 = service_group
            service_group_discount = float(item.get("discount", 0))
            brand = item.get("brand", None)
            test_data2 = brand
            brand_discount = float(item.get("brand_discount", 0))
            if brand:
                coupon.brands.set([brand])
                CouponBrand.objects.create(
                    coupon=coupon,
                    brand_id=brand,
                    brand_discount=brand_discount
                )
            if service_group:
                coupon.coupon_service_groups.set([service_group])
                CouponServiceGroup.objects.create(
                    coupon=coupon,
                    service_group_id=service_group,
                    service_group_discount=service_group_discount
                )
    if len(service_ids) > 0:
        service_ids = json.loads(service_ids)
        coupon.excluded_services.set(service_ids)
    if client == 'all':
        pass
        # client_ids = list(Client.objects.values_list('id', flat=True).distinct())
        # client_ids_str = [str(client_id) for client_id in client_ids]
        # coupon.clients.set(client_ids_str)
    if client != 'all':
        client = json.loads(client)
        coupon.clients.set(client)
    if len(excluded_products) > 0:
        excluded_products = json.loads(excluded_products)
        coupon.excluded_products.set(excluded_products)
    if len(product_brand) > 0:
        product_brand = json.loads(product_brand)
        coupon.brand_id.set(product_brand)
    if len(days_restriction) > 0:
        days_restriction = json.loads(days_restriction)
        for day in days_restriction:
            day = day.get("day", None)
            CouponBlockDays.objects.create(day=day, coupon_id=coupon.id)
    if len(store_restriction) > 0:
        store_restriction = json.loads(store_restriction)
        coupon.locations.set(store_restriction)
    serializer = CouponSerializer(coupon, context={'request': request})
    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Coupon created successfully!',
                'error_message': None,
                'errors': error,
                'coupon': serializer.data,

            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['PATCH'])
@permission_classes([AllowAny])
def update_coupon(request):
    id = request.data.get('id', None)
    if id:
        product_brand = request.data.get('product_brand', [])
        service_ids = request.data.get('excludedServices', [])
        service_group_brand = request.data.get('specificServiceGroupBrandDiscount', [])
        store_restriction = request.data.get('storeRestrictions', [])
        excluded_products = request.data.get('excludedProducts', [])
        days_restriction = request.data.get('dayRestrictions', [])
        client = request.data.get('clients', 'all')
        location = request.data.get('location', [])
        requested_status = request.data.get('status', False)
        buyOneGetOne = request.data.get('buyOneGetOne', [])
        fixedAmount = request.data.get('fixedAmount', [])
        selectedType = request.data.get('selectedType', None)
        buy_one_type = request.data.get('type', None)
        coupon_to_filter = request.data.get('coupon_code', None)
        error = []
        # try:
        if requested_status == 'true':
            requested_status = True
        else:
            requested_status = False
        instance = Coupon.objects.get(id=id)
        # code_check = Coupon.objects.filter(code__icontains=coupon_to_filter)
        # if code_check:
        #     code_check= code_check.first()
        #     if code_check
        #     return Response({"msg": "Coupon already exists"}, status=status.HTTP_400_BAD_REQUEST)
        instance.requested_status = requested_status
        instance.name = request.data.get('coupon_name', instance.name)
        instance.short_description = request.data.get('coupon_description', instance.short_description)
        instance.coupon_type_value = request.data.get('couponTypeValue', instance.coupon_type_value)
        instance.start_date = request.data.get('startDate', instance.start_date)
        instance.end_date = request.data.get('endDate', instance.end_date)
        instance.usage_limit = request.data.get('usageLimit', instance.usage_limit)
        instance.code = request.data.get('coupon_code', instance.code)
        instance.user_limit = request.data.get('userLimit', instance.user_limit)
        instance.coupon_type = request.data.get('couponType', instance.coupon_type)
        instance.buy_one_type = request.data.get('type', instance.buy_one_type)
        instance.amount_spent = request.data.get('amount_spent', instance.amount_spent)
        instance.discounted_percentage = request.data.get('discounted_percentage', instance.discounted_percentage)
        instance.client_type = request.data.get('client_type', instance.client_type)
        instance.save()
        
        if buy_one_type == 'Service':
            instance.buy_one_get_one_service.clear()
            instance.buy_one_get_one_service.set([selectedType])
            
            
        if buy_one_type == 'Product':
            instance.buy_one_get_one_product.clear()
            instance.buy_one_get_one_product.set([selectedType])
            
            
            
        if len(location) > 0:
            location = json.loads(location)
            instance.business.clear()
            instance.business.set(location)
            
            
        if len(service_group_brand) > 0:
            service_group_brand = json.loads(service_group_brand)
            for item in service_group_brand:
                service_group = item.get("service_group", None)
                test_data1 = service_group
                service_group_discount = float(item.get("discount", 0))
                brand = item.get("brand", None)
                test_data2 = brand
                brand_discount = float(item.get("brand_discount", 0))
                if brand:
                    instance.brands.clear()
                    instance.brands.set([brand])
                    brand_to_del = CouponBrand.objects.filter(coupon=instance)
                    if brand_to_del:
                        brand_to_del.delete()
                    CouponBrand.objects.create(
                        coupon=instance,
                        brand_id=brand,
                        brand_discount=brand_discount
                    )
                if service_group:
                    instance.coupon_service_groups.clear()
                    instance.coupon_service_groups.set([service_group])
                    service_group_del = CouponServiceGroup.objects.filter(coupon=instance)
                    if service_group_del:
                        service_group_del.delete()
                    CouponServiceGroup.objects.create(
                        coupon=instance,
                        service_group_id=service_group,
                        service_group_discount=service_group_discount
                    )
        if len(service_ids) > 0:
            instance.excluded_services.clear()
            service_ids = json.loads(service_ids)
            instance.excluded_services.set(service_ids)
        if client == 'all':
            instance.clients.clear()
        if client != 'all':
            client = json.loads(client)
            instance.clients.clear()
            instance.clients.set(client)
        if len(excluded_products) > 0:
            excluded_products = json.loads(excluded_products)
            instance.excluded_products.clear()
            instance.excluded_products.set(excluded_products)
        if len(product_brand) > 0:
            product_brand = json.loads(product_brand)
            instance.brand_id.clear()
            instance.brand_id.set(product_brand)
        if len(days_restriction) > 0:
            days_restriction = json.loads(days_restriction)
            deleted_block_days = CouponBlockDays.objects.filter(coupon_id=instance.id)
            if deleted_block_days:
                deleted_block_days.delete()
            for day in days_restriction:
                day = day.get("day", None)
                CouponBlockDays.objects.create(day=day, coupon_id=instance.id)
        if len(store_restriction) > 0:
            store_restriction = json.loads(store_restriction)
            instance.locations.clear()
            instance.locations.set(store_restriction)
        serializer = CouponSerializer(instance, context={'request': request})
        return Response(
            {
                'status': True,
                'status_code': 200,
                'response': {
                    'message': 'Coupon updated successfully!',
                    'error_message': None,
                    'errors': error,
                    'coupon': serializer.data,

                }
            },
            status=status.HTTP_200_OK
        )
    else:
        return Response({"msg": "Enter the valid id"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_coupon(request, id=None):
    if id:
        coupon = Coupon.objects.filter(id=id)
        coupon.delete()
        return Response(
            {
                'status': True,
                'status_code': 200,
                'response': {
                    'message': 'Coupon deleted successfully!',
                    'error_message': None,
                    # 'errors': error,
                    # 'coupon': serializer.data,

                }
            },
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_coupon(request):
    coupon_code = request.query_params.get('coupon_code', None)
    client_type = request.query_params.get('client_type', None)
    client_id = request.query_params.get('client_id', None)
    client_type = request.query_params.get('client_type')
    total_price = request.query_params.get('totalPriceWithoutTax',None)
    location = request.query_params.get('location_id',None)
    try:
        coupon = Coupon.objects.get(code=coupon_code)
    except Coupon.DoesNotExist:
        try:
            try:
                refund = RefundCoupon.objects.get(refund_coupon_code = coupon_code, is_used = False)
                
                if float(total_price) < refund.amount:
                    return Response(
                            {
                                'status': False,
                                'status_code': 400,
                                'response': {
                                    'message': 'Coupon can not be implement',
                                    'error_message': None,

                                }
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                if location != str(refund.related_refund.location.id):
                #     return Response({'True':"True",'coming location':location , 'Refund location':refund.related_refund.location.id})
                # else:
                #     return Response({'False':"False", 'coming location':location , 'Refund location':refund.related_refund.location.id})
                    # raise ValueError(f'coming location{location} and refund location {refund.related_refund.location.id}')
                    return Response(
                            {
                                'status': False,
                                'status_code': 400,
                                'response': {
                                    'message': 'This coupon code is not available on this location',
                                    'error_message': None,

                                }
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                if(str(client_type) is str(refund.related_refund.client_type)):
                    return Response(
                                {
                                    'status': False,
                                    'status_code': 400,
                                    'response': {
                                        'message': 'Please Enter a Valid Client Type',
                                        'error_message': None,

                                    }
                                },
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    
                if client_id:
                    if ( client_id == refund.client.id and str(client_type) == str(refund.related_refund.client_type )):
                            return Response(
                                    {
                                        'status': False,
                                        'status_code': 400,
                                        'response': {
                                            'message': 'Coupon does not valid for selected client',
                                            'error_message': None,
                                            

                                        }
                                    },
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                
                    
                    
            except Exception as e:
                raise ValueError(f'{e}')
            serializer = RefundCouponSerializer(refund)
            return Response(
                    {
                        'status': True,
                        'status_code': 201,
                        'response': {
                            'message': 'Coupon redeemed successfully!',
                            'error_message': None,
                            'coupon_id': refund.id,
                            'usage_limit':refund.is_used,
                            # 'user_limit': coupon.user_limit,
                            'coupon': serializer.data,
                            'amount_spent':refund.amount,
                            'total_price':total_price

                        }
                    },
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response(
                {
                    'status': False,
                    'status_code': 400,
                    'response': {
                        'message': 'Enter a valid coupon',
                        'error_message': f'Error in refund{e}',

                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
    else:
        if location is not None:
            location_exists = coupon.locations.filter(id=location)
            if location_exists.exists():
                return Response(
                    {
                        'status': False,
                        'status_code': 400,
                        'response': {
                            'message': 'This coupon code is not available on this location',
                            'error_message': None,
                            # 'current_day': current_day

                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        if coupon.usage_limit <=0:
            return Response(
                {
                    'status': False,
                    'status_code': 400,
                    'response': {
                        'message': 'Coupon usage limit exceed',
                        'error_message': None,
                        # 'current_day': current_day

                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if coupon.user_limit <= 0:
            return Response(
                {
                    'status': False,
                    'status_code': 400,
                    'response': {
                        'message': 'Coupon user limit exceed',
                        'error_message': None,
                        # 'current_day': current_day

                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        # if location is not None:
        #     location_exists = coupon.locations.filter(id=location)
        #     if location_exists.exists():
        #         pass
        #     else:
        #         return Response(
        #             {
        #                 'status': False,
        #                 'status_code': 400,
        #                 'response': {
        #                     'message': 'This coupon code is not available',
        #                     'error_message': None,
        #                     # 'current_day': current_day
        # 
        #                 }
        #             },
        #             status=status.HTTP_400_BAD_REQUEST
        #         )

        if total_price is not None:
            if coupon.coupon_type_value == '3':
                total_price = float(total_price)
                if total_price < float(coupon.amount_spent):
                    return Response(
                        {
                            'status': False,
                            'status_code': 400,
                            'response': {
                                'message': 'Coupon can not be implement',
                                'error_message': None,
                                # 'current_day': current_day

                            }
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
        current_date = timezone.now().date()
        current_day = timezone.now()
        current_day = current_day.strftime('%A')
        day_check = CouponBlockDays.objects.filter(day__icontains=current_day, coupon_id=coupon.id)
        if day_check:
            return Response(
                {
                    'status': False,
                    'status_code': 400,
                    'response': {
                        'message': 'Coupon can not be added on {current_day}'.format(current_day=current_day),
                        'error_message': None,

                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        # if total_price is not None:
        #     if float(total_price) >= float(coupon.amount_spent):
        #         return Response(
        #             {
        #                 'status': False,
        #                 'status_code': 400,
        #                 'response': {
        #                     'message': 'Coupon can not be implement',
        #                     'error_message': None,
        #                     'current_day': current_day
        #
        #                 }
        #             },
        #             status=status.HTTP_400_BAD_REQUEST
        #         )

        if coupon.end_date < current_date:
            return Response(
                {
                    'status': False,
                    'status_code': 400,
                    'response': {
                        'message': 'Coupon expired',
                        'error_message': None,

                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if coupon.client_type != client_type:
            return Response(
                {
                    'status': False,
                    'status_code': 400,
                    'response': {
                        'message': 'Enter a valid client type',
                        'error_message': None,

                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if client_id is not None:
            check_coupon = Coupon.objects.get(code=coupon_code)
            if check_coupon.clients.exists():
                check_coupon = Coupon.objects.filter(clients__id=client_id)
                if check_coupon:
                    pass
                else:
                    return Response(
                        {
                            'status': False,
                            'status_code': 400,
                            'response': {
                                'message': 'Coupon does not valid for selected client',
                                'error_message': None,
                                'current_day':current_day

                            }
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
    serializer = CouponSerializer(coupon, context={'request': request})
    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Coupon redeemed successfully!',
                'error_message': None,
                'coupon_id': coupon.id,
                'usage_limit':coupon.usage_limit,
                'user_limit': coupon.user_limit,
                'coupon': serializer.data,
                'coupon.amount_spent':coupon.amount_spent,
                'total_price':total_price

            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_all_coupon(request):
    coupon = Coupon.objects.all()
    coupon.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Coupon deleted successfully!',
                'error_message': None,
                # 'errors': error,
                # 'coupon': serializer.data,

            }
        },
        status=status.HTTP_200_OK
    )