

from Business.models import Business
from Business.serializers.v1_serializers import BusinessGetSerializer
from Product.models import Product
from Product.serializers import ProductSerializer
from Tenants.models import Tenant

from django_tenants.utils import tenant_context


from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status


from .serializers import CurrencySerializer, SoftwareSerializer, CountrySerializer, StateSerializer, CitySerializer

from .models import City, Software, Country, State, Currency

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_currencies(request):
    currencies= Currency.objects.filter(is_deleted=False)
    serialized = CurrencySerializer(currencies, many=True)
    
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'All Currency',
                'error_message' : None,
                'currency' : serialized.data,
                
            }
        },
        status=status.HTTP_200_OK
    )

    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_tenants_product(request):
    data = []
    businesses = []
    tenants= Tenant.objects.all()
    for tnt in tenants:
        with tenant_context(tnt):
            all_products = Product.objects.filter(is_deleted=False).order_by('-created_at')
            serialized = ProductSerializer(all_products, many=True, context={'request' : request})
            data.extend(serialized.data)

            all_businesses = Business.objects.all()
            b_serialized = BusinessGetSerializer(all_businesses , context={'request' : request})
            businesses.append(b_serialized.data)
            print(b_serialized.data)
            
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'All Products and businesses in all tenants',
                'error_message' : None,
                'products' : data,
                'businesses' : businesses,
                
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_softwares(request):
    all_softwares = Software.objects.filter(
        is_active=True,
        is_deleted=False
    )
    serialized = SoftwareSerializer(all_softwares, many=True)
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'All Available Active Softwares',
                'error_message' : None,
                'data' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_countries(request):
    all_countries = Country.objects.filter(
        is_active=True,
        is_deleted=False
    )
    serialized = CountrySerializer(all_countries, many=True)
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'All Available Active Countries',
                'error_message' : None,
                'data' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_states(request):
    country = request.GET.get('country' , None)
    if country is None:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Country ID is missing',
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        all_states = State.objects.filter(
            is_active=True,
            is_deleted=False,
            country__id=country
        )
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Invalid Country ID',
                    'messages' : [i for i in err],
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    serialized = StateSerializer(all_states, many=True)
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'All Available Active States',
                'error_message' : None,
                'data' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_cities(request):
    state = request.GET.get('state', None)
    if state is None:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'State ID is missing',
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        all_city = City.objects.filter(
            is_active=True,
            is_deleted=False,
            state__id=state,
        )
    except Exception as err:
         return Response(
            {
                'status' : False,
                'status_code' : 400,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Invalid State ID',
                    'messages' : [i for i in err],
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    serialized = CitySerializer(all_city, many=True)
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'All Available Active Cities',
                'error_message' : None,
                'data' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_locations_data(request):
    # print(request.META)
    data = []
    for dt in request.META:
        data.append({dt : str(request.META.get(dt))})
    return Response(
        {
            'data' : data
        },
        status=status.HTTP_200_OK
    )