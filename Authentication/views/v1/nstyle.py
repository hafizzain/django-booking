from django.shortcuts import render

from django.http import HttpResponse

from django_tenants.utils import tenant_context
# from django.contrib.auth.models import User
from Authentication.models import User
from Tenants.models import Tenant, Domain
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from NStyle.Constants import StatusCodes
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

    if not all([first_name, last_name, email, username, mobile_number, password ]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        pub_tenant = Tenant.objects.get(schema_name='public')
    except Tenant.DoesNotExist :
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.PUBLIC_TENANT_404_5001,
                'response' : {
                    'message' : 'Internal Server Error',
                    'error_message' : 'Public Tenant not found',
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    with tenant_context(pub_tenant):
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
        )

        user_tenant = Tenant.objects.create(
            user=user,
            name=username,
            domain=username,
            schema_name=username
        )

        user_domain = Domain.objects.create(
            
        )


    with tenant_context():
        pass


    return HttpResponse(f'')


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