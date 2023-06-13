
from datetime import datetime, timedelta
import email
from threading import Thread
from django.conf import settings
from operator import ge
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Appointment.Constants.durationchoice import DURATION_CHOICES
from Appointment.models import Appointment, AppointmentNotes, AppointmentService
from Authentication.Constants.Email import send_welcome_email
from Authentication.serializers import UserSerializerByClient, UserTenantLoginSerializer
from Authentication.Constants import CreateTenant, AuthTokenConstants, OTP
from django.contrib.auth import authenticate, logout


from Business.models import Business, BusinessAddressMedia, BusinessType
from Client.models import Client
from Client.serializers import Client_TenantSerializer, ClientSerializer
from Customer.serializers import AppointmentClientSerializer, AppointmentServiceClientSerializer
from Employee.models import Employee

from NStyle.Constants import StatusCodes

from Authentication.models import AccountType, User, VerificationOTP
from Tenants.models import ClientIdUser, ClientTenantAppDetail, Domain, Tenant
from Utility.Constants.Data.Durations import DURATION_CHOICES_DATA
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
    client_auto_id= request.data.get('client_id' ,None)    
    business_id= request.data.get('business', None)
    
    data = []
    
    try:
        user = User.objects.get(email__icontains = email, user_account_type__account_type = 'Everyone' )
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'status_code_text' : StatusCodes.USER_ALREADY_VERIFIED_4007,
                'response' : {
                    'message' : 'Account Exit',
                    'error_message' : 'Account Already Exist on this Email',
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as err:
        pass
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
            data.append(f'Client Email already exist tenant{client.full_name}')
            
        else:
            client  = Client.objects.create(
                #user = user,
                business = business,
                full_name = name,
                mobile_number=number,
                email = email,
                client_id = client_auto_id,
                is_active = True
            )
            client_id = client.id
            data.append(f'Client Created Successfully {client.full_name}')
            
    try:
        username = email.split('@')[0]
        if username:
            try:
                user_check = User.objects.get(username = username)
            except Exception as err:
                data.append(f'username user is errors  {str(err)}')
                #data.append(f'username user is  {user_check}')
                pass
            else:
                username = f'{username} {len(User.objects.all())}'
                data.append(f'username user is {username}')
    except Exception as err:
        data.append(f'Client errors {str(err)}')
        
    try:
        if client:
            data.append(f'Client Email already exist  in if else condition {client.full_name}')
            
            try:
                username = client.email.split('@')[0]
                try:
                    user_check = User.objects.get(username = username)
                except Exception as err:
                    data.append(f'username user is client errors {str(err)}')
                    #data.append(f'username user is  {user_check}')
                    pass
                else:
                    username = f'{username} {len(User.objects.all())}'
                    data.append(f'username user is {username}')
            except Exception as err:
                data.append(f'Client errors {str(err)}')
            
            user = User.objects.create(
                first_name = str(client.full_name),
                username = username,
                email = str(client.email),
                is_email_verified = True,
                is_active = True,
                mobile_number = str(client.mobile_number),
            )
            account_type = AccountType.objects.create(
                user = user,
                account_type = 'Everyone'
            )
            # client_id = ClientIdUser.objects.get(user = user. )
            # if client_id:
            #     pass
            # else:
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
                'message' : 'We have sent the OTP on your email!',
                'error_message' : None,
                'client': data,
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
    otp = None
    try:
        if code_for == 'Email':
            otp = VerificationOTP.objects.get(
                code_for='Email',
                user__email=email,
                code=code
            )
            user = otp.user
            user.is_email_verified = True
        
        elif code_for == 'Mobile':
            otp = VerificationOTP.objects.get(
                code_for='Mobile',
                user__mobile_number=mobile_number,
                code=code
            )
            user = otp.user
            user.is_mobile_verified = True
        else:
            otp = None
            raise Exception('Verification OTP not found')

    except Exception as err:
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
            status = status.HTTP_400_BAD_REQUEST
        )
    else:
        user.is_active = True
        user.save()
        otp.delete()
        try:
            user_tenant = Tenant.objects.get(user = user)
        except:
            pass
        else:
            with tenant_context(user_tenant):
                try:
                    t_user = User.objects.get(email = user.email)
                except:
                    pass
                else:
                    t_user.is_active = True
                    if code_for == 'Email':
                        t_user.is_email_verified = True
                    elif code_for == 'Mobile':
                        t_user.is_mobile_verified = True

                    t_user.save()

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
    
    token, created = Token.objects.get_or_create(user=otp.user)
        
    if change_password is None:
        serialized = UserSerializerByClient(user)
    try:
        thrd = Thread(target=send_welcome_email(user=user))
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
    
    tenant_id = request.GET.get('tenant_id', None)

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
            is_deleted=False,
            user_account_type__account_type = 'Everyone'
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

    serialized = UserSerializerByClient(user, context={'tenant_id' : tenant_id})
    
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
            serializer = AppointmentClientSerializer(app_service, many = True, context={'request' : request,'tenant' : tenant.tenant.schema_name})
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

@api_view(['PUT'])
@permission_classes([AllowAny])
def cancel_appointment_client(request):
    appointment_id = request.GET.get('appointment_id', None)
    hash = request.GET.get('hash', None)
    appointment_notes = request.data.get('appointment_notes', None)
    
    data = []    
    if appointment_id and hash is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'appointment_id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        tenant = Tenant.objects.get(id = hash)
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
            appointment = Appointment.objects.get(id=str(appointment_id))
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : 404,
                    'status_code_text' : '404',
                    'response' : {
                        'message' : 'Invalid Appointment ID!',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        appointment_service = AppointmentService.objects.filter(appointment=appointment.id)
        for app_service in appointment_service:
            app_service.appointment_status = 'Cancel'
            app_service.save()
        
        try:
            appointment_notes = AppointmentNotes.objects.get( appointment = appointment)
            appointment_notes.text = appointment_notes
            appointment_notes.save()
        except Exception as err:
            #pass
            AppointmentNotes.objects.create(
                appointment = appointment,
                text = appointment_notes
            )
        
        serializer = AppointmentClientSerializer(appointment, context={'request' : request})
        data.append(serializer.data)
        # try:
        #     thrd = Thread(target=cancel_appointment, args=[] , kwargs={'appointment' : service_appointment, 'tenant' : request.tenant} )
        #     thrd.start()
        # except Exception as err:
        #     print(err)
        #     pass
            
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Cancel Appointment Successfully',
                'error_message' : None,
                'appointment': serializer.data
            }
        },
        status=status.HTTP_200_OK
    )
    
    
@api_view(['PUT'])
@permission_classes([AllowAny])
def update_appointment_client(request):
    appointment_service = request.data.get('appointment_service', None)
    hash = request.data.get('hash', None)
    
    data = []    
    if appointment_service and hash is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'appointment_id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        tenant = Tenant.objects.get(id = hash)
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
    appointment = ''
    
    with tenant_context(tenant):
        if type(appointment_service) == str:
            appointment_service = appointment_service.replace("'" , '"')
            appointment_service = json.loads(appointment_service)
        else:
            pass
        
        for service in appointment_service:
            try:
                date = service.get('date', None)
                date_time = service.get('date_time', None)
                app_duration = service.get('duration', None)
                id = service.get('id', None)
                
                app_date_time = f'2000-01-01 {date_time}'
        
                duration = DURATION_CHOICES[app_duration]
                app_date_time = datetime.fromisoformat(app_date_time)
                datetime_duration = app_date_time + timedelta(minutes=duration)
                datetime_duration = datetime_duration.strftime('%H:%M:%S')
                end_time = datetime_duration
                
                appoint_service = AppointmentService.objects.get(id = str(id))
                appoint_service.appointment_date = date
                appoint_service.appointment_time = date_time
                appoint_service.end_time = end_time
                appointment = appoint_service.appointment.id
                appoint_service.save()
                
                serializer = AppointmentServiceClientSerializer(appoint_service, context={'request' : request})
                data.append(serializer.data)
            except Exception as err:
                data.append(str(err))
                #pass

    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Update Appointment Successfully',
                'error_message' : None,
                'appointment_id': appointment,
                'appointment': data,
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def generate_id(request):
    
    hash = request.GET.get('hash', None)
    
    if hash is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'hash'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        tenant = Tenant.objects.get(id = hash)
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
        tenant_name = tenant.schema_name
        tenant_name = tenant_name.split('-')
        tenant_name = [word[0] for word in tenant_name]
        print(tenant_name)
        ''.join(tenant_name)
        count = Client.objects.all().count()
        count += 1
    
        return_loop = True
        while return_loop:
            if 0 < count <= 9 : 
                count = f'000{count}'
            elif 9 < count <= 99 :
                count = f'00{count}'
            elif 99 < count <= 999:
                count = f'0{count}'
            new_id =f'{tenant_name}-CLI-{count}'
            
            try:
                Client.objects.get(employee_id=new_id)
                count += 1
            except:
                return_loop = False
                break
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Generated ID',
                'error_message' : None,
                'id' : new_id
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_client_detail(request):
    hash = request.GET.get('hash', None)
    client_id = request.GET.get('client_id', None)
    client_email = request.GET.get('client_email', None)


    data = []
    errors = []

    try:
        user = User.objects.get(
            email = client_email,
            user_account_type__account_type = 'Everyone'
        )
    except:
        errors.append(str(err))
    else:
        user_data = {
            'id' : f'{user.id}',
            'full_name' : f'{user.first_name} {user.last_name if user.last_name else ''}',
            'image' : '',
            'client_id' : '',
            'email' : '',
            'mobile_number' : '',
            'dob' : '',
            'postal_code' : '',
            'address' : '',
            'gender' : '',
            'card_number' : '',
            'country' : '',
            'city' : '',
            'state' : '',
            'is_active' : '',
            'language' : '',
            'about_us' : '',
            'marketing' : '',
            'country_obj' : '',
            'customer_note' : '',
            'created_at' : '',
        }
        data.append(user_data)
        return Response(
            {
                'status' : 200,
                'status_code' : '200',
                'response' : {
                    'message' : 'All Client',
                    'error_message' : errors,
                    'client' : data
                }
            },
            status=status.HTTP_200_OK
        )

    if hash is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'hash'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        tenant = Tenant.objects.get(id = hash)
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
            all_client=Client.objects.get(id = client_id)
            serialized = Client_TenantSerializer(all_client, context={'request' : request,'tenant' : tenant.schema_name })
            data.append(serialized.data)
        except Exception as err:
            # client_id = request.GET.get('client_id', None)
            errors.append(str(err))
            pass
            
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Client',
                'error_message' : errors,
                'client' : data
            }
        },
        status=status.HTTP_200_OK
    )

            