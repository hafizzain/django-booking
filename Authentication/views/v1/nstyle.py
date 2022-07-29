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
from rest_framework.decorators import api_view
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
    # last_name = data.get('last_name', None)
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
                    'user' : {
                        # 'first_name' : user.first_name,
                        # 'last_name' : user.last_name,
                        'username' : user.username,
                        # 'full_name' : user.full_name,
                        'email' : user.email,
                        # 'is_active' : user.is_active,
                        # 'mobile_number' : user.mobile_number,
                    },
                }
            },
            status=status.HTTP_201_CREATED
        )
