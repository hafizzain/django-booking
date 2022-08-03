

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status

from .serializers import SoftwareSerializer, CountrySerializer, StateSerializer, CitySerializer

from .models import City, Software, Country, State



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