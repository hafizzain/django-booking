from django.shortcuts import render

from django.http import HttpResponse

from django_tenants.utils import tenant_context
from django.db.models import Q
# from django.contrib.auth.models import User
from Authentication.models import User, VerificationOTP
from Tenants.models import Tenant, Domain
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from NStyle.Constants import StatusCodes

import random
import string
# Create your views here.


@api_view(['POST'])
def create_tenant_business_user(request):
    data = request.data

    first_name = data.get('first_name', None)
    last_name = data.get('last_name', None)
    email = data.get('email', None)
    username = data.get('username', None)
    mobile_number = data.get('mobile_number', None)
    password = data.get('password', None)

    if not all([first_name, email, username, mobile_number, password ]):
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
                        'password'
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
    # try:
    #     pub_tenant = Tenant.objects.get(schema_name='public')
    # except Tenant.DoesNotExist :
    #     return Response(
    #         {
    #             'status' : False,
    #             'status_code' : StatusCodes.PUBLIC_TENANT_404_5001,
    #             'response' : {
    #                 'message' : 'Internal Server Error',
    #                 'error_message' : 'Public Tenant not found',
    #             }
    #         },
    #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #     )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    user.first_name=first_name
    user.last_name=last_name
    user.full_name=f'{first_name} {last_name}'
    user.mobile_number=mobile_number
    user.save()

    user_tenant = Tenant.objects.create(
        user=user,
        name=username,
        domain=username,
        schema_name=username
    )

    user_domain = Domain.objects.create(
        user=user,
        schema_name=username,
        domain=username,
        tenant=user_tenant,
    )

    random_digits_for_code = ''.join(random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
    otp = VerificationOTP(
        user=user,
        code=random_digits_for_code,
        code_for='Mobile'
    )
    otp.save()
    
    user_token = Token.objects.create(
        user=user
    )

    # with tenant_context():
    #     pass
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Account created successfully',
                    'user' : {
                        'first_name' : user.first_name,
                        'last_name' : user.last_name,
                        'username' : user.username,
                        'full_name' : user.full_name,
                        'email' : user.email,
                        'is_active' : user.is_active,
                        'mobile_number' : user.mobile_number,
                    },
                    'access_token' : str(user_token.key)
                }
            },
            status=status.HTTP_201_CREATED
        )


# @csrf_exempt
# def create_user(request):
#     if request.method == 'POST':
#         data = request.POST
#         pblc_tnt = Tenant.objects.get(schema_name = 'public')


#         with tenant_context(pblc_tnt):
#             user = User.objects.create(
#                 username=data['username'],
#                 password=data['password'],
#             )
#             usr_tnt = Tenant.objects.create(
#                 schema_name=data['username'],
#                 domain_name = data['username'],
#                 user = user
#             )
#             usr_domain = Domain.objects.create(
#                 tenant = usr_tnt,
#                 domain = f'{data["username"]}.localhost'
#             )

#         with tenant_context(usr_tnt):
#             spr_user = User.objects.create_superuser(
#                 username = data['username'],
#                 password = data['password'],
#                 is_active = True,
#                 is_staff = True,
#                 is_superuser = True
#             )
#             print('SUPERUSER : ' , spr_user)
#             print('SUPERUSER : ' , spr_user.is_superuser)

#         return HttpResponse(f'http://{data["username"]}.localhost:8000/admin')
#     else:

#         return HttpResponse('working')