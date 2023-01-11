


from datetime import datetime, time, timedelta
import email
from django.conf import settings
from operator import ge
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Appointment.Constants.durationchoice import DURATION_CHOICES
from Authentication.serializers import UserTenantLoginSerializer

from Business.models import BusinessAddressMedia, BusinessType
from Business.serializers.v1_serializers import BusinessAddress_CustomerSerializer, EmployeAppointmentServiceSerializer, EmployeTenatSerializer, OpeningHoursSerializer,AdminNotificationSettingSerializer, BookingSettingSerializer, BusinessTypeSerializer, Business_GetSerializer, Business_PutSerializer, BusinessAddress_GetSerializer, BusinessThemeSerializer, BusinessVendorSerializer, ClientNotificationSettingSerializer, StaffNotificationSettingSerializer, StockNotificationSettingSerializer, BusinessTaxSerializer, PaymentMethodSerializer
from Client.models import Client
from Employee.models import Employee

from NStyle.Constants import StatusCodes

from Appointment.models import AppointmentService
from Authentication.models import User
from Business.models import Business, BusinessSocial, BusinessAddress, BusinessOpeningHour, BusinessTheme, StaffNotificationSetting, ClientNotificationSetting, AdminNotificationSetting, StockNotificationSetting, BookingSetting, BusinessPaymentMethod, BusinessTax, BusinessVendor
from Product.models import Product, ProductStock
from Profile.models import UserLanguage
from Profile.serializers import UserLanguageSerializer
from Service.models import Service, ServiceGroup
from Tenants.models import Domain, Tenant
from Utility.models import Country, Currency, ExceptionRecord, Language, NstyleFile, Software, State, City
from Utility.serializers import LanguageSerializer
import json
from django.db.models import Q

from django_tenants.utils import tenant_context

from Sale.serializers import AppointmentCheckoutSerializer, BusinessAddressSerializer, CheckoutSerializer, EmployeeBusinessSerializer, MemberShipOrderSerializer, ProductOrderSerializer, ServiceGroupSerializer, ServiceOrderSerializer, ServiceSerializer, VoucherOrderSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_types(request):
    all_types = BusinessType.objects.filter(
        is_active=True,
        is_deleted=False
    )
    serialized = BusinessTypeSerializer(all_types, many=True, context={'request' : request})
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'All business types',
                'data' : serialized.data
            }
        }
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def create_user_business(request):
    user_id = request.data.get('user', None)
    business_name = request.data.get('business_name', None)
    country = request.data.get('country', None)
    state = request.data.get('state', None)
    city = request.data.get('city', None)
    postal_code = request.data.get('postal_code', None)
    address = request.data.get('address', None)
    opening_hours = request.data.get('opening_hours', None)
    business_types = request.data.get('business_types', None)
    software_used = request.data.get('software_used', None)

    if not all([user_id, business_name, country, state, city, postal_code, address, opening_hours, business_types, software_used ]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'user',
                        'business_name',
                        'country',
                        'state',
                        'city',
                        'postal_code',
                        'address',
                        'opening_hours',
                        'business_types',
                        'software_used',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(
            id=user_id,
            is_blocked=False,
            is_deleted=False
        )
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.USER_NOT_EXIST_4005,
                'response' : {
                    'message' : 'User not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        domain = Domain.objects.get(
            domain=business_name.replace(' ', '-'),
            is_deleted=False,
            is_active=True,
            is_blocked=False
        )
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.BUSINESS_NAME_ALREADY_TAKEN_4014,
                'status_code_text' : 'BUSINESS_NAME_ALREADY_TAKEN_4014',
                'response' : {
                    'message' : 'Business Name already taken',
                }
            },
            status=status.HTTP_403_FORBIDDEN
        )
    except:
        pass

    user_tenant = Tenant.objects.get(
        user=user,
        is_deleted=False,
        is_blocked=False
    )

    with tenant_context(user_tenant):
        website = request.data.get('website', '')
        sub_domain_new_name=business_name.replace(' ', '-')

        try:
            tnt_country = Country.objects.get(
                unique_code=country,
                is_deleted=False
            )
        except:
            tnt_country = None

        try:
            tnt_state = State.objects.get(
                unique_code=state,
                is_deleted=False
            )
        except:
            tnt_state = None

        try:
            tnt_city = City.objects.get(
                unique_code=state,
                is_deleted=False
            )
        except:
            tnt_city = None

    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Business Account Created',
                    'data' : {
                        'domain' : sub_domain_new_name,
                    }
                }
            },
            status=status.HTTP_201_CREATED
        )
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_business(request):
    user = request.GET.get('user', None)

    if user is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'User id is required',
                    'fields' : [
                        'user',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user_business = Business.objects.get(
            user=user,
            is_deleted=False,
            is_active=True,
            is_blocked=False
        )
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                'response' : {
                    'message' : 'Business Not Found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    serialized = Business_GetSerializer(user_business , context={'request' : request})

    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : 'BUSINESS_FOUND',
                'response' : {
                    'message' : 'Business Found',
                    'error_message' : None,
                    'business' : serialized.data
                }
            },
            status=status.HTTP_200_OK
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_by_domain(request):
    domain_name = request.GET.get('domain', None)

    if domain_name is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'User id is required',
                    'fields' : [
                        'domain',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        domain_name = f'{domain_name}.{settings.BACKEND_DOMAIN_NAME}'
        domain = None
        try :
           tenant_id = Tenant.objects.get(domain = domain_name )
           id = tenant_id.id
        except Exception as err:
            pass
        with tenant_context(Tenant.objects.get(schema_name = 'public')):
            domain = Domain.objects.get(domain=domain_name)

        if domain is not None:
            with tenant_context(domain.tenant):
                user_business = Business.objects.filter(
                    is_deleted=False,
                    is_active=True,
                    is_blocked=False
                )
                if len(user_business) > 0:
                    user_business = user_business[0]
                else:
                    raise Exception('0 Business found')
        else :
            raise Exception('Business Not Exist')
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                'response' : {
                    'message' : 'Business Not Found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    

    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : 'BUSINESS_FOUND',
                'response' : {
                    'message' : 'Business Found',
                    'error_message' : None,
                    'business' : {
                        'id' : str(user_business.id),
                        'business_name' : str(user_business.business_name),
                        'tenant_id' : str(id),
                        # 'logo' : user_business.logo if user_business.logo else None ,
                    }
                }
            },
            status=status.HTTP_200_OK
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business_additional_information(request):
    business_id = request.data.get('business', None)
    

    if business_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'User id is required',
                    'fields' : [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(
            id=business_id,
            is_deleted=False,
            is_blocked=False
        )
    except Exception as err :
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                'response' : {
                    'message' : 'Business Not Found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    is_completed = request.data.get('is_completed', None)
    
    team_size = request.data.get('team_size', business.team_size)
    how_find_us = request.data.get('how_find_us', business.how_find_us)
    
    selected_softwares = request.data.get('selected_softwares', [])
    selected_types = request.data.get('selected_types', [])
    currency_id = request.data.get('currency', None)
    
    try:
        currency= Currency.objects.get(id=currency_id)
        business.currency = currency
    except Exception as err:
        print(str(err))
        
    if is_completed is not None:
        business.is_completed = True
    else :
        business.is_completed = False
    
    business.team_size = team_size
    business.how_find_us = how_find_us
    business.save()

    if type(selected_softwares) == str:
        selected_softwares = json.loads(selected_softwares)
    elif type(selected_softwares) == list:
        pass
    
    business.software_used.clear()
    for software_id in selected_softwares:
        software = Software.objects.get(id=software_id)
        business.software_used.add(software)

    if type(selected_types) == str:
        selected_types = json.loads(selected_types)
    elif type(selected_types) == list:
        pass

    business.business_types.clear()
    for type_id in selected_types:
        type_obj = BusinessType.objects.get(id=type_id)
        business.business_types.add(type_obj)
    
    business.save()

    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : 'Saved Data',
                'response' : {
                    'message' : 'Successfully updated',
                    'error_message' : None,
                }
            },
            status=status.HTTP_200_OK
        )

# business_types
# software_used

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business(request):
    business_id = request.data.get('business', None)

    if business_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'User id is required',
                    'fields' : [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(
            id=business_id,
            is_deleted=False,
            is_blocked=False
        )
    except Exception as err :
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                'response' : {
                    'message' : 'Business Not Found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    serialized = Business_PutSerializer(business, data=request.data)
    
    if serialized.is_valid():
        serialized.save()

        website_url = request.data.get('website', None)
        fb_url = request.data.get('facebook', None)
        insta_url = request.data.get('instagram', None)
        business_social, created = BusinessSocial.objects.get_or_create(
            business=business,
            user=business.user
        )
        
        if website_url is not None:
            business_social.website = website_url
        else:
            business_social.website = ''

        if fb_url is not None:
            business_social.facebook = fb_url
        else:
            business_social.facebook = ''

        if insta_url is not None:
            business_social.instagram = insta_url
        else:
            business_social.instagram = ''
        
        business_social.save()
    
        logo = request.data.get('logo', None)
        if logo is not None:
            business.logo = logo
            business.save()
        serialized = Business_GetSerializer(business, context={'request' : request})
        return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : 'Saved Data',
                'response' : {
                    'message' : 'Successfully updated',
                    'error_message' : None,
                    'business' : serialized.data
                }
            },
            status=status.HTTP_200_OK
        )

    else:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.COULD_NOT_SAVE_FORM_DATA_4016,
                'status_code_text' : 'COULD_NOT_SAVE_FORM_DATA_4016',
                'response' : {
                    'message' : 'Could not save, Something went wrong',
                    'error_message' : serialized.errors,
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )



@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_locations(request, business_id):
    try:
        business = Business.objects.get(
            id=business_id,
            is_deleted=False,
            is_blocked=False,
            is_active=True
        )
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                'response' : {
                    'message' : 'Business Not Found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    business_addresses = BusinessAddress.objects.filter(
        business = business,
        is_deleted=False,
        is_closed=False,
        is_active=True
    ).order_by('-created_at').distinct()
    # all_products = BusinessAddress.objects.filter(is_deleted=True)
    # for i in all_products:
    #     i.delete()
    data = []
    if len(business_addresses) > 0:
        serialized = BusinessAddress_GetSerializer(business_addresses, many=True,context={'request' : request})
        data = serialized.data

    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : '200',
                'response' : {
                    'message' : 'Business All Locations',
                    'error_message' : None,
                    'count' : len(data),
                    'locations' : data,
                }
            },
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_business_location(request):
    business_id = request.data.get('business', None)
    user = request.user
    address = request.data.get('address', None)
    address_name = request.data.get('address_name', None)
    country = request.data.get('country', None)
    state = request.data.get('state', None)
    city = request.data.get('city', None)
    postal_code = request.data.get('postal_code', None)
    
    email= request.data.get('email',None)
    mobile_number = request.data.get('mobile_number', None)
    
    banking = request.data.get('banking',None)
    currency = request.data.get('currency',None)
    
    start_time = request.data.get('start_time', None)
    close_time = request.data.get('close_time', None)

    if not all([business_id, address, email, mobile_number, address_name]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'business',
                        'address',
                        'address_name',
                        'email',
                        'mobile_number',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        business = Business.objects.get(
            id=business_id,
            is_deleted=False,
            is_blocked=False,
            is_active=True
        )
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                'response' : {
                    'message' : 'Business Not Found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    if business.user.id != user.id:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.USER_HAS_NO_PERMISSION_1001,
                'status_code_text' : 'USER_HAS_NO_PERMISSION_1001',
                'response' : {
                    'message' : 'You are not allowed to add Business Location, Only Business owner can',
                    'error_message' : 'Error message',
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        if currency is not None:
            currency_id = Currency.objects.get( id = currency, is_deleted=False, is_active=True )
        if country is not None:
            country = Country.objects.get( id=country, is_deleted=False, is_active=True )
        if state is not None:
            state = State.objects.get( id=state, is_deleted=False, is_active=True )
        if city is not None:
            city = City.objects.get( id=city, is_deleted=False, is_active=True )
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'status_code_text' : 'Invalid Data',
                'response' : {
                    'message' : 'Invalid Country, State or City',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    business_address = BusinessAddress(
        business = business,
        user = user,
        address = address,
        address_name = address_name,
        email= email,
        mobile_number=mobile_number,
        country=country,
        currency = currency_id,
        state=state,
        city=city,
        banking = banking,
        is_primary = False,
        is_active = True,
        is_deleted = False,
        is_closed = False,
    )
    if postal_code is not None:
        business_address.postal_code = postal_code
    business_address.save()
    
    opening_day = request.data.get('open_day', None)   
    if type(opening_day) == str:
        opening_day = json.loads(opening_day)
    else:
        pass  

    # data={}
    # if start_time or close_time is not None:
    #     days = [
    #         'Monday',
    #         'Tuesday',
    #         'Wednesday',
    #         'Thursday',
    #         'Friday',
    #         'Saturday',
    #         'Sunday',
    #     ]
    days = [
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday',
    ]
    for day in days:
        
        bds_schedule = BusinessOpeningHour.objects.create(
            business_address = business_address,
            business = business,
            day = day,
        )
        s_day = opening_day.get(day.lower(), None)
        if s_day is not None:
            # bds_schedule.start_time = s_day.get('start_time', None)
            # bds_schedule.close_time = s_day.get('close_time', None)
            
            bds_schedule.start_time = s_day['start_time']
            bds_schedule.close_time = s_day['end_time']
        else:
            bds_schedule.is_closed = True

        bds_schedule.save()
      
            
    # serialized = OpeningHoursSerializer(busines_opening,  data=request.data)
    # if serialized.is_valid():
    #     serialized.save()
    #     data.update(serialized.data)
    try:
        all_product = Product.objects.all()
        
        for pro in all_product:
            product = Product.objects.get(
            id=pro.id,
            is_deleted = False,
            )
            stock  = ProductStock.objects.create(
                    user = user,
                    business = business,
                    product = product,
                    location = business_address,
                    available_quantity = 0,
                    low_stock = 0, 
                    reorder_quantity = 0,
                    #alert_when_stock_becomes_lowest = alert_when_stock_becomes_lowest,
                    #is_active = stock_status,
            )
    except Exception as err:
        print(str(err))
        ExceptionRecord.objects.create(
            text = f'{str(err) } line number 761'
        )
    
    
    serialized = BusinessAddress_GetSerializer(business_address, context={'request' : request})
    # if serialized.is_valid():
    #     serialized.save()
    #     data.update(serialized.data)
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'status_code_text' : 'Created',
                'response' : {
                    'message' : 'Location Added successful',
                    'error_message' : None,
                    'locations' : serialized.data
                }
            },
            status=status.HTTP_201_CREATED
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_location(request):
    user = request.user
    location_id = request.GET.get('location', None)

    if location_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'location',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business_address = BusinessAddress.objects.get(
            id=location_id,
            is_deleted = False,
            is_closed = False,
        )
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.LOCATION_NOT_FOUND_4017,
                'status_code_text' : 'LOCATION_NOT_FOUND_4017',
                'response' : {
                    'message' : 'Location Not Found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    if business_address.user == user or business_address.business.user == user :
        business_address.is_deleted = True
        business_address.save()
        return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : '200',
                'response' : {
                    'message' : 'Location deleted!',
                    'error_message' : None,
                }
            },
            status=status.HTTP_200_OK
        )

    else:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.USER_HAS_NO_PERMISSION_1001,
                'status_code_text' : 'USER_HAS_NO_PERMISSION_1001',
                'response' : {
                    'message' : 'You don"t have permission to delete this location',
                    'error_message' : 'User don"t have permission to delete this Business Address, user must be Business Owner or Location creator',
                }
            },
            status=status.HTTP_403_FORBIDDEN
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_location(request):
    location_id = request.data.get('location', None)

    if location_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'location',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business_address = BusinessAddress.objects.get(
            id=location_id,
            is_deleted = False,
            is_closed = False,
        )
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.LOCATION_NOT_FOUND_4017,
                'status_code_text' : 'LOCATION_NOT_FOUND_4017',
                'response' : {
                    'message' : 'Location Not Found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    opening_day = request.data.get('open_day', None)   
    if type(opening_day) == str:
        opening_day = json.loads(opening_day)
    else:
        pass 

    user = request.user
    if business_address.user == user or business_address.business.user == user :
        business_address.address_name = request.data.get('address_name', business_address.address_name)
        business_address.address = request.data.get('address', business_address.address)
        business_address.postal_code = request.data.get('postal_code', business_address.postal_code)
        business_address.mobile_number= request.data.get('mobile_number', business_address.mobile_number)
        business_address.email= request.data.get('email', business_address.email)
        business_address.banking= request.data.get('banking', business_address.banking)
        business_address.service_avaiable= request.data.get('service_avaiable', business_address.service_avaiable)
        business_address.location_name= request.data.get('location_name', business_address.location_name)
        business_address.description= request.data.get('description', business_address.description)
             
        country = request.data.get('country', None)
        state = request.data.get('state', None)
        city = request.data.get('city', None)
        currency = request.data.get('currency', None)
        images = request.data.get('images', None)
        is_publish = request.data.get('is_publish', None)
        
        if is_publish is not None:
            business_address.is_publish = True
        else:
            business_address.is_publish = False
            
        
        if images is not None:
            try:
                image = BusinessAddressMedia.objects.get(business = business_address.business,business_address = business_address,)
                image.delete()
            except:
                pass
            images = BusinessAddressMedia.objects.create(
                user = user,
                business = business_address.business,
                business_address = business_address,
                image = images
            )

        try:
            if currency is not None:
                currency_id = Currency.objects.get( id = currency, is_deleted=False, is_active=True )
                business_address.currency = currency_id
                business_address.save()
                
            if country is not None:
                country = Country.objects.get( id=country, is_deleted=False, is_active=True )
                business_address.country = country
                business_address.save()
            if state is not None:
                state = State.objects.get( id=state, is_deleted=False, is_active=True )
                business_address.state = state
                business_address.save()
            if city is not None:
                city = City.objects.get( id=city, is_deleted=False, is_active=True )
                business_address.city = city
                business_address.save()
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : 400,
                    'status_code_text' : 'Invalid Data',
                    'response' : {
                        'message' : 'Invalid Country, State or City',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        business_address.save()
        
        days = [
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
            'saturday',
            'sunday',
        ]
        
        for day in days:
            try:
                bds_schedule = BusinessOpeningHour.objects.get(business_address=business_address, day=day)
        
            except Exception as err:
                pass
            
            print(day)
            s_day = opening_day.get(day.lower(), None)
            if s_day is not None:
                bds_schedule.start_time = s_day['start_time']
                bds_schedule.close_time = s_day['end_time']
                bds_schedule.is_closed = False

            else:
                bds_schedule.is_closed = True

            bds_schedule.save()

        serialized = BusinessAddress_GetSerializer(business_address, context={'request' : request})

        return Response(
                {
                    'status' : True,
                    'status_code' : 200,
                    'status_code_text' : 'Updated',
                    'response' : {
                        'message' : 'Location updated successful',
                        'error_message' : None,
                        'location' : serialized.data
                    }
                },
                status=status.HTTP_200_OK
            )
        

    else:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.USER_HAS_NO_PERMISSION_1001,
                'status_code_text' : 'USER_HAS_NO_PERMISSION_1001',
                'response' : {
                    'message' : 'You don"t have permission to edit this location',
                    'error_message' : 'User don"t have permission to edit this Business Address, user must be Business Owner or Location creator',
                }
            },
            status=status.HTTP_403_FORBIDDEN
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_theme(request):
    business_id = request.GET.get('business', None)

    if business_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                    'response' : {
                        'message' : 'Business Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
    business_theme, created = BusinessTheme.objects.get_or_create(
        business=business,
        user=business.user,
        is_deleted=False, 
        is_active=True
    )

    serialized = BusinessThemeSerializer(business_theme)
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : 'BusinessTheme',
            'response' : {
                'message' : 'Business Theme',
                'error_message' : None,
                'theme' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business_theme(request):
    theme_id = request.data.get('theme', None)
    business_id = request.data.get('business', None)

    if not all([theme_id, business_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'theme',
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                    'response' : {
                        'message' : 'Business Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    business_theme, created = BusinessTheme.objects.get_or_create(
        business=business,
        user=business.user,
        is_deleted=False,
        is_active=True
    )

    serialized = BusinessThemeSerializer(business_theme, data=request.data)
    if serialized.is_valid():
        serialized.save()
        return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : 'BusinessTheme',
                'response' : {
                    'message' : 'Business theme updated',
                    'error_message' : None,
                    'theme' : serialized.data
                }
            },
            status=status.HTTP_200_OK
        )

    return Response(
        {
            'status' : True,
            'status_code' : 400,
            'status_code_text' : 'INVALID DATA',
            'response' : {
                'message' : 'Invalid Values',
                'error_message' : str(serialized.errors),
            }
        },
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_business_language(request):
    business_id = request.data.get('business', None)
    language_id = request.data.get('language', None)
    is_default = request.data.get('is_default', False)

    
    if not all([language_id, business_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'language',
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                    'response' : {
                        'message' : 'Business Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
    try:
        language = Language.objects.get(id=language_id, is_active=True,  is_deleted=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.LANGUAGE_NOT_FOUND_4018,
                    'status_code_text' : 'LANGUAGE_NOT_FOUND_4018',
                    'response' : {
                        'message' : 'Language Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

    
    language_obj = UserLanguage.objects.create(
        user=business.user,
        profile=business.profile,
        language=language,
        is_default=is_default
    )
    language_obj.save()
    seralized = UserLanguageSerializer(language_obj)
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Language Added',
                'error_message' : None,
                'language' : seralized.data
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_language(request):
    id = request.data.get('id', None)

    if not all([id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        language = UserLanguage.objects.get(id=id)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.LANGUAGE_NOT_FOUND_4018,
                    'status_code_text' : 'LANGUAGE_NOT_FOUND_4018',
                    'response' : {
                        'message' : 'UserLanguage Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    seralized = UserLanguageSerializer(language, data=request.data, partial=True)
    if seralized.is_valid():
        seralized.save()
        return Response(
                {
                    'status' : True,
                    'status_code' : 200,
                    'status_code_text' : '200',
                    'response' : {
                        'message' : 'Language Added',
                        'error_message' : None,
                        'language' : seralized.data
                    }
                },
                status=status.HTTP_200_OK
            )

    else:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'status_code_text' : 'INVALID DATA',
                'response' : {
                    'message' : 'Updated unsuccessful',
                    'error_message' : seralized.error_messages,
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )



@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_languages(request):
    business_id = request.GET.get('business', None)

    if not all([business_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                    'response' : {
                        'message' : 'Business Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

    business_languages = UserLanguage.objects.filter(user=business.user)
    seralized = UserLanguageSerializer(business_languages, many=True)
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Business languages',
                'error_message' : None,
                'languages' : seralized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_languages(request):
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
        language = UserLanguage.objects.get(id=id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'UserLanguage Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    language.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Language deleted successful',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_languages(request):
    all_languages = Language.objects.filter(is_active=True, is_deleted=False)

    serialized = LanguageSerializer(all_languages, many=True)
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'All languages',
                'error_message' : None,
                'languages' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_business_notification_settings(request):
    business_id = request.GET.get('business', None)

    if not all([business_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                    'response' : {
                        'message' : 'Business Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    staff_set, created = StaffNotificationSetting.objects.get_or_create(business=business, user=business.user, is_active=True)
    client_set, created = ClientNotificationSetting.objects.get_or_create(business=business, user=business.user, is_active=True)
    admin_set, created = AdminNotificationSetting.objects.get_or_create(business=business, user=business.user, is_active=True)
    stock_set, created = StockNotificationSetting.objects.get_or_create(business=business, user=business.user, is_active=True)


    staff_serializer = StaffNotificationSettingSerializer(staff_set)
    client_serializer = ClientNotificationSettingSerializer(client_set)
    admin_serializer = AdminNotificationSettingSerializer(admin_set)
    stock_serializer = StockNotificationSettingSerializer(stock_set)

    data = {}
    data.update(staff_serializer.data)
    data.update(client_serializer.data)
    data.update(admin_serializer.data)
    data.update(stock_serializer.data)
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'All Notification Settings',
                'error_message' : None,
                'settings' : data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business_notification_settings(request):
    business_id = request.data.get('business', None)
    if business_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    
    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                    'response' : {
                        'message' : 'Business Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    staff_set, created = StaffNotificationSetting.objects.get_or_create(business=business, user=business.user, is_active=True)
    client_set, created = ClientNotificationSetting.objects.get_or_create(business=business, user=business.user, is_active=True)
    admin_set, created = AdminNotificationSetting.objects.get_or_create(business=business, user=business.user, is_active=True)
    stock_set, created = StockNotificationSetting.objects.get_or_create(business=business, user=business.user, is_active=True)


    staff_serializer = StaffNotificationSettingSerializer(staff_set, data=request.data)
    client_serializer = ClientNotificationSettingSerializer(client_set, data=request.data)
    admin_serializer = AdminNotificationSettingSerializer(admin_set, data=request.data)
    stock_serializer = StockNotificationSettingSerializer(stock_set, data=request.data)

    data = {}
    if staff_serializer.is_valid():
        staff_serializer.save()
        data.update(staff_serializer.data)
    
    if client_serializer.is_valid():
        client_serializer.save()
        data.update(client_serializer.data)
    
    if admin_serializer.is_valid():
        admin_serializer.save()
        data.update(admin_serializer.data)

    if stock_serializer.is_valid():
        stock_serializer.save()
        data.update(stock_serializer.data)
        
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Notification setting updated',
                'error_message' : None,
                'settings' : data
            }
        },
        status=status.HTTP_200_OK
    )




@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_booking_settings(request):
    business_id = request.GET.get('business', None)

    if not all([business_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                    'response' : {
                        'message' : 'Business Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    booking_setting, created = BookingSetting.objects.get_or_create(business=business, user=business.user, is_active=True)
    serializer = BookingSettingSerializer(booking_setting)

    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Business Booking Setting',
                'error_message' : None,
                'setting' : serializer.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business_booking_settings(request):
    business_id = request.data.get('business', None)

    if not all([business_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                    'response' : {
                        'message' : 'Business Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    booking_setting, created = BookingSetting.objects.get_or_create(
        business=business, 
        user=business.user,
        is_active=True
        )
    serializer = BookingSettingSerializer(booking_setting, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : '200',
                'response' : {
                    'message' : 'Business Booking setting updated!',
                    'error_message' : None,
                    'setting' : serializer.data
                }
            },
            status=status.HTTP_200_OK
        )
    
    else:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'status_code_text' : '400',
                'response' : {
                    'message' : 'Invalid Data',
                    'error_message' : str(serializer.error_messages),
                    'tech_message' : str(serializer.errors),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_payment_method(request):
    method_type = request.data.get('method_type', None)
    business_id = request.data.get('business', None)

    if not all([method_type, business_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'method_type',
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = request.user

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                    'response' : {
                        'message' : 'Business Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )


    payment_method = BusinessPaymentMethod(
        user=user,
        business=business,
        method_type=method_type
    )
    payment_method.save()
    serialized = PaymentMethodSerializer(payment_method)

    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'status_code_text' : '201',
                'response' : {
                    'message' : 'Payment method added!',
                    'error_message' : None,
                    'payment_method' : serialized.data
                }
            },
            status=status.HTTP_201_CREATED
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_payment_method(request):
    method_type = request.data.get('method_type', None)
    method_id = request.data.get('id', None)

    if not all([method_type, method_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'id',
                        'method_type',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = request.user
    try:
        payment_method = BusinessPaymentMethod.objects.get(id=method_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Payment method Not Found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    payment_method.method_type = method_type
    payment_method.save()
    serialized = PaymentMethodSerializer(payment_method, context={'request':request})

    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : '200',
                'response' : {
                    'message' : 'Payment method updated!',
                    'error_message' : None,
                    'payment_method' : serialized.data
                }
            },
            status=status.HTTP_200_OK
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_payment_methods(request):
    business_id = request.GET.get('business', None)

    if not all([business_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                    'response' : {
                        'message' : 'Business Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )


    payment_methods = BusinessPaymentMethod.objects.filter(
        business=business,
        is_active=True
    )
    serialized = PaymentMethodSerializer(payment_methods, many=True)

    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : '200',
                'response' : {
                    'message' : 'Payment method added!',
                    'error_message' : None,
                    'payment_methods' : serialized.data
                }
            },
            status=status.HTTP_200_OK
        )
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_business_tax(request):
    business_id = request.data.get('business', None)
    tax_type = request.data.get('tax_type', 'Individual')
    name = request.data.get('name', None)
    tax_rate = request.data.get('tax_rate', None)
    tax_ids = request.data.get('tax_ids', None)
    location = request.data.get('location', None)
    
    tax_id = request.data.get('tax_id',None)
    
    if business_id is None or (tax_type != 'Location' and name is None) or (tax_type == 'Group' and tax_ids is None)  or (tax_type == 'Location' and location is None ):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'name',
                        'business',
                        'tax_type',
                        
                        # 'tax_rate',
                        'tax_ids',
                        'location',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = request.user

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                    'response' : {
                        'message' : 'Business Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    if tax_type == 'Location':
        try:
            location = BusinessAddress.objects.get(id=location) 
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.LOCATION_NOT_FOUND_4017,
                    'status_code_text' : 'LOCATION_NOT_FOUND_4017',
                    'response' : {
                        'message' : 'Location Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        try:
                tax = BusinessTax.objects.get(id=tax_id)
        except Exception as err:
                return Response(
                        {
                            'status' : False,
                            'status_code' : StatusCodes.LOCATION_NOT_FOUND_4017,
                            'status_code_text' : 'BUSINESSS_TAX_NOT_FOUND',
                            'response' : {
                                'message' : 'Business Tax Not Found',
                                'error_message' : str(err),
                            }
                        },
                        status=status.HTTP_404_NOT_FOUND
                    )
    if tax_rate is None:  
        tax_rate = 0
        
    business_tax = BusinessTax.objects.create(
        user = user,
        business=business,
        tax_type = tax_type,
        tax_rate = tax_rate,
    )
    if tax_type == 'Group' or tax_type == 'Individual':
        business_tax.name = name
    if tax_type == 'Location':
        business_tax.location = location
        business_tax.parent_tax.add(tax)
    
    all_errors = []
    import json

    if tax_type == 'Group':
        # all_errors.append({'type' : str(type(tax_ids))})
        # all_errors.append({'tax_ids' : tax_ids})
        if tax_ids is not None:
            if type(tax_ids) == str :
                ids_data = json.loads(tax_ids)
            else:
                ids_data = tax_ids
            for id in ids_data:
                #all_errors.append(str(id))
                try:
                    get_p_tax = BusinessTax.objects.get(id=id)
                    business_tax.parent_tax.add(get_p_tax)
                except Exception as err:
                    all_errors.append(str(err))

    # parent_tax = 
    business_tax.save()
    serialized = BusinessTaxSerializer(business_tax,context={'request':request} )
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'status_code_text' : '201',
                'response' : {
                    'message' : 'Business Tax added!',
                    'error_message' : None,
                    'tax' : serialized.data,
                    'errors' : json.dumps(all_errors)
                }
            },
            status=status.HTTP_201_CREATED
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business_tax(request):
    tax_id = request.data.get('tax_id', None)
    business_id = request.data.get('business', None)
    tax_type = request.data.get('tax_type', None)
    name = request.data.get('name', None)
    tax_rate = request.data.get('tax_rate', None)
    tax_ids = request.data.get('tax_ids', None)
    location = request.data.get('location', None)
    parent_tax = request.data.get('parent_tax', None)
    
    if business_id is None or (tax_type != 'Location' and name is None) or (tax_type == 'Group' and tax_ids is None) or (tax_type == 'Location' and location is None ):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'name',
                        'business',
                        'tax_type',
                        #'tax_rate',
                        #'tax_ids',
                        #'location',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if (tax_type != 'Group' and tax_type != 'Location'):
        tax_rate = int(tax_rate)
    user = request.user

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                    'response' : {
                        'message' : 'Business Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    if tax_type == 'Location':
        try:
            location = BusinessAddress.objects.get(id=location) 
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.LOCATION_NOT_FOUND_4017,
                    'status_code_text' : 'LOCATION_NOT_FOUND_4017',
                    'response' : {
                        'message' : 'Location Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            tax = BusinessTax.objects.get(id=parent_tax)
            print(tax)
        except Exception as err:
                return Response(
                        {
                            'status' : False,
                            'status_code' : StatusCodes.LOCATION_NOT_FOUND_4017,
                            'status_code_text' : 'BUSINESSS_TAX_NOT_FOUND',
                            'response' : {
                                'message' : 'Business Tax Not Found',
                                'error_message' : str(err),
                            }
                        },
                        status=status.HTTP_404_NOT_FOUND
                    )

    if tax_rate is None:
        tax_rate = 0

    try:
        business_tax = BusinessTax.objects.get(
            id=tax_id,
            user = user,
            business=business,
        )
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : 404,
                    'status_code_text' : '404',
                    'response' : {
                        'message' : 'Business Tax Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    business_tax.tax_type = tax_type
    business_tax.tax_rate = tax_rate
    if tax_type == 'Group' or tax_type == 'Individual':
        business_tax.name = name
    if tax_type == 'Location':
        business_tax.parent_tax.clear()
        business_tax.location = location
        business_tax.parent_tax.add(tax)

    if tax_type == 'Group':
        try:
            business_tax.parent_tax.clear()
        except:
            pass
        if type(tax_ids) == str:
            import json
            ids_data = json.loads(tax_ids)
        else:
            ids_data = tax_ids
        for id in ids_data:
            try:
                get_p_tax = BusinessTax.objects.get(id=id)
                business_tax.parent_tax.add(get_p_tax)
            except:
                pass
            # print(id)


    # parent_tax = 
    business_tax.save()
    serialized = BusinessTaxSerializer(business_tax , context={'request':request} )
    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : '200',
                'response' : {
                    'message' : 'Business Tax updated!',
                    'error_message' : None,
                    'tax' : serialized.data
                }
            },
            status=status.HTTP_200_OK
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_business_payment_methods(request):
    user = request.user
    method_id = request.data.get('id', None)

    if method_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        payment_method = BusinessPaymentMethod.objects.get(
            id=method_id,
            is_active=True
        )
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Business payment method not found!',
                    'error_message' : None,
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    if payment_method.business.user != user and payment_method.user != user:
        return Response(
            {
                'status' : False,
                'status_code' : 403,
                'status_code_text' : '403',
                'response' : {
                    'message' : 'You are not allowed to delete this payment method!',
                    'error_message' : None,
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    payment_method.delete()

    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : '200',
                'response' : {
                    'message' : 'Business payment method Deleted!',
                    'error_message' : None,
                }
            },
            status=status.HTTP_200_OK
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_taxes(request):
    business_id = request.GET.get('business', None)

    if business_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                    'response' : {
                        'message' : 'Business Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

    all_taxes = BusinessTax.objects.filter(business=business, is_active=True)
    serialized = BusinessTaxSerializer(all_taxes, many=True, context={'request':request})
    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : '200',
                'response' : {
                    'message' : 'Business Taxes!',
                    'error_message' : None,
                    'tax' : serialized.data
                }
            },
            status=status.HTTP_200_OK
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_business_tax(request):
    tax_id = request.data.get('tax', None)

    if tax_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'tax',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        tax = BusinessTax.objects.get(id=tax_id)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : 404,
                    'status_code_text' : '404',
                    'response' : {
                        'message' : 'Tax Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    tax.delete()
    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : '200',
                'response' : {
                    'message' : 'Business Tax Deleted!',
                    'error_message' : None,
                }
            },
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_business_vendor(request):
    business_id = request.data.get('business', None)
    user= request.user
    
    try:
        business=Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Business not found',
                    'error_message' : str(err),
                }
            }
    
        )
    vendor_csv = request.data.get('file', None)


    file = NstyleFile.objects.create(
        file = vendor_csv
    )
    with open( file.file.path , 'r', encoding='utf-8') as imp_file:
        for index, row in enumerate(imp_file):
            if index == 0:
                continue
            row = row.split(',')
            row = row
            
            if len(row) < 5:
                continue
            vendor_name = row[0].strip('"')
            email = row[1].strip('"')
            address = row[2].strip('"')
            status_ven = row[3].strip('"')
            gstin = row[4].strip('"')
            
            create_vendor = BusinessVendor.objects.create(
                user = user,
                business = business,
                vendor_name =vendor_name,
                address =  address,
                gstin =gstin,
                email = email,
                #is_active = status
            )
            if status_ven.strip() ==  'Active':
                create_vendor.is_active =True
                create_vendor.save()
            else :
                create_vendor.is_active = False
                create_vendor.save()
                
            print(f'Added Vendor {create_vendor} ... {vendor_name} ')
                
    file.delete()
    return Response({'Status' : 'Success'})
            

@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_vendors(request):
    all_vendors = BusinessVendor.objects.filter(is_deleted=False, is_closed=False)
    serialized = BusinessVendorSerializer(all_vendors, many=True)
    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : '200',
                'response' : {
                    'message' : 'All available business vendors!',
                    'error_message' : None,
                    'vendors' : serialized.data
                }
            },
            status=status.HTTP_200_OK
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_business_vendor(request):
    user = request.user
    business_id = request.data.get('business', None)
    vendor_name = request.data.get('vendor_name', None)
    address = request.data.get('address', None)
    mobile_number = request.data.get('mobile_number', None)

    email = request.data.get('email', None)
    country = request.data.get('country', None)
    state = request.data.get('state', None)
    city = request.data.get('city', None)
    gstin = request.data.get('gstin', None)
    website = request.data.get('website', None)
    is_active = request.data.get('is_active', None)
    
    if not all([business_id,vendor_name, address, email, is_active]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'business', 'vendor_name', 'address', 'email', 'is_active'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        if country is not None:
            country = Country.objects.get( id=country, is_deleted=False, is_active=True )
        if state is not None:
            state = State.objects.get( id=state, is_deleted=False, is_active=True )
        if city is not None:
            city = City.objects.get( id=city, is_deleted=False, is_active=True )
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'status_code_text' : 'Invalid Data',
                'response' : {
                    'message' : 'Invalid Country, State or City',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
     
    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                    'response' : {
                        'message' : 'Business Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    if is_active is not None:
        is_active= json.loads(is_active)
    else:
        is_active= True
        
    try:
        vendor = BusinessVendor.objects.create(
            user = user,
            business = business,
            country = country,
            state = state,
            city = city,
            vendor_name = vendor_name,
            address = address,
            gstin = gstin,
            website = website,
            email = email,
            mobile_number = mobile_number,
            is_active = is_active,
        )
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'status_code_text' : 'Invalid Data',
                'response' : {
                    'message' : 'Something went wrong',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    serialized = BusinessVendorSerializer(vendor)
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'status_code_text' : '201',
                'response' : {
                    'message' : 'Business vendors created!',
                    'error_message' : None,
                    'vendor' : serialized.data
                }
            },
            status=status.HTTP_201_CREATED
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business_vendor(request):
    vendor_id = request.data.get('vendor', True)

    if not all([vendor_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'vendor'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

     
        
    try:
        vendor = BusinessVendor.objects.get(
            id = vendor_id
        )
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Vendor not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    phone_number=request.data.get('mobile_number',None)
    if phone_number is not None:
        vendor.mobile_number = phone_number
    else :
        vendor.mobile_number = None
    vendor.save()
    serialized = BusinessVendorSerializer(vendor, data=request.data)
    if serialized.is_valid():
        serialized.save()
        return Response(
                {
                    'status' : True,
                    'status_code' : 200,
                    'status_code_text' : '200',
                    'response' : {
                        'message' : 'Business vendors updated!',
                        'error_message' : None,
                        'vendor' : serialized.data
                    }
                },
                status=status.HTTP_200_OK
            )
    else:
        return Response(
                {
                    'status' : False,
                    'status_code' : 400,
                    'status_code_text' : '400',
                    'response' : {
                        'message' : 'Invalid Data!',
                        'error_message' : str(serialized.errors),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_business_vendor(request):
    vendor_id = request.data.get('vendor', True)

    if not all([vendor_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'vendor'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

     
        
    try:
        vendor = BusinessVendor.objects.get(
            id = vendor_id
        )
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Vendor not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    vendor.delete()
    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : '200',
                'response' : {
                    'message' : 'Business vendors deleted!',
                    'error_message' : None,
                }
            },
            status=status.HTTP_200_OK
        )
        
@api_view(['GET'])
@permission_classes([AllowAny])
def search_business_vendor(request):
    text = request.GET.get('text', None)

    if text is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'text',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    search_vendor = BusinessVendor.objects.filter(
        Q(vendor_name__icontains=text)|
        Q(address__icontains=text)|
        Q(mobile_number__icontains=text)|
        Q(email__icontains=text)
        
    )
    serialized = BusinessVendorSerializer(search_vendor, many=True, context={'request':request})
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'All Search Business Vendor!',
                'error_message' : None,
                'count' : len(serialized.data),
                'vendors' : serialized.data,
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_domain_business_address(request):   
    tenant_id = request.GET.get('hash', None)
    data = []
    service_group = []
    
    if tenant_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'hash',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    
    try:
        tenant = Tenant.objects.get(id = tenant_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'status_code_text' : 'Invalid Data',
                'response' : {
                    'message' : 'Invalid Tenant Id',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )                 
    with tenant_context(tenant):
        user_business = Business.objects.filter(
            is_deleted=False,
            is_active=True,
            is_blocked=False
        )                
        if len(user_business) > 0:
            user_business = user_business[0]
        else:
            raise Exception('0 Business found')
        try:
            business_addresses = BusinessAddress.objects.filter(
                business = str(user_business.id),
                is_deleted=False,
                is_closed=False,
                is_active=True
            ).order_by('-created_at').distinct()
        except Exception as err:
            print(err)
            
        
        if len(business_addresses) > 0:
            serialized = BusinessAddress_CustomerSerializer(business_addresses, many=True,context={
                                                            'tenant' : tenant.schema_name})
            data = serialized.data
        else:
            raise Exception('0 business addresses found')
        try:
            services_group= ServiceGroup.objects.filter(
                business = str(user_business.id)
                ,is_deleted=False,
                is_blocked=False).order_by('-created_at')
        except Exception as err:
            print(err)    
        
        
        if len(services_group) > 0:
            serialized = ServiceGroupSerializer(services_group,  many=True, context={'request' : request, 'tenant': tenant} )     
            service_group = serialized.data
        else:
            raise Exception('0 business addresses found')
                
    #     else :
    #         raise Exception('Business Not Exist')
    # except Exception as err:
    #     return Response(
    #         {
    #             'status' : False,
    #             'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
    #             'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
    #             'response' : {
    #                 'message' : 'Business Not Found',
    #                 'error_message' : str(err),
    #             }
    #         },
    #         status=status.HTTP_404_NOT_FOUND
    #     )
            
    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : '200',
                'response' : {
                    'message' : 'Business All Locations',
                    'error_message' : None,
                    'count' : len(data),
                    'locations' : data,
                    'service_group': service_group,
                }
            },
            status=status.HTTP_200_OK
        )
    
@api_view(['POST'])
@permission_classes([AllowAny])
def get_check_availability(request):                  
    check_availability = request.data.get('check_availability', None)
    tenant_id = request.data.get('hash', None)
    
    if tenant_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'hash',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    
    try:
        tenant = Tenant.objects.get(id = tenant_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'status_code_text' : 'Invalid Data',
                'response' : {
                    'message' : 'Invalid Tenant Id',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if type(check_availability) == str:
        check_availability = json.loads(check_availability)
    else:
        pass
              
    data = []
    with tenant_context(tenant):
        for check in check_availability:
            emp_id = check.get('member_id', None)
            duration = check.get('duration', None)
            start_time = check.get('app_time', None)
            date = check.get('date', None)
            
            dtime = datetime.strptime(start_time, "%H:%M:%S")
            start_time = dtime.time()
            
            dt = datetime.strptime(date, "%Y-%m-%d")
            date = dt.date()
            
            app_date_time = f'2000-01-01 {start_time}'
        
            duration = DURATION_CHOICES[duration]
            app_date_time = datetime.fromisoformat(app_date_time)
            datetime_duration = app_date_time + timedelta(minutes=duration)
            datetime_duration = datetime_duration.strftime('%H:%M:%S')
            tested = datetime.strptime(datetime_duration ,'%H:%M:%S').time()
            end_time = datetime_duration
                
            try:
                employee = Employee.objects.get(id = emp_id)                
                try:
                    av_staff_ids = AppointmentService.objects.filter(
                        member__id = employee.id,
                        appointment_date = date,
                        # appointment_time__gte = start_time, # 1:00
                        # end_time__lte = start_time, # 1:40
                        # member__employee_employedailyschedule__date = date,
                        # member__employee_employedailyschedule__start_time__lte = start_time,
                        # member__employee_employedailyschedule__end_time__gte = start_time,
                        is_blocked = False,
                    )#.values_list('member__id', flat=True)
                    
                    for ser in av_staff_ids:
                        #data.append(f'{av_staff_ids} type {type(start_time)}, tested {ser.appointment_time}')
                        if tested < ser.appointment_time and start_time > ser.end_time:
                            data.append(f'Employe Already busy  {employee.full_name}')
                                        
                        else:
                            data.append(f'Employees are free, you can proceed further employee name {employee.full_name}')
                    if len(av_staff_ids) == 0:
                        data.append(f'Employees are free, you can proceed further employee name {employee.full_name}')
                        #data.append(f'{av_staff_ids} type {type(datetime_duration)}, ')
                    
                except Exception as err:
                    data.append(f'the employe{employee}, start_time {str(err)}')
            except Exception as err:
                pass
                    
    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : '200',
                'response' : {
                    'message' : 'Employees Check Availability',
                    'error_message' : None,
                    'employee':data
                }
            },
            status=status.HTTP_200_OK
        )
        
@api_view(['GET'])
@permission_classes([AllowAny])
def get_employee_appointment(request):
    date = request.GET.get('date', None)
    start_time = request.GET.get('start_time', None)
    tenant_id = request.GET.get('hash', None)
    
    if tenant_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'hash',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        tenant = Tenant.objects.get(id = str(tenant_id))
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'status_code_text' : 'Invalid Data',
                'response' : {
                    'message' : 'Invalid Tenant Id',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = []
    
    with tenant_context(tenant):
        all_emp = Employee.objects.filter(is_deleted=False).order_by('-created_at')
        for emp in all_emp:
            availability = AppointmentService.objects.filter(
                #member__id__in = empl_list,
                #business = ,
                member__id = emp.id,
                appointment_date = date,
                is_blocked = False,
                appointment_time__lte = start_time, # 1:00
                end_time__gte = start_time,
            )
            if len(availability) >= 0 or len(availability) <= 3 :
                data.append(f'the employe id {emp.id}')
                serializer = EmployeeBusinessSerializer(emp)
                return Response(
                {
                    'status' : True,
                    'status_code' : 200,
                    'status_code_text' : '200',
                    'response' : {
                        'message' : 'Employees are free',
                        'error_message' : None,
                        'employee':serializer.data
                    }
                },
                status=status.HTTP_200_OK
            )
    return Response(
                    {
                        'status' : True,
                        'status_code' : 200,
                        'status_code_text' : '200',
                        'response' : {
                            'message' : 'Employees are free',
                            'error_message' : None,
                            'employee': data
                        }
                    },
                    status=status.HTTP_200_OK
                )
    
@api_view(['POST'])
@permission_classes([AllowAny])
def create_client_business(request):
    tenant_id = request.data.get('hash', None)
    name = request.data.get('full_name', None)
    email = request.data.get('email', None)
    number = request.data.get('mobile_number', None)
    password = request.data.get('password', None)
    
    business_id= request.data.get('business', None)
    
    data = []
    
    if tenant_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'hash',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        tenant = Tenant.objects.get(id = tenant_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'status_code_text' : 'Invalid Data',
                'response' : {
                    'message' : 'Invalid Tenat Id',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )    
    
    with tenant_context(tenant):
       
        try:
            business=Business.objects.get(id=business_id)
        except Exception as err:
            return Response(
            {
                'status' : True,
                'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text' :'BUSINESS_NOT_FOUND_4015' ,
                'response' : {
                    'message' : 'Business not found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
        try:
            client = Client.objects.get(mobile_number__icontains = number )
        except Exception as err:
            client = ''
            pass
        if len(client) > 0:
            data.append(f'Client Phone number already exist {client.full_name}')
        else:
            client  = Client.objects.create(
                #user = tenant.user,
                business = business,
                full_name = name,
                mobile_number=number,
                email = email,
            )
            data.append(f'Client Created Successfully {client.full_name}')
    try:
        username = email.split('@')[0]
        user = User.objects.create(
            first_name = name,
            username = username,
            email = email,
            is_email_verified = True,
            is_active = True,
            mobile_number = number,
        )
        user.set_password(password)
        user.save()
    except Exception as err:
        return Response(
            {
                'status' : True,
                'status_code_text' :'BUSINESS_NOT_FOUND_4015' ,
                'response' : {
                    'message' : 'User not found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
            
    serialized = UserTenantLoginSerializer(user)
     
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Client Create Successfully',
                'error_message' : None,
                'client': serialized.data,
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['POST'])
@permission_classes([AllowAny])
def employee_availability(request):                  
    employee = request.data.get('employee', None)
    tenant_id = request.data.get('hash', None)
    date = request.data.get('date', None)
    
    if tenant_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'hash',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        tenant = Tenant.objects.get(id = tenant_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'status_code_text' : 'Invalid Data',
                'response' : {
                    'message' : 'Invalid Tenant Id',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if type(employee) == str:
        employee = json.loads(employee)
    else:
        pass
              
    data = []
    dt = datetime.strptime(date, "%Y-%m-%d")
    date = dt.date()
            
    with tenant_context(tenant):
        for check in employee:
            emp_id = check.get('member_id', None)
            
            try:
                employee = Employee.objects.get(id = emp_id)                
                av_staff_ids = AppointmentService.objects.filter(
                    
                    member__id = employee.id,
                    appointment_date = date,
                    is_blocked = False,
                ) #.values_list('member__id', flat=True)
                serilizer =  EmployeAppointmentServiceSerializer(av_staff_ids, many = True)
                data.extend(serilizer.data)
            except Exception as err:
                pass
                    
    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : '200',
                'response' : {
                    'message' : 'Employees Check Availability',
                    'error_message' : None,
                    'employee':data
                }
            },
            status=status.HTTP_200_OK
        )