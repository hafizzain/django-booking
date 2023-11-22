from rest_framework import status
from Business.models import Business
from Utility.models import Country, State, City
from Authentication.models import User
from NStyle.Constants import StatusCodes
import json
from Utility.models import NstyleFile
from django.db.models import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import render
from rest_framework.response import Response


from Service.models import Service

from Sale.serializers import ServiceSerializer, ServiceSerializerDropdown

# from Service.models import Service
# from Service.serializers import ServiceSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def get_services(request):
    
    query = Q(is_deleted=False)
    service= Service.objects.filter(query).order_by('-created_at')
    serialized = ServiceSerializer(service,  many=True, )
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Service',
                'error_message' : None,
                'service' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_services_dropdown(request):
    
    query = Q(is_deleted=False, is_active=True)
    services = Service.objects.filter(query).order_by('-created_at')
    serialized = ServiceSerializerDropdown(services,  many=True)
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Service',
                'error_message' : None,
                'service' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    

# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_services(request):
#     all_services = Service.objects.all().order_by('-created_at')
#     serialized = ServiceSerializer(all_services,  many=True )
#     return Response(
#         {
#             'status' : 200,
#             'status_code' : '200',
#             'response' : {
#                 'message' : 'All Service',
#                 'error_message' : None,
#                 'service' : serialized.data
#             }
#         },
#         status=status.HTTP_200_OK
#     )