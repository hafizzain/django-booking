


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
from Product.models import Brand, Product, ProductStock
from Profile.models import UserLanguage
from Profile.serializers import UserLanguageSerializer
from Promotions.models import BlockDate, CategoryDiscount, DateRestrictions, DayRestrictions, DirectOrFlatDiscount, FixedPriceService, FreeService, MentionedNumberService, PurchaseDiscount, ServiceGroupDiscount, SpecificBrand, SpecificGroupDiscount, SpendDiscount, SpendSomeAmount, SpendSomeAmountAndGetDiscount
from Promotions.serializers import DirectOrFlatDiscountSerializers, FixedPriceServiceSerializers, MentionedNumberServiceSerializers, PurchaseDiscountSerializers, SpecificBrandSerializers, SpecificGroupDiscountSerializers, SpendDiscountSerializers, SpendSomeAmountSerializers
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
    data = []
    
    flatordirect = DirectOrFlatDiscount.objects.filter(is_deleted=False).order_by('-created_at').distinct()
    serialized = DirectOrFlatDiscountSerializers(flatordirect,  many=True, context={'request' : request})
    data.extend(serialized.data)
    
    specific_group = SpecificGroupDiscount.objects.filter(is_deleted=False).order_by('-created_at').distinct()
    serialized = SpecificGroupDiscountSerializers(specific_group,  many=True, context={'request' : request})
    data.extend(serialized.data)
    
    purchase_discount = PurchaseDiscount.objects.filter(is_deleted=False).order_by('-created_at').distinct()
    serialized = PurchaseDiscountSerializers(purchase_discount,  many=True, context={'request' : request})
    data.extend(serialized.data)
    
    specificbrand = SpecificBrand.objects.filter(is_deleted=False).order_by('-created_at').distinct()
    serialized = SpecificBrandSerializers(specificbrand,  many=True, context={'request' : request})
    data.extend(serialized.data)
    
    spend_discount = SpendDiscount.objects.filter(is_deleted=False).order_by('-created_at').distinct()
    serialized = SpendDiscountSerializers(spend_discount,  many=True, context={'request' : request})
    data.extend(serialized.data)
    
    spend_discount = SpendSomeAmount.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = SpendSomeAmountSerializers(spend_discount,  many=True, context={'request' : request})
    data.extend(serialized.data)
    
    fixed_price = FixedPriceService.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = FixedPriceServiceSerializers(fixed_price,  many=True, context={'request' : request})
    data.extend(serialized.data)
    
    free_price = MentionedNumberService.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = MentionedNumberServiceSerializers(free_price,  many=True, context={'request' : request})
    data.extend(serialized.data)
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Discount',
                'error_message' : None,
                'flatordirect' : data
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
        datetestriction = DateRestrictions.objects.get(directorflat = directorflat.id)
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
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id  = str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()
                    
                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text = f'{str(err)}')
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
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date= date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
               BlockDate.objects.create(
                    directorflat = directorflat,
                    date = date,
                ) 
    
    serializers= DirectOrFlatDiscountSerializers(directorflat, context={'request' : request})
       
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Direct or Flat Updated Successfully!',
                'error_message' : None,
                'error' : error,
                'flatordirect' : serializers.data
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
                service_group = cat.get('service_group', None)
                discount = cat.get('discount', None)
                
                try:
                    service_grp = ServiceGroup.objects.get(id = str(service_group))
                except:
                    pass
                ServiceGroupDiscount.objects.create(
                    specificgroupdiscount = sp_grp ,
                    
                    servicegroup = service_grp,
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
    
    serializers= SpecificGroupDiscountSerializers(sp_grp, context={'request' : request})
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Specific Group Discount Created Successfully!',
                    'error_message' : None,
                    'errors' : error,
                    'specificgroup' : serializers.data,
                    
                }
            },
            status=status.HTTP_201_CREATED
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_specificgroupdiscount(request):
    user = request.user
    
    specificgroup_id = request.data.get('id', None)
    
    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    
    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)
    
    servicegroup = request.data.get('servicegroup', None)  
    
    error = []
    
    if specificgroup_id is None: 
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
        specific_group = SpecificGroupDiscount.objects.get(id=specificgroup_id)
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
        
        
    if servicegroup is not None:
        if type(servicegroup) == str:
            servicegroup = servicegroup.replace("'" , '"')
            servicegroup = json.loads(servicegroup)
        else:
            pass
        for cat in servicegroup:
            id = cat.get('id', None)
            service_group = cat.get('service_group', None)
            discount = cat.get('discount', None)
            is_deleted = cat.get('is_deleted', None)
            try:
                service_grp = ServiceGroup.objects.get(id = str(service_group))
            except:
                pass
            if id is not None:
                try:
                    ser_grp = ServiceGroupDiscount.objects.get(id = str(id))
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
                    specificgroupdiscount = specific_group ,
                    servicegroup = service_grp,
                    discount = discount
                )
        
    try:
        daterestriction = DateRestrictions.objects.get(specificgroupdiscount = specific_group.id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'daterestriction Service Not Found!',
                    'error_message' : str(err),
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
            dayrestrictions = dayrestrictions.replace("'" , '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id  = str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()
                    
                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text = f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    specificgroupdiscount = specific_group,
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
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date= date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
               BlockDate.objects.create(
                    specificgroupdiscount = specific_group,
                    date = date,
                ) 
        
    serializers= SpecificGroupDiscountSerializers(specific_group, context={'request' : request})
       
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Specific Group Discount Updated Successfully!',
                'error_message' : None,
                'error' : error,
                'specificgroup' : serializers.data
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
        specific_grp = SpecificGroupDiscount.objects.get(id=specific_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Specific group Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    specific_grp.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Specific Group Discount deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
  
@api_view(['GET'])
@permission_classes([AllowAny])
def get_specificgroupdiscount(request):
    specific_group = SpecificGroupDiscount.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = SpecificGroupDiscountSerializers(specific_group,  many=True, context={'request' : request})
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Specific Group Discount',
                'error_message' : None,
                'specificgroup' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
   
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
    purchase_discount = PurchaseDiscount.objects.create(
        user = user,
        business =  business,
        select_type = select_type,
        purchase = purchase,
        discount_value = discount_value,
    )
    if select_type == 'Product':
        try:
            product_id=Product.objects.get(id=product)
        except Exception as err:
            return Response(
                {
                        'status' : False,
                        'status_code' : StatusCodes.PRODUCT_NOT_FOUND_4037,
                        'response' : {
                        'message' : 'Product not found',
                        'error_message' : str(err),
                    }
                }
        
            )
            
        try:
            discount_product_id=Product.objects.get(id=discount_product)
        except Exception as err:
            return Response(
                {
                        'status' : False,
                        'status_code' : StatusCodes.PRODUCT_NOT_FOUND_4037,
                        'response' : {
                        'message' : 'Discount Product not found',
                        'error_message' : str(err),
                        
                    }
                }
            )
        purchase_discount.product = product_id
        purchase_discount.discount_product = discount_product_id
        purchase_discount.save()
   
    else:
        try:
            service_id=Service.objects.get(id=service)
        except Exception as err:
            return Response(
                {
                        'status' : False,
                        'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
                        'response' : {
                        'message' : 'Product not found',
                        'error_message' : str(err),
                    }
                }
        
            )
            
        try:
            discount_service_id=Service.objects.get(id=discount_service)
        except Exception as err:
            return Response(
                {
                        'status' : False,
                        'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
                        'response' : {
                        'message' : 'Discount Product not found',
                        'error_message' : str(err),
                    }
                }
        
            )
        purchase_discount.service = service_id
        purchase_discount.discount_service = discount_service_id
        purchase_discount.save()
      
    date_res = DateRestrictions.objects.create(
        purchasediscount = purchase_discount,
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
                    purchasediscount = purchase_discount ,
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
                    purchasediscount = purchase_discount,
                    date = date,
                )
                
            except Exception as err:
               error.append(str(err))
               
    serializers= PurchaseDiscountSerializers(purchase_discount, context={'request' : request})
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Purchase Discount Created Successfully!',
                    'error_message' : None,
                    'errors' : error,
                    'purchasediscount' : serializers.data,
                    
                }
            },
            status=status.HTTP_201_CREATED
        )
    
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
    
    discount_value = request.data.get('discount_value', None)
    
    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    
    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)
    
    error = []
    
    if purchase_id is None: 
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
        purchase_discount = PurchaseDiscount.objects.get(id=purchase_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Purchase Discount Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
        
    try:
        daterestriction = DateRestrictions.objects.get(purchasediscount = purchase_discount.id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'daterestriction Service Not Found!',
                    'error_message' : str(err),
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
            dayrestrictions = dayrestrictions.replace("'" , '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id  = str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()
                    
                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text = f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    purchasediscount = purchase_discount,
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
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date= date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
               BlockDate.objects.create(
                    purchasediscount = purchase_discount,
                    date = date,
                )
    serializers= PurchaseDiscountSerializers(purchase_discount, data=request.data, partial=True, context={'request' : request})
    if serializers.is_valid():
        serializers.save()
    else:
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
            'response' : {
                'message' : 'Invialid Data',
                'error_message' : str(serializers.errors),
            }
        },
        status=status.HTTP_404_NOT_FOUND
    )
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Purchase Discount Updated Successfully!',
                'error_message' : None,
                'error' : error,
                'purchasediscount' : serializers.data
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
        purchase_dicount = PurchaseDiscount.objects.get(id=purchase_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Purchase Discount Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    purchase_dicount.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Purchase Discount deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_purchasediscount(request):
    purchase_discount = SpecificGroupDiscount.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = PurchaseDiscountSerializers(purchase_discount,  many=True, context={'request' : request})
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Purchase Discount',
                'error_message' : None,
                'purchasediscount' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_specificbrand_discount(request):
    user = request.user
    business_id = request.data.get('business', None)
    
    service_group = request.data.get('service_group', None)
    brand = request.data.get('brand', None)
    
    discount_brand = request.data.get('discount_brand', None)
    discount_service_group = request.data.get('discount_service_group', None)
    
    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    
    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)
    
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
    try:
        service_grp = ServiceGroup.objects.get(id = str(service_group))
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.SERVICEGROUP_NOT_FOUND_4042,
                    'response' : {
                    'message' : 'Service Group not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    try:
        brand_id = Brand.objects.get(id = str(brand))
    except Exception as err:
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_CATEGORY_BRAND_4020,
                'response' : {
                'message' : 'Brand not found',
                'error_message' : str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    specific_brand = SpecificBrand.objects.create(
        user = user,
        business =  business,
        
        servicegroup = service_grp,
        brand = brand_id,
        discount_brand = discount_brand,
        discount_service_group = discount_service_group,
    )
    
    date_res = DateRestrictions.objects.create(
        specificbrand = specific_brand ,
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
                    specificbrand = specific_brand,
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
                    specificbrand = specific_brand,
                    date = date,
                )
                
            except Exception as err:
               error.append(str(err))
    
    serializers= SpecificBrandSerializers(specific_brand, context={'request' : request})
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Specific Brand Discount Created Successfully!',
                    'error_message' : None,
                    'errors' : error,
                    'specificbrand' : serializers.data,
                    
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
        specific_dicount = SpecificBrand.objects.get(id=id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Specific Brand Discount Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    specific_dicount.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Specific Brand Discount deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_specificbrand_discount(request):
    specificbrand = SpecificBrand.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = SpecificBrandSerializers(specificbrand,  many=True, context={'request' : request})
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Purchase Discount',
                'error_message' : None,
                'specificbrand' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_specificbrand_discount(request):
    
    specific_id = request.data.get('id', None)
    
    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    
    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)
    
    error = []
    
    if specific_id is None: 
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
        specific_discount = SpecificBrand.objects.get(id=specific_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Specific Discount Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
        
    try:
        daterestriction = DateRestrictions.objects.get(specificbrand = specific_discount.id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'daterestriction Service Not Found!',
                    'error_message' : str(err),
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
            dayrestrictions = dayrestrictions.replace("'" , '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id  = str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()
                    
                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text = f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    specificbrand = specific_discount,
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
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date= date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
               BlockDate.objects.create(
                    specificbrand = specific_discount,
                    date = date,
                )
    serializers= SpecificBrandSerializers(specific_discount, data=request.data, partial=True, context={'request' : request})
    if serializers.is_valid():
        serializers.save()
    else:
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
            'response' : {
                'message' : 'Invialid Data',
                'error_message' : str(serializers.errors),
            }
        },
        status=status.HTTP_404_NOT_FOUND
    )
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Specific Brand Discount Updated Successfully!',
                'error_message' : None,
                'error' : error,
                'specificbrand' : serializers.data
            }
        },
        status=status.HTTP_200_OK
    )
    
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
    
    try:
            service_id=Service.objects.get(id=service)
    except Exception as err:
        return Response(
            {
                    'status' : False,
                    'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
                    'response' : {
                    'message' : 'Service not found',
                    'error_message' : str(err),
                }
            }
    
        )
    
    spend_discount = SpendDiscount.objects.create(
        user = user,
        business =  business,
        select_type = select_type,
        spend_amount = spend_amount,
        discount_value = discount_value,
        service = service_id,
    )
    
    if discount_product:
        try:
            discount_product_id=Product.objects.get(id=discount_product)
        except Exception as err:
            return Response(
                {
                        'status' : False,
                        'status_code' : StatusCodes.PRODUCT_NOT_FOUND_4037,
                        'response' : {
                        'message' : 'Discount Product not found',
                        'error_message' : str(err),
                        
                    }
                }
            )
        spend_discount.discount_product = discount_product_id
        spend_discount.save()
    if discount_service:
        try:
            discount_service_id=Service.objects.get(id=discount_service)
        except Exception as err:
            return Response(
                {
                        'status' : False,
                        'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
                        'response' : {
                        'message' : 'Discount Service not found',
                        'error_message' : str(err),
                    }
                }
        
            )
        spend_discount.discount_service = discount_service_id
        spend_discount.save()
      
    date_res = DateRestrictions.objects.create(
        spenddiscount = spend_discount,
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
                    spenddiscount = spend_discount,
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
                    spenddiscount = spend_discount,
                    date = date,
                )
                
            except Exception as err:
               error.append(str(err))
               
    serializers = SpendDiscountSerializers(spend_discount, context={'request' : request})
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Spend Discount Created Successfully!',
                    'error_message' : None,
                    'errors' : error,
                    'spenddiscount' : serializers.data,
                    
                }
            },
            status=status.HTTP_201_CREATED
        )
    
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
        spend_discount = PurchaseDiscount.objects.get(id=spend_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Purchase Discount Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
        
    try:
        daterestriction = DateRestrictions.objects.get(spenddiscount = spend_discount.id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'daterestriction Service Not Found!',
                    'error_message' : str(err),
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
            dayrestrictions = dayrestrictions.replace("'" , '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id  = str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()
                    
                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text = f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    spenddiscount = spend_discount,
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
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date= date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
               BlockDate.objects.create(
                    spenddiscount = spend_discount,
                    date = date,
                )
   
    serializers= PurchaseDiscountSerializers(spend_discount, data=request.data, partial=True, context={'request' : request})
    if serializers.is_valid():
        serializers.save()
    else:
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
            'response' : {
                'message' : 'Invialid Data',
                'error_message' : str(serializers.errors),
            }
        },
        status=status.HTTP_404_NOT_FOUND
    )
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Purchase Discount Updated Successfully!',
                'error_message' : None,
                'error' : error,
                'purchasediscount' : serializers.data
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
        spend_discount = SpendDiscount.objects.get(id=spend_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Spend Discount Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    spend_discount.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Spend Discount deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_spend_discount(request):
    spend_discount = SpendDiscount.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = SpendDiscountSerializers(spend_discount,  many=True, context={'request' : request})
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Spend Discount',
                'error_message' : None,
                'spenddiscount' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
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
    
    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)
    
    spend_service = request.data.get('spend_service', None)
    
    
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
        user = user,
        business =  business,
        # service = service_id,
        # spend_amount = spend_amount,
    )
      
    if spend_service is not None:
        if type(spend_service) == str:
            spend_service = spend_service.replace("'" , '"')
            spend_service = json.loads(spend_service)
        else:
            pass
        for cat in spend_service:
            try:
                service = cat.get('service', None)
                discount = cat.get('spend_amount', None)
                
                try:
                    service_id = Service.objects.get(id = str(service))
                except:
                    pass
                SpendSomeAmountAndGetDiscount.objects.create(
                    # user = user,
                    # business = business,
                    
                    spandsomeamount = spend_some_amount,
                    service = service_id,
                    spend_amount = discount
                )
                
            except Exception as err:
               error.append(str(err))
      
    date_res = DateRestrictions.objects.create(
        spendsomeamount = spend_some_amount,
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
                    spendsomeamount = spend_some_amount,
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
                    spendsomeamount = spend_some_amount,
                    date = date,
                )
                
            except Exception as err:
               error.append(str(err))
               
    serializers = SpendSomeAmountSerializers(spend_some_amount, context={'request' : request})
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Spend Amount Created Successfully!',
                    'error_message' : None,
                    'errors' : error,
                    'spendamount' : serializers.data,
                    
                }
            },
            status=status.HTTP_201_CREATED
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_spend_some_amount(request):
    
    spend_id = request.data.get('id', None)
    
    spend_service = request.data.get('spend_service', None)

    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    
    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)
    
    error = []
    
    if spend_id is None: 
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
        spend_some = SpendSomeAmount.objects.get(id=spend_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Spend Some Amount Discount Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
        
    try:
        daterestriction = DateRestrictions.objects.get(spendsomeamount = spend_some.id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'daterestriction Service Not Found!',
                    'error_message' : str(err),
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
            spend_service = spend_service.replace("'" , '"')
            spend_service = json.loads(spend_service)
        else:
            pass
        for cat in spend_service:
            id = cat.get('id', None)
            service_group = cat.get('service', None)
            discount = cat.get('spend_amount', None)
            is_deleted = cat.get('is_deleted', None)
            try:
                service_grp = Service.objects.get(id = str(service_group))
            except:
                pass
            if id is not None:
                try:
                    ser_grp = SpendSomeAmountAndGetDiscount.objects.get(id = str(id))
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
                    spandsomeamount = spend_some,
                    
                    service = service_grp,
                    spend_amount = discount
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
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id  = str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()
                    
                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text = f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    spendsomeamount = spend_some,
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
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date= date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
               BlockDate.objects.create(
                    spendsomeamount = spend_some,
                    date = date,
                )
    serializers= SpendSomeAmountSerializers(spend_some, data=request.data, partial=True, context={'request' : request})
    if serializers.is_valid():
        serializers.save()
    else:
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
            'response' : {
                'message' : 'Invialid Data',
                'error_message' : str(serializers.errors),
            }
        },
        status=status.HTTP_404_NOT_FOUND
    )
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Spend Some Discount Updated Successfully!',
                'error_message' : None,
                'error' : error,
                'spendsome' : serializers.data
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
        spend_discount = SpendSomeAmount.objects.get(id=spend_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Spend Some Discount Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    spend_discount.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Spend Some Discount deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_spend_some_amount(request):
    spend_discount = SpendSomeAmount.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = SpendSomeAmountSerializers(spend_discount,  many=True, context={'request' : request})
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Spend Some Discount',
                'error_message' : None,
                'spendsome' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_fixed_price_service(request):
    user = request.user
    business_id = request.data.get('business', None)
    
    spend_amount = request.data.get('spendAmount', None)
    duration = request.data.get('duration', None)
    service = request.data.get('service', None)
    
    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    
    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)    
    
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
    
    
    fixed_price = FixedPriceService.objects.create(
        user = user,
        business =  business,
        
        duration = duration,
        spend_amount = spend_amount,
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
        fixedpriceservice = fixed_price,
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
                    fixedpriceservice = fixed_price,
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
                    fixedpriceservice = fixed_price,
                    date = date,
                )
                
            except Exception as err:
               error.append(str(err))
               
    serializers = FixedPriceServiceSerializers(fixed_price, context={'request' : request})
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Fixed Price Service Created Successfully!',
                    'error_message' : None,
                    'errors' : error,
                    'fixedprice' : serializers.data,
                    
                }
            },
            status=status.HTTP_201_CREATED
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_fixed_price_service(request):
    
    fixed_id = request.data.get('id', None)
    
    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    
    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)
    
    spend_amount = request.data.get('spendAmount', None)
    duration = request.data.get('duration', None)
    service = request.data.get('service', None)
    
    error = []
    
    if fixed_id is None: 
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
        fixed_price = FixedPriceService.objects.get(id=fixed_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Fixed Service Discount Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
        
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
        daterestriction = DateRestrictions.objects.get(fixedpriceservice = fixed_price.id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'daterestriction Service Not Found!',
                    'error_message' : str(err),
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
            dayrestrictions = dayrestrictions.replace("'" , '"')
            dayrestrictions = json.loads(dayrestrictions)
        else:
            pass
        for dayres in dayrestrictions:
            id = dayres.get('id', None)
            day = dayres.get('day', None)
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id  = str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()
                    
                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text = f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    fixedpriceservice = fixed_price,
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
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date= date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
               BlockDate.objects.create(
                    fixedpriceservice = fixed_price,
                    date = date,
                )
    
    serializers= FixedPriceServiceSerializers(fixed_price, data=request.data, partial=True, context={'request' : request})
    if serializers.is_valid():
        serializers.save()
    else:
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
            'response' : {
                'message' : 'Invialid Data',
                'error_message' : str(serializers.errors),
            }
        },
        status=status.HTTP_404_NOT_FOUND
    )
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Fixed Price Service Updated Successfully!',
                'error_message' : None,
                'error' : error,
                'fixedprice' : serializers.data
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
        fixed_price = FixedPriceService.objects.get(id=fixed_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Fixed Price Discount Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    fixed_price.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Fixed Price Service deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_free_service(request):
    user = request.user
    business_id = request.data.get('business', None)
    
    # spend_amount = request.data.get('spendAmount', None)
    # duration = request.data.get('duration', None)
    freeservice = request.data.get('freeService', None)
    service = request.data.get('service', None)
    
    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    
    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)    
    
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
    
    try:
            freeservice_id=Service.objects.get(id=str(freeservice))
    except Exception as err:
        return Response(
        {
                'status' : False,
                'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
                'response' : {
                'message' : 'Free Service not found',
                'error_message' : str(err),
            }
        }
    )
    
    mention_number = MentionedNumberService.objects.create(
        user = user,
        business =  business,
        
        service = freeservice_id,
        # duration = duration,
        # spend_amount = spend_amount,
    )
    if service is not None:
        if type(service) == str:
            service = service.replace("'" , '"')
            service = json.loads(service)

        elif type(service) == list:
            pass
    
        for ser in service:
            try:
                id = ser.get('service', None)
                quantity = ser.get('quantity', None)
                
                try:
                    service_id = Service.objects.get(id = str(id))
                except Exception as err:
                    error.append(str(err))
                
                FreeService.objects.create(
                    mentionnumberservice = mention_number,
                    quantity = quantity,
                    service = service_id
                )
                
            except Exception as err:
                error.append(str(err))
    
    
    date_res = DateRestrictions.objects.create(
        mentionednumberservice = mention_number,
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
                    mentionednumberservice = mention_number,
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
                    mentionednumberservice = mention_number,
                    date = date,
                )
                
            except Exception as err:
               error.append(str(err))
               
    serializers = MentionedNumberServiceSerializers(mention_number, context={'request' : request})
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Free Service Created Successfully!',
                    'error_message' : None,
                    'errors' : error,
                    'freservice' : serializers.data,
                    
                }
            },
            status=status.HTTP_201_CREATED
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_free_service(request):
    
    mention_price_id = request.data.get('id', None)
    
    location = request.data.get('location', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    
    dayrestrictions = request.data.get('dayrestrictions', None)
    blockdate = request.data.get('blockdate', None)
    
    service = request.data.get('service', None)
    freeService = request.data.get('freeService', None)
    
    error = []
    
    if mention_price_id is None: 
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
        mention_service = MentionedNumberService.objects.get(id=mention_price_id)
        
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Mention number Service Discount Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    if freeService:
        try:
            services = Service.objects.get(id=str(freeService))
            mention_service.service = services
            mention_service.save()
        except Exception as err:
            return Response(
        {
                'status' : False,
                'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
                'response' : {
                'message' : 'Free Service not found',
                'error_message' : str(err),
            }
        },
        status=status.HTTP_404_NOT_FOUND
    )
     
    try:
        daterestriction = DateRestrictions.objects.get(mentionednumberservice = mention_service.id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'daterestriction Service Not Found!',
                    'error_message' : str(err),
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
            service = service.replace("'" , '"')
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
                    free_service = FreeService.objects.get(id  = str(id_service))
                    is_deleted = ser.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        free_service.delete()
                        continue
                    free_service.quantity = quantity
                    free_service.service = services
                    free_service.save()
                    
                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text = f'{str(err)}')
            else:
                FreeService.objects.create(
                    mentionnumberservice = mention_service,
                    
                    quantity = quantity,
                    service = services
                    
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
            if id is not None:
                try:
                    dayrestriction = DayRestrictions.objects.get(id  = str(id))
                    is_deleted = dayres.get('is_deleted', None)
                    if str(is_deleted) == "True":
                        dayrestriction.delete()
                        continue
                    dayrestriction.day = day
                    dayrestriction.save()
                    
                except Exception as err:
                    error.append(str(err))
                    ExceptionRecord.objects.create(text = f'{str(err)}')
            else:
                DayRestrictions.objects.create(
                    mentionednumberservice = mention_service,
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
                    if str(is_deleted) == "True":
                        block_date.delete()
                        continue
                    block_date.date= date
                    block_date.save()
                except Exception as err:
                    error.append(str(err))
            else:
               BlockDate.objects.create(
                    mentionednumberservice = mention_service,
                    date = date,
                )
    
    serializers= MentionedNumberServiceSerializers(mention_service, )#data=request.data, partial=True, context={'request' : request})

    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Free Price Service Updated Successfully!',
                'error_message' : None,
                'error' : error,
                'freservice' : serializers.data
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
        mention_price = MentionedNumberService.objects.get(id=mention_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Free Price Discount Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    mention_price.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Free Price Service deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )