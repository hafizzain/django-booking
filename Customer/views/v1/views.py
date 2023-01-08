
from datetime import datetime
import email
from django.conf import settings
from operator import ge
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Authentication.serializers import UserTenantLoginSerializer
from Authentication.Constants import CreateTenant, AuthTokenConstants, OTP


from Business.models import Business, BusinessAddressMedia, BusinessType
from Client.models import Client
from Employee.models import Employee

from NStyle.Constants import StatusCodes

from Authentication.models import User
from Tenants.models import Domain, Tenant
from Utility.models import Country, Currency, ExceptionRecord, Language, NstyleFile, Software, State, City
from Utility.serializers import LanguageSerializer
import json
from django.db.models import Q

from django_tenants.utils import tenant_context   


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
                    'message' : 'Invalid Tenant Id',
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
        try:
            OTP.generate_user_otp(user=user, code_for='Email')
        except Exception as error:
            ExceptionRecord.objects.create(text=f'Error from create Customer User \n{str(error)}')
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
            
    #serialized = UserTenantLoginSerializer(user)
     
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'End OTP to User email Please verify!',
                'error_message' : None,
                #'client': serialized.data,
            }
        },
        status=status.HTTP_200_OK
    )
    