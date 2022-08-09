


from operator import ge
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from Business.models import BusinessType
from Business.serializers.v1_serializers import BusinessTypeSerializer

from NStyle.Constants import StatusCodes

from Authentication.models import User
from Business.models import Business, BusinessSocial, BusinessAddress, BusinessOpeningHour
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


    print(type(opening_hours))
    print(type(business_types))
    print(type(software_used))

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

        # tenant_user = User.objects.get(
        #     is_superuser=True,
        #     username=user.username
        # )
        # user_business = Business.objects.create(
        #     user=tenant_user,
        #     business_name=business_name,
        # )
        # business_social = BusinessSocial.objects.create(
        #     business=user_business,
        #     user=tenant_user,
        #     website=website
        # )
        # business_address = BusinessAddress.objects.create(
        #     user=tenant_user,
        #     business=user_business,
        #     country=tnt_country,
        #     state=tnt_state,
        #     city=tnt_city,
        #     address=address,
        #     email=tenant_user.email,
        #     mobile_number=user.mobile_number
        # )

        # address_hours = BusinessOpeningHour.objects.create(
        #     business=user_business,
        #     business_address=business_address,
        #     day='Sunday',
        #     start_time='',
        #     close_time='',
        # )

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