from django.shortcuts import render

from django.db import connection
from django.db.models import Q
from Authentication.Constants.CreateTenant import create_tenant
from Authentication.Constants.UserConstants import create_user_account_type, complete_user_account

# from django.contrib.auth.models import User
from Authentication.models import User, VerificationOTP
from Tenants.Constants.tenant_constants import set_schema, verify_tenant_email_mobile
from Tenants.models import EmployeeTenantDetail, Tenant, Domain
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response    
from rest_framework.authtoken.models import Token
from rest_framework import status
from NStyle.Constants import StatusCodes
from threading import Thread
from Authentication.Constants import OTP
from django.contrib.auth import authenticate
from Authentication.serializers import UserLoginSerializer, UserSerializer, UserTenantSerializer
from django_tenants.utils import tenant_context
from Authentication.Constants.Email import send_welcome_email
# Create your views here.

@api_view(['GET'])
@permission_classes([AllowAny])
def all_users(request):
    all_users = User.objects.all()
    serialized = UserSerializer(all_users, many=True)
    return Response(
        {
            'data' : serialized.data
        }
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def create_tenant_business_user(request):
    data = request.data

    first_name = data.get('first_name', None)
    last_name = data.get('last_name', None)
    email = data.get('email', None)
    # username = data.get('username', None)
    mobile_number = data.get('mobile_number', None)
    password = data.get('password', None)
    account_type = data.get('account_type', None)
    business_name = data.get('business_name', None)
    business_industry = data.get('business_industry', None)
    social_account = data.get('social_account', None)

    required_fields = [first_name, last_name, email, mobile_number, account_type ]
    return_fields = ['first_name', 'last_name', 'email', 'mobile_number','account_type']

    if account_type is not None and account_type.lower() == 'business':
        required_fields.append(business_name)
        required_fields.append(business_industry)

        return_fields.append('business_name')
        return_fields.append('business_industry')
        
    if social_account is None:
        required_fields.append(password)
        return_fields.append('password')

    if not all(required_fields) :
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : return_fields
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    if social_account is None and len(password) < 6:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.PASSWORD_STRENGTH_4003,
                'status_code_text' : 'PASSWORD_STRENGTH_4003',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Please enter a strong password.',
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    

    existing_users = User.objects.filter(
        # Q(username=username) |
        Q(email=email) |
        Q(mobile_number=mobile_number)
    )
    if len(existing_users) > 0:
        existing_fields = []
        for usr in existing_users:
            # if usr.username == username:
            #     existing_fields.append('username')
            if usr.email == email:
                existing_fields.append('email')
            
            if usr.mobile_number == mobile_number:
                existing_fields.append('mobile_number')
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.ACCOUNT_ALREADY_EXISTS_4002,
                'status_code_text' : 'ACCOUNT_ALREADY_EXISTS_4002',
                'response' : {
                    'message' : 'User already taken from following fields',
                    'error_message' : 'Account already exist',
                    'taken_fields' : existing_fields
                }
            },status=status.HTTP_400_BAD_REQUEST
        )

    username = f'{first_name} {last_name}'

    
    try:
        User.objects.get(username = username)
        username +=  str(len(User.objects.all()))
    except:
        pass

    try:
        data._mutable = True
    except:
        pass



    if social_account:
       password = 'systemadmin!@#4'

    try:
        data['username'] = username
        data['password'] = password
    except:
        pass

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    try:
        thrd = Thread(target=complete_user_account, args=[request], kwargs={'user' : user, 'data': data})
        thrd.start()
    except:
        pass

    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Account created successfully',
                    'messages' : [
                        'Account created successfully',
                        'Verification OTP has been sent to your mobile number, Please verify'
                    ]
                }
            },
            status=status.HTTP_201_CREATED
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
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
        
        try:
            thrd = Thread(target=verify_tenant_email_mobile, args=[], kwargs={'prev_tenant_name': 'public', 'user' : otp.user ,'verify': code_for})
            thrd.start()
        except Exception as err:
            print('ERROR Threading : ', err)
            pass
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
        serialized = UserTenantSerializer(user)
        s_data = dict(serialized.data)
        s_data['id'] = None
        s_data['access_token'] = None
        try:
            with tenant_context(Tenant.objects.get(user=user)):
                tnt_token = Token.objects.get(user__username=user.username)
                s_data['id'] = str(tnt_token.user.id)
                s_data['access_token'] = str(tnt_token.key)
        except:
            pass

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
                    'data' : s_data
                }
            },
            status=status.HTTP_200_OK
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def get_tenant_detail(request):
    data= {}
    email= request.data.get('email', None)
    
    user = request.user
    
    user_tnt = Tenant.objects.get(user__email=email)
    with tenant_context(user_tnt):
        try:
            tnt_user = User.objects.get(email = email)
            data['id'] = str(tnt_user.id)
            data['access_token'] = str(tnt_user.auth_token.key)
            data['domain'] = str(user_tnt.schema_name)
        
        except Exception as err:
            return Response({
                'status' : False,
                'status_code' : 400,
                'status_code_text' : 'Tenant Not Found',
                'response' : {
                'message' : 'Tenant Data',
                'data' : str(err)   
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : '200',
                'response' : {
                    'message' : 'Tenant Data',
                    'data' : data   
                }
            },
    )
            
    

@api_view(['POST'])
@permission_classes([AllowAny])
def send_verification_otp(request):
    code_for = request.data.get('code_for', None)
    email = request.data.get('email', None)
    mobile_number = request.data.get('mobile_number', None)
    ignore_activity = request.data.get('ignore_activity', False)
     
    if code_for is None or (code_for is not None and code_for == 'Mobile' and mobile_number is None ) or (code_for is not None and code_for == 'Email' and email is None ) :
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
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
            user = User.objects.get(email=email)
        elif code_for == 'Mobile':
            user = User.objects.get(mobile_number=mobile_number)
        
        if ignore_activity:
            pass

        elif (user.is_mobile_verified and code_for == 'Mobile') or (user.is_email_verified and code_for == 'Email'):
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.USER_ALREADY_VERIFIED_4007,
                    'status_code_text' : 'USER_ALREADY_VERIFIED_4007',
                    'response' : {
                        'message' : f'{"Email" if code_for == "Email" and user.is_email_verified else "Mobile Number"} already verified',
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.USER_NOT_EXIST_4005,
                    'status_code_text' : 'USER_NOT_EXIST_4005',
                    'response' : {
                        'message' : f'User with this {"Email" if code_for == "Email" else "Mobile Number"} not exist',
                        'error_fields' : ["email" if code_for == "Email" else "phone_number"],
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

    try:
        otp = VerificationOTP.objects.get(
            code_for='Email' if code_for == 'Email' else 'Mobile' ,
            user=user,
        )
        otp.delete()
    except Exception as err:
        print(err)
        pass

    try:
        thrd = Thread(target=OTP.generate_user_otp, kwargs={'user' : user, 'code_for':f"{'Email' if code_for == 'Email' else 'Mobile'}"})
        thrd.start()
    except:
        pass

    return Response(
            {
                'status' : True,
                'status_code' : StatusCodes.OTP_SEND_SUCCESSFULLY_4008,
                'status_code_text' : 'OTP_SEND_SUCCESSFULLY_4008',
                'response' : {
                    'message' : f'OTP sent to your {"Email" if code_for == "Email" else "Mobile Number"}',
                }
            },
            status=status.HTTP_200_OK
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email', None)
    social_account = request.data.get('social_account', False)
    password = request.data.get('password', None)
    
    employee = False
    if social_account:
        social_platform = request.data.get('social_platform', None)
    s_data = {}
    
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
    
    connection.set_schema_to_public()
    try:
        user = User.objects.filter(
            email=email,
            is_deleted=False
        ).exclude(user_account_type__account_type = 'Everyone')[0]
    
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
    # else:
    #     user = User.objects.get(
    #         email__icontans =email,
    #         is_deleted=False,
    #         user_account_type__account_type = 'Employee'
    #     )[0]
    #     employee = True 
    try:
        user = User.objects.get(
            email =email,
            is_deleted=False,
            user_account_type__account_type = 'Employee'
        )
        employee = True
    except Exception as err: 
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_CREDENTIALS_4013,
                    'status_code_text' : 'INVALID_CREDENTIALS_4013',
                    'response' : {
                        'message' : f'testing phase {str(err)}',
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
    if employee:
        #s_data['id'] = None
        employe_user = EmployeeTenantDetail.objects.get(user = user)
        with tenant_context(employe_user.tenant):
            user = User.objects.get(
                email=email,
                is_deleted=False,
                user_account_type__account_type = 'Employee'
            )
            serialized = UserLoginSerializer(user, context={'employee' : True, })
            s_data = dict(serialized.data)
            
    # else:
    #     serialized = UserLoginSerializer(user, context={'employee' : False, })
    #     s_data = dict(serialized.data)
    #     s_data['id'] = None
    #     s_data['access_token'] = None
    #     try:
    #         with tenant_context(Tenant.objects.get(user=user)):
    #             tnt_token = Token.objects.get(user__username=user.username)
    #             s_data['id'] = str(tnt_token.user.id)
    #             s_data['access_token'] = str(tnt_token.key)
    #     except:
    #         pass


    return Response(
            {
                'status' : False,
                'status_code' : 200,
                'response' : {
                    'message' : 'Authenticated',
                    #'data' : serialized.data
                    'data' : employee
                }
            },
            status=status.HTTP_200_OK
        )


@api_view(['PUT'])
@permission_classes([AllowAny])
def change_password(request):
    password = request.data.get('password', None)
    email = request.data.get('email', None)
    mobile_number = request.data.get('mobile_number', None)

    if password is None or not any([email, mobile_number]):
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
                        'mobile_number',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        if email is not None:
            user = User.objects.get(email=email)
        elif mobile_number is not None:
            user = User.objects.get(mobile_number=mobile_number)
        else:
            raise Exception('User not exist')
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

    user.set_password(password)
    user.save()

    return Response(
            {
                'status' : False,
                'status_code' : 200,
                'response' : {
                    'message' : 'Password Changed'
                }
            },
            status=status.HTTP_200_OK
        )