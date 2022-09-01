from http import client
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from Business.models import Business
from Utility.models import Country, State, City
from Client.models import Client


import json

from NStyle.Constants import StatusCodes

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
    crad_number= request.data.get('crad_number' , None)
    is_active = request.data.get('is_active', None)
    
    city= request.data.get('city', None)
    state= request.data.get('state', None)
    country= request.data.get('country', None)
    
    if not all([business_id, client_id, full_name, image , email ,gender  ,address, is_active ]):
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
                        'image',
                        'email',
                        'gender', 
                        'postal_code', 
                        'address' ,
                        'is_active',
                        'business_id',
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
        email= email,
        mobile_number= mobile_number,
        dob=dob,
        gender= gender,
        country= country,
        state = state,
        city = city,
        postal_code = postal_code,
        address=address,
        crad_number=crad_number,
        
    )