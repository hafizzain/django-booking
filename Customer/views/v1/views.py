
from datetime import datetime
import email
from threading import Thread
from django.conf import settings
from operator import ge
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Appointment.models import Appointment, AppointmentService
from Authentication.Constants.Email import send_welcome_email
from Authentication.serializers import UserSerializerByClient, UserTenantLoginSerializer
from Authentication.Constants import CreateTenant, AuthTokenConstants, OTP
from django.contrib.auth import authenticate, logout


from Business.models import Business, BusinessAddressMedia, BusinessType
from Client.models import Client
from Customer.serializers import AppointmentClientSerializer
from Employee.models import Employee

from NStyle.Constants import StatusCodes

from Authentication.models import AccountType, User, VerificationOTP
from Tenants.models import ClientIdUser, ClientTenantAppDetail, Domain, Tenant
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
    client = ''
    client_id = ''
   
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
            client = Client.objects.get(email__icontains = email )
            client = client
            client_id = client.id
        except Exception as err:
            pass
        
        # try:
        #     user = User.objects.get(id = tenant.user.id )
        # except Exception as err:
        #     pass
        
        if client:
            data.append(f'Client Email already exist {client.full_name}')
            
        else:
            client  = Client.objects.create(
                #user = user,
                business = business,
                full_name = name,
                mobile_number=number,
                email = email,
            )
            client_id = client.id
            data.append(f'Client Created Successfully {client.full_name}')
            
    try:
        username = email.split('@')[0]
        if username:
            try:
                user_check = User.objects.get(username = username)
            except Exception as err:
                pass
            else:
                # return Response(
                #     {
                #         'status' : True,
                #         'status_code_text' :'USER_ALREADY_EXIST' ,
                #         'response' : {
                #             'message' : 'User are Exist with this username!',
                #             'error_message' : user_check.username,
                #         }
                #     },
                #     status=status.HTTP_404_NOT_FOUND
                # )
                username = f'{username} {len(User.objects.all())}'

        if client:
            data.append(f'Client Email already exist {client.full_name}')
    
            user = User.objects.create(
                first_name = str(client.full_name),
                username = str(client.full_name),
                email = str(client.email),
                is_email_verified = True,
                is_active = True,
                mobile_number = str(client.mobile_number),
            )
            account_type = AccountType.objects.create(
                user = user,
                account_type = 'Everyone'
            )
            user_client = ClientIdUser.objects.create(
                user = user,
                client_id = client_id,
                is_everyone = True
            )
        else:
            user = User.objects.create(
                first_name = name,
                username = username,
                email = email,
                is_email_verified = True,
                is_active = True,
                mobile_number = number,
            )
            account_type = AccountType.objects.create(
                user = user,
                account_type = 'Everyone'
            )
            user_client = ClientIdUser.objects.create(
                user = user,
                client_id = client_id,
                is_everyone = True
                
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
    try:
        token = Token.objects.get(user=otp.user)
    except Token.DoesNotExist:
        token = Token.objects.create(user=otp.user)
        
    if change_password is None:
        user = otp.user
        serialized = UserSerializerByClient(user)
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


@api_view(['POST'])
@permission_classes([AllowAny])
def customer_login(request):
    email = request.data.get('email', None)
    social_account = request.data.get('social_account', False)
    password = request.data.get('password', None)

    if social_account:
        social_platform = request.data.get('social_platform', None)
    
    if not email or (not social_account and not password ) or (social_account and not social_platform ):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'email',
                        'password',
                        'social_account',
                        'social_platform',
                        ],
                    'choices_fields' : ['password if social account', 'social_account if logged in with email']
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    #connection.set_schema_to_public()
    try:
        user = User.objects.get(
            email=email,
            is_deleted=False
        )
        
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_CREDENTIALS_4013,
                'status_code_text' : 'INVALID_CREDENTIALS_4013',
                'response' : {
                    'message' : 'User does not exist with this email',
                    'error_message' : str(err),
                    'fields' : ['email']
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )


    if not social_account and not user.is_active:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.USER_ACCOUNT_INACTIVE_4009,
                'status_code_text' : 'USER_ACCOUNT_INACTIVE_4009',
                'response' : {
                    'message' : 'This account is inactive! Please verify.',
                    'error_message' : 'Account is not active'
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if user.social_account and not social_account:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.ACCOUNT_ASSOCIATED_WITH_SOCIAL,
                'status_code_text' : 'ACCOUNT_ASSOCIATED_WITH_SOCIAL',
                'response' : {
                    'message' : f'This Account associated with {user.social_platform}, Please signin with {user.social_platform}',
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if not social_account:
        user = authenticate(username=user.username, password=password)
        if user is None:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_CREDENTIALS_4013,
                    'status_code_text' : 'INVALID_CREDENTIALS_4013',
                    'response' : {
                        'message' : 'Incorrect Password',
                        'fields' : ['password']
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

    if not social_account and not user.is_email_verified:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.USER_EMAIL_NOT_VERIFIED_4010,
                'status_code_text' : 'USER_EMAIL_NOT_VERIFIED_4010',
                'response' : {
                    'message' : 'Your Email is not verified.',
                    'error_message' : 'User Email is not verified yet'
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    # elif not user.is_mobile_verified:
    #     return Response(
    #         {
    #             'status' : False,
    #             'status_code' : StatusCodes.USER_PHONE_NUMBER_NOT_VERIFIED_4011,
    #             'status_code_text' : 'USER_PHONE_NUMBER_NOT_VERIFIED_4011',
    #             'response' : {
    #                 'message' : 'Your Mobile Number is not verified',
    #                 'error_message' : 'Users"s mobile number is not verified'
    #             }
    #         },
    #         status=status.HTTP_404_NOT_FOUND
    #     )
    elif user.is_blocked:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.USER_ACCOUNT_IS_BLOCKED_4012,
                'status_code_text' : 'USER_ACCOUNT_IS_BLOCKED_4012',
                'response' : {
                    'message' : 'Your Account is blocked! Contact our support',
                    'error_message' : 'Users"s Account is blocked, Can"t access this account'
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    serialized = UserSerializerByClient(user)
    
    return Response(
            {
                'status' : False,
                'status_code' : 200,
                'response' : {
                    'message' : 'Authenticated',
                    'data' : serialized.data
                }
            },
            status=status.HTTP_200_OK
        )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_client_appointment(request):
    client_id = request.GET.get('client_id', None)
    data = []
    
    if client_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'client_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    
    client_app = ClientTenantAppDetail.objects.filter(client_id__icontains = client_id)
    
    for tenant in client_app:
        with tenant_context(tenant.tenant):
            try:
                client = Client.objects.get(id = str(client_id))
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
            today = datetime.today()
            app_service = Appointment.objects.filter(client = client) 
                                #created_at__gte = day )
            serializer = AppointmentClientSerializer(app_service, many = True, context={'request' : request})
            data.extend(serializer.data)

    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : 'All Appointment Client',
                    'error_message' : None,
                    'appointment': data
                }
            },
            status=status.HTTP_200_OK
        )