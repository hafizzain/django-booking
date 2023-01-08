
from datetime import datetime
import email
from threading import Thread
from django.conf import settings
from operator import ge
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Authentication.Constants.Email import send_welcome_email
from Authentication.serializers import UserTenantLoginSerializer
from Authentication.Constants import CreateTenant, AuthTokenConstants, OTP


from Business.models import Business, BusinessAddressMedia, BusinessType
from Client.models import Client
from Employee.models import Employee

from NStyle.Constants import StatusCodes

from Authentication.models import User, VerificationOTP
from Tenants.models import Domain, Tenant
from Utility.models import Country, Currency, ExceptionRecord, Language, NstyleFile, Software, State, City
from Utility.serializers import LanguageSerializer
import json
from django.db.models import Q
from rest_framework.authtoken.models import Token


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
    
    
@api_view(['POST'])
@permission_classes([AllowAny])
def customer_verify_otp(request):
    code = request.data.get('code', None)
    code_for = request.data.get('code_for', None)
    email = request.data.get('email', None)
    mobile_number = request.data.get('mobile_number', None)
    change_password = request.data.get('change_password', None)

    if not all([code, code_for]) or (code_for is not None and code_for == 'Mobile' and mobile_number is None ) or (code_for is not None and code_for == 'Email' and email is None ) :
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'code',
                        'code_for',
                        'email',
                        'mobile_number',
                        ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if code_for is not None and code_for not in ['Mobile', 'Email']:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_CHOICE_4004,
                'status_code_text' : 'INVALID_CHOICE_4004',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Invalid Choice.',
                    'valid_choices' : [
                        'Mobile',
                        'Email'
                        ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        if code_for == 'Email':
            otp = VerificationOTP.objects.get(
                code_for='Email',
                user__email=email,
                code=code
            )
            otp.user.is_email_verified = True
            otp.user.is_active = True
            otp.user.save()
            otp.delete()
        elif code_for == 'Mobile':
            otp = VerificationOTP.objects.get(
                code_for='Mobile',
                user__mobile_number=mobile_number,
                code=code
            )
            otp.user.is_mobile_verified = True
            otp.user.is_active = True
            otp.user.save()
            otp.delete()
        else:
            otp = None
            raise Exception('Verification OTP not found')
        
        # try:
        #     thrd = Thread(target=verify_tenant_email_mobile, args=[], kwargs={'prev_tenant_name': 'public', 'user' : otp.user ,'verify': code_for})
        #     thrd.start()
        # except Exception as err:
        #     print('ERROR Threading : ', err)
        #     pass
    except Exception as err:
        print(err)
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_OTP_4006,
                'status_code_text' : 'INVALID_OTP_4006',
                'response' : {
                    'message' : 'OTP not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if otp is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_OTP_4006,
                'status_code_text' : 'INVALID_OTP_4006',
                'response' : {
                    'message' : 'OTP not found',
                    'error_message' : str(err),
                    'messages': ['OTP not exist', 'May be something went wrong'],
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    s_data = dict()
    if change_password is None:
        user = otp.user
        serialized = UserTenantLoginSerializer(user)
        #s_data = dict(serialized.data)
        
        # try:
        #     with tenant_context(Tenant.objects.get(user=user)):
        #         tnt_token = Token.objects.get(user__username=user.username)
        #         s_data['id'] = str(tnt_token.user.id)
        #         s_data['access_token'] = str(tnt_token.key)
        # except:
        #     pass
    try:
        thrd = Thread(target=send_welcome_email(user=otp.user))
        thrd.start()
    except:
        pass
    return Response(
            {
                'status' : True,
                'status_code' : StatusCodes.OTP_VERIFIED_2001,
                'status_code_text' : 'OTP_VERIFIED_2001',
                'response' : {
                    'message' : 'OTP Verified',
                    'data' : serialized.data
                }
            },
            status=status.HTTP_200_OK
        )
    