from http import client
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from Business.models import Business
from Utility.models import Country, State, City
from Client.models import Client, ClientGroup
from Client.serializers import ClientSerializer, ClientGroupSerializer


import json

from NStyle.Constants import StatusCodes

@api_view(['GET'])
@permission_classes([AllowAny])
def get_client(request):
    all_client=Client.objects.all().order_by('-created_at')
    serialized = ClientSerializer(all_client, many=True,  context={'request' : request})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Staff Group',
                'error_message' : None,
                'employees' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_client(request):
    user = request.user  
    business_id= request.data.get('business', None) 
    
    full_name= request.data.get('full_name', None)
    image = request.data.get('image', None)
    client_id= request.data.get('client_id' ,None)
    
    email= request.data.get('email', None)
    mobile_number= request.data.get('mobile_number', None)    
    
    dob= request.data.get('dob', None)
    gender = request.data.get('gender' , 'Male')
    
    postal_code= request.data.get('postal_code' , None)
    address= request.data.get('address' , None)
    card_number= request.data.get('card_number' , None)
    is_active = request.data.get('is_active', None)
    
    city= request.data.get('city', None)
    state= request.data.get('state', None)
    country= request.data.get('country', None)
    
    if not all([business_id, client_id, full_name , email ,gender  ,address, is_active ]):
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
                        'client_id',
                        'full_name',
                        'email',
                        'gender', 
                        'postal_code', 
                        'address' ,
                        'is_active',
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
    try:
        if country is not None:
            country = Country.objects.get(id=country)
        if state is not None:
            state= State.objects.get(id=state)
        if city is not None:
            city = City.objects.get(id=city)
    except Exception as err:
        return Response(
            {
                'status' : True,
                'status_code' : StatusCodes.INVALID_COUNTRY_STATE_CITY_4021,
                'status_code_text' :'INVALID_COUNTRY_STATE_CITY_4021' ,
                'response' : {
                    'message' : 'Invalid Country, State, City not found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
        
    client=Client.objects.create(
        user=user,
        business=business,
        full_name = full_name,
        image= image,
        client_id=client_id,
        email= email,
        mobile_number=mobile_number,
        dob=dob,
        address=address,
        gender= gender,
        country= country,
        state = state,
        city = city,
        postal_code= postal_code,
        card_number= card_number,
    )
    serialized= ClientSerializer(client, partial=True, context={'request' : request})
    return Response(
        {
            'status' : True,
            'status_code' : 201,
            'response' : {
                'message' : 'Employees Added!',
                'error_message' : None,
                'Client' : serialized.data
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_client(request): 
    # sourcery skip: avoid-builtin-shadow
        id = request.data.get('id', None)
        if id is None:
            return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'User id is required',
                    'fields' : [
                        'id',
                    ]
                }
            },
             status=status.HTTP_400_BAD_REQUEST
           )
        try:
            client = Client.objects.get(id=id)
        except Exception as err:
              return Response(
             {
                    'status' : False,
                    'status_code' : StatusCodes.USER_NOT_EXIST_4005,
                    'status_code_text' : 'USER_NOT_EXIST_4005',
                    'response' : {
                        'message' : 'Client Not Found',
                        'error_message' : str(err),
                    }
                },
                   status=status.HTTP_404_NOT_FOUND
              )
              
        serialized= ClientSerializer(client, data=request.data, partial=True, context={'request' : request})
        if serialized.is_valid():
           serialized.save()
           return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : 'Update Employee Successfully',
                    'error_message' : None,
                    'Employee' : serialized.data
                }
            },
            status=status.HTTP_200_OK
           )
        else:
              return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_EMPLOYEE_PERMISSION_4027,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : str(serialized.errors),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        
        
        
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_client(request):
    client_id = request.data.get('client_id', None)
    if client_id is None:
     return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required.',
                    'fields' : [
                        'client_id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
          
    try:
        client = Client.objects.get(id=client_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Employee ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    client.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Client deleted successful',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_client_group(request):
    user = request.user     
    business_id= request.data.get('business', None)
        
    email= request.data.get('email', None)    
    name = request.data.get('name', None)
    client = request.data.get('client', None)
        
    is_active= request.data.get('is_active' , None)
    
    if not all([ business_id, name, client ]):
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
                          'client',
                          'email', 
                          'name',
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
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Business not found',
                    'error_message' : str(err),
                }
                }
            )
    
    if is_active is not None:
        is_active = json.loads(is_active)
    else: 
        is_active = False
    
    client_group=ClientGroup.objects.create(
        user=user,
        business=business,
        name= name,
        email= email,
        is_active= is_active,
    )
    client_error = []
    if type(client) == str:
            client = json.loads(client)

    elif type(client) == list:
            pass
        
    for usr in client:
            try:
               employe = Client.objects.get(id=usr)  
               client_group.client.add(employe)
            except Exception as err:
                client_error.append(str(err))
        # client_group.save()
        # serialized = ClientGroupSerializer(staff_group)
       
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Staff Group Create!',
                    'error_message' : None,
                    'StaffGroup' : serialized.data,
                    'staff_errors' : employees_error,
                }
            },
            status=status.HTTP_201_CREATED
        ) 
    
    serialized=ClientGroupSerializer(client_group)