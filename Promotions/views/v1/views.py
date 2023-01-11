


from datetime import datetime
import email
from django.conf import settings
from operator import ge
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Authentication.serializers import UserTenantLoginSerializer

from Business.models import BusinessAddressMedia, BusinessType
from Business.serializers.v1_serializers import EmployeTenatSerializer, OpeningHoursSerializer,AdminNotificationSettingSerializer, BookingSettingSerializer, BusinessTypeSerializer, Business_GetSerializer, Business_PutSerializer, BusinessAddress_GetSerializer, BusinessThemeSerializer, BusinessVendorSerializer, ClientNotificationSettingSerializer, StaffNotificationSettingSerializer, StockNotificationSettingSerializer, BusinessTaxSerializer, PaymentMethodSerializer
from Client.models import Client
from Employee.models import Employee

from NStyle.Constants import StatusCodes

from Appointment.models import AppointmentService
from Authentication.models import User
from Business.models import Business, BusinessSocial, BusinessAddress, BusinessOpeningHour, BusinessTheme, StaffNotificationSetting, ClientNotificationSetting, AdminNotificationSetting, StockNotificationSetting, BookingSetting, BusinessPaymentMethod, BusinessTax, BusinessVendor
from Product.models import Product, ProductStock
from Profile.models import UserLanguage
from Profile.serializers import UserLanguageSerializer
from Promotions.models import BlockDate, CategoryDiscount, DateRestrictions, DayRestrictions, DirectOrFlatDiscount, ServiceGroupDiscount, SpecificGroupDiscount
from Promotions.serializers import DirectOrFlatDiscountSerializers
from Service.models import Service, ServiceGroup
from Tenants.models import Domain, Tenant
from Utility.models import Country, Currency, ExceptionRecord, Language, NstyleFile, Software, State, City
from Utility.serializers import LanguageSerializer
import json
from django.db.models import Q

from django_tenants.utils import tenant_context

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_directorflat(request):
    user = request.user
    business_id = request.data.get('business', None)
    
    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    
    dayrestrictions = request.data.get('dayrestrictions', None)
    categorydiscount = request.data.get('categorydiscount', None)
    blockdate = request.data.get('blockdate', None)
    
    error = []
    
    if not all([business_id ]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
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
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Business not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    flatordirect = DirectOrFlatDiscount.objects.create(
        user = user,
        business =  business,
    )
    date_res = DateRestrictions.objects.create(
        directorflat = flatordirect ,
        start_date = start_date,
        end_date =end_date,
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
            categorydiscount = categorydiscount.replace("'" , '"')
            categorydiscount = json.loads(categorydiscount)
        else:
            pass
        for cat in categorydiscount:
            try:
                category = cat.get('category', None)
                discount = cat.get('discount', None)
                # all_category = cat.get('all_category', None)
                # service_discount = cat.get('service_discount', None)
                # retail_discount = cat.get('retail_discount', None)
                # voucher_discount = cat.get('voucher_discount', None)
                
                category_discount = CategoryDiscount.objects.create(
                    directorflat = flatordirect ,
                    
                    category_type = category,
                    discount = discount
                    # all_category = all_category,
                    # service_discount = service_discount,
                    # retail_discount = retail_discount,
                    # voucher_discount = voucher_discount,
                )
                
            except Exception as err:
               error.append(str(err))
    
    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'" , '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            try: 
                day = dayres.get('day', None)
                
                DayRestrictions.objects.create(
                    directorflat = flatordirect ,
                    day = day,
                )
                
            except Exception as err:
               error.append(str(err))
    
    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'" , '"')
            blockdate = json.loads(blockdate)
        else:
            pass
        
        for bl_date in blockdate:
            
            try: 
                date = bl_date.get('date', None)
                BlockDate.objects.create(
                    directorflat = flatordirect ,
                    date = date,
                )
                
            except Exception as err:
               error.append(str(err))
               
    serializers= DirectOrFlatDiscountSerializers(flatordirect, context={'request' : request})
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Direct or Flat Created Successfully!',
                    'error_message' : None,
                    'errors' : error,
                    'flatordirect' : serializers.data,
                    
                }
            },
            status=status.HTTP_201_CREATED
        ) 

@api_view(['GET'])
@permission_classes([AllowAny])
def get_directorflat(request):
    flatordirect = DirectOrFlatDiscount.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = DirectOrFlatDiscountSerializers(flatordirect,  many=True, context={'request' : request})
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Direct or Flat Discount',
                'error_message' : None,
                'flatordirect' : serialized.data
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
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
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
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Direct Or Flat Discount Service Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    directorflat.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Direct or Flat deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_directorflat(request):
    directorflat_id = request.data.get('id', None)
    
    location = request.data.get('location', None)
    
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    
    dayrestrictions = request.data.get('dayrestrictions', None)
    categorydiscount = request.data.get('categorydiscount', None)
    blockdate = request.data.get('blockdate', None)
    
    error = []
    
    if directorflat_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
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
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Direct Or Flat Discount Service Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        datetestriction = DateRestrictions.objects.get(id=directorflat.id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Direct Or Flat Discount datetestriction Service Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    if start_date:
        datetestriction.start_date = start_date
    if end_date:
        datetestriction.end_date = end_date
    
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
            categorydiscount = categorydiscount.replace("'" , '"')
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
                    category_id = CategoryDiscount.objects.get(id = str(id))
                    if bool(is_deleted) == True:
                        category_id.delete()
                    category_id.category_type = category
                    category_id.discount = discount
                    category_id.save()
                except Exception as err:
                    error.append(str(err))
            else:
                CategoryDiscount.objects.create(
                    directorflat = directorflat ,
                    
                    category_type = category,
                    discount = discount
                )
    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'" , '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            is_deleted = cat.get('is_deleted', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id  = str(id))
                    if bool(is_deleted) == True:
                        dayrestriction.delete()
                    dayrestriction.day = day
                    dayrestriction.save()
                except Exception as err:
                    error.append(str(err))
            else:
                DayRestrictions.objects.create(
                    directorflat = directorflat ,
                    day = day,
                )
                
    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'" , '"')
            blockdate = json.loads(blockdate)
        else:
            pass
        
        for bl_date in blockdate:    
            date = bl_date.get('date', None)
            is_deleted = bl_date.get('is_deleted', None)
            id = bl_date.get('id', None)
            if id is not None:
                try:
                    block_date = BlockDate.objects.get(id = str(id))
                    if bool(is_deleted) == True:
                        block_date.delete()
                    block_date.date= date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
               BlockDate.objects.create(
                    directorflat = directorflat,
                    date = date,
                ) 
                    
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Update Appointment Successfully',
                'error_message' : None,
                'Appointment' : 'serializer.data'
            }
        },
        status=status.HTTP_200_OK
    )
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_specificgroupdiscount(request):
    user = request.user
    business_id = request.data.get('business', None)
    
    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    
    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)
    
    servicegroup = request.data.get('servicegroup', None)    
    
    
    error = []
    
    if not all([business_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
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
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Business not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    sp_grp = SpecificGroupDiscount.objects.create(
        user = user,
        business =  business,
    )
    date_res = DateRestrictions.objects.create(
        specificgroupdiscount = sp_grp ,
        start_date = start_date,
        end_date =end_date,
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
            servicegroup = servicegroup.replace("'" , '"')
            servicegroup = json.loads(servicegroup)
        else:
            pass
        for cat in servicegroup:
            try:
                category = cat.get('service_group', None)
                discount = cat.get('discount', None)
                
                category_discount = ServiceGroupDiscount.objects.create(
                    specificgroupdiscount = sp_grp ,
                    
                    servicegroup = category,
                    discount = discount
                )
                
            except Exception as err:
               error.append(str(err))
               
    if dayrestrictions is not None:
        if type(dayrestrictions) == str:
            dayrestrictions = dayrestrictions.replace("'" , '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            try: 
                day = dayres.get('day', None)
                
                DayRestrictions.objects.create(
                    specificgroupdiscount = sp_grp ,
                    day = day,
                )
                
            except Exception as err:
                error.append(str(err))
    
    if blockdate is not None:
        if type(blockdate) == str:
            blockdate = blockdate.replace("'" , '"')
            blockdate = json.loads(blockdate)
        else:
            pass
        
        for bl_date in blockdate:
            
            try: 
                date = bl_date.get('date', None)
                BlockDate.objects.create(
                    specificgroupdiscount = sp_grp,
                    date = date,
                )
                
            except Exception as err:
               error.append(str(err))
               
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Direct or Flat Created Successfully!',
                    'error_message' : None,
                    'errors' : error,
                    'flatordirect' : 'serializers.data',
                    
                }
            },
            status=status.HTTP_201_CREATED
        )