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
from Sale.Constants.Custom_pag import CustomPagination

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
    no_pagination = request.GET.get('no_pagination', None)
    page = request.GET.get('page', None)

    
    query = Q(is_deleted=False)
    services = Service.objects.filter(query).prefetch_related('servicegroup_services').order_by('-created_at')

    serialized = list(ServiceSerializerDropdown(services,  many=True).data)

    paginator = CustomPagination()
    paginator.page_size = 1000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'services', extra=None, current_page=page)
    return response
    

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