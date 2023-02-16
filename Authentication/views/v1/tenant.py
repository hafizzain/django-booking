

from Employee.models import Employee
from Employee.serializers import EmployeSerializer
from Tenants.models import EmployeeTenantDetail
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.contrib.auth import authenticate

from Authentication.serializers import  UserTenantLoginSerializer
from Authentication.models import User

from NStyle.Constants import StatusCodes
from django_tenants.utils import tenant_context


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email', None)
    social_account = request.data.get('social_account', False)
    password = request.data.get('password', None)
    employee = False
    
    if social_account:
        social_platform = request.data.get('social_platform', None)
        social_id = request.data.get('social_id', None)
    
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
                        ],
                    'choices_fields' : ['password if social account', 'social_account if logged in with email']
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        if social_account:
            user = User.objects.get(
                email=email,
                is_deleted=False,
                social_account = True,
                social_platform = social_platform,
                social_id = social_id
            )
        else:
            user = User.objects.get(
                email=email,
                is_deleted=False,
            )
            if user.social_account:
                return Response(
                    {
                        'status' : False,
                        'status_code' : StatusCodes.ACCOUNT_ASSOCIATED_WITH_SOCIAL,
                        'status_code_text' : 'ACCOUNT_ASSOCIATED_WITH_SOCIAL',
                        'response' : {
                            'message' : f'This account associated with {user.social_platform}, Please login with {user.social_platform}',
                            'error_message' : 'Social Account trying to login with Email',
                        }
                    },
                    status=status.HTTP_403_FORBIDDEN
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

    if not social_account:
        user = authenticate(username=user.username, password=password)

    if user is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_CREDENTIALS_4013,
                'status_code_text' : 'INVALID_CREDENTIALS_4013',
                'response' : {
                    'message' : 'Invalid Password',
                    'fields' : ['password']
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if not user.is_active:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.USER_ACCOUNT_INACTIVE_4009,
                'status_code_text' : 'USER_ACCOUNT_INACTIVE_4009',
                'response' : {
                    'message' : 'Your account is inactive! Please verify.',
                    'error_message' : 'Account is not active'
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    # elif not user.is_email_verified:
    #     return Response(
    #         {
    #             'status' : False,
    #             'status_code' : StatusCodes.USER_EMAIL_NOT_VERIFIED_4010,
    #             'status_code_text' : 'USER_EMAIL_NOT_VERIFIED_4010',
    #             'response' : {
    #                 'message' : 'Your Email is not verified.',
    #                 'error_message' : 'User Email is not verified yet'
    #             }
    #         },
    #         status=status.HTTP_404_NOT_FOUND
    #     )
    elif not user.is_mobile_verified:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.USER_PHONE_NUMBER_NOT_VERIFIED_4011,
                'status_code_text' : 'USER_PHONE_NUMBER_NOT_VERIFIED_4011',
                'response' : {
                    'message' : 'Your Mobile Number is not verified',
                    'error_message' : 'Users"s mobile number is not verified'
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
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
        
    serialized = UserTenantLoginSerializer(user, context={'employee' : False, })
    return Response(
            {
                'status' : True,
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
def get_user(request):
    user_id = request.GET.get('user', None)
    employee = request.GET.get('employee', None)
    permisson = []

    if user_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Invalid User ID',
                    'fields' : [
                        'user'
                        ],
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(
            id=user_id,
            is_active=True,
            is_deleted=False,
            is_blocked=False
        )
    except:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'User not found',
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )


    if not user.is_active:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.USER_ACCOUNT_INACTIVE_4009,
                'status_code_text' : 'USER_ACCOUNT_INACTIVE_4009',
                'response' : {
                    'message' : 'Your account is inactive! Please verify.',
                    'error_message' : 'Account is not active'
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    elif not user.social_account and not user.is_email_verified:
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
        try:
            emp = Employee.objects.get(email = str(user.email))
            serialized = EmployeSerializer(emp, context={'request' : request, }) #context={'request' : request, })
            response_data = serialized.data
            
            for da in response_data:
                permissions = da['permissions']
                
                permisson.append(permissions)
                
        except Exception as err:
            return str(err)
    
    serialized = UserTenantLoginSerializer(user)
    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : 'Authenticated',
                    'data' : serialized.data,
                    'permission' : permisson
                }
            },
            status=status.HTTP_200_OK
        )