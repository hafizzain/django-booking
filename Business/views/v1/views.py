


from operator import ge
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from Business.models import BusinessType
from Business.serializers.v1_serializers import BusinessTypeSerializer, Business_GetSerializer, Business_PutSerializer, BusinessAddress_GetSerializer, BusinessThemeSerializer

from NStyle.Constants import StatusCodes

from Authentication.models import User
from Business.models import Business, BusinessSocial, BusinessAddress, BusinessOpeningHour, BusinessTheme
from Tenants.models import Domain, Tenant
from Utility.models import Country, State, City

from django_tenants.utils import tenant_context

@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_types(request):
    all_types = BusinessType.objects.filter(
        is_active=True,
        is_deleted=False
    )
    serialized = BusinessTypeSerializer(all_types, many=True)
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
    
    serialized = Business_GetSerializer(user_business)

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
        domain = None
        with tenant_context(Tenant.objects.get(schema_name = 'public')):
            domain = Domain.objects.get(domain__icontains=domain_name)

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
                        'logo' : user_business.logo if user_business.logo else None ,
                    }
                }
            },
            status=status.HTTP_200_OK
        )


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
        if fb_url is not None:
            business_social.facebook = fb_url
        if insta_url is not None:
            business_social.instagram = insta_url
        
        business_social.save()
    
        logo = request.data.get('logo', None)
        if logo is not None:
            business.logo = logo
            business.save()
        serialized = Business_GetSerializer(business)
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
    )
    data = []
    if len(business_addresses) > 0:
        serialized = BusinessAddress_GetSerializer(business_addresses, many=True)
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
    country_id = request.data.get('country', None)
    state_id = request.data.get('state', None)
    city_id = request.data.get('city', None)
    postal_code = request.data.get('postal_code', None)

    if not all([business_id, address, address_name, country_id, state_id, city_id, postal_code]):
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
                        'country',
                        'state',
                        'city',
                        'postal_code',
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
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        country = Country.objects.get( id=country_id, is_deleted=False, is_active=True )
        state = State.objects.get( id=state_id, is_deleted=False, is_active=True )
        city = City.objects.get( id=city_id, is_deleted=False, is_active=True )
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
        postal_code = postal_code,
        country=country,
        state=state,
        city=city,
        is_primary = False,
        is_active = True,
        is_deleted = False,
        is_closed = False,
    )
    business_address.save()

    serialized = BusinessAddress_GetSerializer(business_address)

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
        business_address.delete()
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
        business_address.address_name = request.data.get('address_name', business_address.address_name)
        business_address.address = request.data.get('address', business_address.address)
        business_address.postal_code = request.data.get('postal_code', business_address.postal_code)

        country = request.data.get('country', None)
        state = request.data.get('state', None)
        city = request.data.get('city', None)

        try:
            country = Country.objects.get( id=country, is_deleted=False, is_active=True )
            state = State.objects.get( id=state, is_deleted=False, is_active=True )
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

        business_address.save()

        serialized = BusinessAddress_GetSerializer(business_address)

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
                    'message' : 'Business Theme',
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

@api_view('POST')
@permission_classes([IsAuthenticated])
def add_business_language(request):
    business = request.data.get('business', None)

    return Response(
        {
            'status' : True,
            'status_code' : 400,
            'status_code_text' : 'INVALID DATA',
            'response' : {
                'message' : 'Language Added',
                'error_message' : None,
            }
        },
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view('POST')
@permission_classes([IsAuthenticated])
def update_language(request):
    business = request.data.get('business', None)

    return Response(
        {
            'status' : True,
            'status_code' : 400,
            'status_code_text' : 'INVALID DATA',
            'response' : {
                'message' : 'Language Added',
                'error_message' : None,
            }
        },
        status=status.HTTP_400_BAD_REQUEST
    )