import json
from threading import Thread
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from Business.models import Business
from CRM.models import Segment
from CRM.serializers import SegmentSerializer
from Client.models import Client
from Utility.models import NstyleFile
from NStyle.Constants import StatusCodes

@api_view(['GET'])
@permission_classes([AllowAny])
def get_segment(request):
    all_segment = Segment.objects.filter(is_deleted = False).order_by('-created_at')
    serialized = SegmentSerializer(all_segment , many = True)
    
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'All Segment',
                'error_message' : None,
                'segment': serialized.data,
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_segment(request):
    user = request.user  
    business_id= request.data.get('business', None) 
    
    name = request.data.get('name', None) 
    segemnt_type = request.data.get('segemnt_type', None) 
    
    client = request.data.get('client', None) 
    description = request.data.get('description', None) 
    
    is_status = request.data.get('is_status', None) 
    
    segment_error = []
    
    if not all([business_id, name, segemnt_type , description ]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'business_id',
                        'name',
                        'segemnt_type',
                        'description',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
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
    segment = Segment.objects.create(
        user = user,
        business = business,
        
        name =  name,
        segemnt_type = segemnt_type,
        description = description
    )
    
    if is_status is not None:
        segment.is_active = True
    else:
         segment.is_active = False
         
    if client is not None:
        if type(client) ==  str:
            client = json.loads(client)
            
        for usr in client:
            try:
                employe = Client.objects.get(id=usr)  
                segment.client.add(employe)
            except Exception as err:
                segment_error.append(str(err))
    segment.save()
    serialized = SegmentSerializer(segment)
    
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Segment Created successfully',
                'error_message' : None,
                'segment': serialized.data,
                'segment_error' : segment_error
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_segment(request):
    segment_id = request.data.get('id', None)
    if id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required.',
                    'fields' : [
                        'id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
          
    try:
        segment = Segment.objects.get(id=segment_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Segment ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    segment.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Segment deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_segment(request):
    segment_id = request.data.get('id', None)
    client = request.data.get('client', None) 

    if segment_id is None: 
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.MISSING_FIELDS_4001,
            'status_code_text' : 'MISSING_FIELDS_4001',
            'response' : {
                'message' : 'Invalid Data!',
                'error_message' : 'Subscription ID are required.',
                'fields' : [
                    'id'                         
                ]
            }
        },
        status=status.HTTP_400_BAD_REQUEST
        )
    try:
        segment = Segment.objects.get(id=segment_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code_text' : 'INVALID_SEGMENT_ID',
                'response' : {
                    'message' : 'Segment Not Found',
                    'error_message' : str(err),
                }
            },
                status=status.HTTP_404_NOT_FOUND
        )
    segment_error =[]
    if client is not None:
        if type(client) ==  str:
            client = json.loads(client)
            
        for usr in client:
            try:
                employe = Client.objects.get(id=usr)  
                segment.client.add(employe)
            except Exception as err:
                print(err)
                segment_error.append(str(err))
    segment.save()
    serializer = SegmentSerializer(segment, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Segment Serializer Invalid',
                'error_message' : str(serializer.errors),
            }
        },
        status=status.HTTP_404_NOT_FOUND
        )
    serializer.save()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Update Segment Successfully',
                'error_message' : None,
                'segment' : serializer.data,
                'segment_error' : segment_error,
            }
        },
        status=status.HTTP_200_OK
        )