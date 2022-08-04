from django.shortcuts import render

from django.http import HttpResponse

from django_tenants.utils import tenant_context
from django.db.models import Q
from Authentication.Constants.CreateTenant import create_tenant
from Authentication.Constants.UserConstants import create_user_account_type, complete_user_account

# from django.contrib.auth.models import User
from Authentication.models import User, VerificationOTP
from Tenants.models import Tenant, Domain
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from NStyle.Constants import StatusCodes
from threading import Thread

import random
import string
# Create your views here.


@api_view(['POST'])
def create_tenant_business_user(request):
    data = request.data

    first_name = data.get('first_name', None)
    email = data.get('email', None)
    username = data.get('username', None)
    mobile_number = data.get('mobile_number', None)
    password = data.get('password', None)
    account_type = data.get('account_type', None)

    if not all([first_name, email, username, mobile_number, password, account_type ]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'username', 
                        'first_name', 
                        'last_name', 
                        'email', 
                        'mobile_number', 
                        'password',
                        'account_type'
                        ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    if len(password) < 8:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.PASSWORD_STRENGTH_4003,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Please enter a strong password.',
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    existing_users = User.objects.filter(
        Q(username=username) |
        Q(email=email) |
        Q(mobile_number=mobile_number)
    )
    if len(existing_users) > 0:
        existing_fields = []
        for usr in existing_users:
            if usr.username == username:
                existing_fields.append('username')
            if usr.email == email:
                existing_fields.append('email')
            
            if usr.mobile_number == mobile_number:
                existing_fields.append('mobile_number')
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.ACCOUNT_ALREADY_EXISTS_4002,
                'response' : {
                    'message' : 'User already taken from following fields',
                    'error_message' : 'Account already exist',
                    'taken_fields' : existing_fields
                }
            },status=status.HTTP_400_BAD_REQUEST
        )

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
    phone_number = request.data.get('phone_number', None)
    
    if not all([code, code_for]) or (code_for is not None and code_for == 'Mobile' and phone_number is None ) or (code_for is not None and code_for == 'Email' and email is None ) :
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'code',
                        'code_for',
                        'email',
                        'phone_number',
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

    # try:
    #     if code_for == 'Email':
    #         user = User.objects.get(
    #             email=email
    #         )
    #     elif code_for == 'Mobile':
    #         user = User.objects.get(
    #             phone_number=phone_number
    #         )
    # except Exception as err:
    #     return Response(
    #         {
    #             'status' : False,
    #             'status_code' : StatusCodes.USER_NOT_EXIST_4005,
    #             'response' : {
    #                 'message' : 'User not found',
    #                 'error_message' : str(err),
    #                 'messages': [i for i in err],
    #             }
    #         },
    #         status=status.HTTP_400_BAD_REQUEST
    #     )

    try:
        if code_for == 'Email':
            otp = VerificationOTP.objects.get(
                code_for='Email',
                user__email=email,
                code=code
            )
        elif code_for == 'Mobile':
            otp = VerificationOTP.objects.get(
                code_for='Email',
                user__email=email,
                code=code
            )
        else:
            otp = None
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_OTP_4006,
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
                'response' : {
                    'message' : 'OTP not found',
                    'error_message' : str(err),
                    'messages': ['OTP not exist', 'May be something went wrong'],
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    otp.delete()
    
    return Response(
            {
                'status' : True,
                'status_code' : StatusCodes.OTP_VERIFIED_4007,
                'response' : {
                    'message' : 'OTP Verified',
                }
            },
            status=status.HTTP_200_OK
        )