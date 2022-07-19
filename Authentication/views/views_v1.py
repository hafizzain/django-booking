from django.shortcuts import render

from django.http import HttpResponse

from django_tenants.utils import tenant_context
from django.contrib.auth.models import User
from Tenants.models import Tenant, Domain
from django.views.decorators.csrf import csrf_exempt
# Create your views here.



def create_user(request):
    print(User.objects.all().count())

    return HttpResponse(f'{User.objects.all().count()}')


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