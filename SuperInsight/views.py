from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect
from MultiLanguage.models import *
from Utility.models import ExceptionRecord
from Tenants.models import Tenant
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from threading import Thread
from Utility.Constants.Tenant.create_dummy_tenants import CreateDummyTenants
from django_tenants.utils import tenant_context
from Client.models import Client
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from Authentication.models import User

status_codes = [
    100, 101, 200, 201, 202, 203, 204, 205, 206, 207, 208, 226, 300, 301, 302, 303, 304, 305, 306, 307, 308, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 422, 423, 424, 426, 428, 429, 431, 451, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511,
]

@login_required(login_url='/super-admin/super-login/')
def DashboardPage(request):
    tenants = Tenant.objects.filter(
        is_active = True,
        is_ready = True,
        is_blocked = False,
        is_deleted = False,
    )
    clients = 0

    for tenant in tenants:
        with tenant_context(tenant):
            tenant_clients = Client.objects.filter(
                is_deleted = False,
                is_active = True,
                is_blocked = False,
            )
            clients += tenant_clients.count()
    context = {
        'total_clients' : clients,
        'get_country_users_url' : reverse('GetCountryClients')
    }
    return render(request, 'SuperAdminPanel/pages/dashboard/dashboard.html', context)


@api_view(['GET',])
@permission_classes([AllowAny])
def GetCountryClients(request):
    tenants = Tenant.objects.filter(
        is_active = True,
        is_ready = True,
        is_blocked = False,
        is_deleted = False,
    )
    clients = 0
    countries = []
    for tenant in tenants:
        with tenant_context(tenant):
            client_countries = Client.objects.filter(
                is_deleted = False,
                is_active = True,
                is_blocked = False,
            ).values_list('country__name', flat=True)
            countries.extend(list(client_countries))
    
    country_labels = set(countries)
    country_values = []

    for c_name in country_labels:
        country_values.append(countries.count(c_name))
        

    return Response({
        'country_labels' : country_labels,
        'country_values' : country_values,
    })

@login_required(login_url='/super-admin/super-login/')
def ExceptionPage(request):
    status_code = request.GET.get('status_code', None)
    business_name = request.GET.get('business_name', None)
    request_method = request.GET.get('request_method', None)
    selected_date = request.GET.get('date', None)


    query = {}
    if status_code:
        query['status_code__icontains'] = status_code
    
    if business_name:
        query['tenant__domain__icontains'] = business_name
    
    if request_method:
        query['method__icontains'] = request_method
    
    if selected_date:
        query['created_at__date'] = selected_date

    exceptions = ExceptionRecord.objects.filter(**query).order_by('-created_at')
    context={}
    context['exceptions'] = exceptions
    context['status_codes'] = status_codes
    return render(request, 'SuperAdminPanel/pages/Exception/exception.html', context)

@login_required(login_url='/super-admin/super-login/')
def TenantsListingPage(request):
    user = request.GET.get('user', None)
    domain = request.GET.get('domain', None)
    status = request.GET.get('status', None)
    query = {}
    if user:
        query['user__username__icontains'] = user
    
    if domain:
        query['domain__icontains'] = domain
    
    if status:
        ST_TYPES = {
            'ALL' : {},
            'active' : {
                'is_active' : True,
            },
            'inactive' : {
                'is_active' : False
            },
        }
        s_type = ST_TYPES.get(status, '')
        if s_type:
            query.update(s_type)


    tenants = Tenant.objects.filter(**query)
    context={}
    context['tenants'] = tenants
    context['free_tenants'] = Tenant.objects.filter(is_ready = True, is_active = False)
    context['creating_tenants'] = Tenant.objects.filter(is_ready = False, is_active = False)
    return render(request, 'SuperAdminPanel/pages/Tenants/index.html', context)

@login_required(login_url='/super-admin/super-login/')
def CreateFreeTenants(request):
    try:
        thrd = Thread(target=CreateDummyTenants)
        thrd.start()
    except Exception as err:
        messages.error(request, str(err))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/super-admin/tenants/'))
    else:
        messages.success(request, 'You will be notify when tenants are successfully created')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/super-admin/tenants/'))


@login_required(login_url='/super-admin/super-login/')
def ExceptionDetailPage(request):
    if request.method == 'GET':
        id = request.GET.get('id')
    
    exception = ExceptionRecord.objects.get(id = id)
    
    context={}
    context['exception'] = exception
    return render(request, 'SuperAdminPanel/pages/Exception/exception-detail.html', context)


@login_required(login_url='/super-admin/super-login/')
def LanguagePage(request):
    languages = Language.objects.all()
    context = {}
    context['languages'] = languages
    return render(request, 'SuperAdminPanel/pages/language/language.html', context)


@login_required(login_url='/super-admin/super-login/')
def LanguageSectionPage(request):
    lang = request.GET.get('language')
    sections = Section.objects.filter(language__title=lang)
    
    return render(request, 'SuperAdminPanel/pages/language/language-section.html', {'sections':sections, 'language':lang})


@login_required(login_url='/super-admin/super-login/')
def LanguageSectionDetailPage(request):
    lang = request.GET.get('language')
    section = request.GET.get('section')

    labels = Labels.objects.filter(section__title=section, section__language__title = lang)
    context = {}
    context['lang'] = lang
    context['section'] = section
    context['labels'] = labels

    return render(request, 'SuperAdminPanel/pages/language/language-section-detail.html', context)



def Logout(request):
    logout(request)
    return redirect('/super-admin/super-login/')

def SuperLogin(request):
    if request.method == "POST":
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)

        try:
            user = User.objects.get(
                email=email,
                is_deleted=False,
                is_admin=True,
            )
        except ObjectDoesNotExist:
            messages.error(request, 'Invalid credentials')
            return render(request, 'SuperAdminPanel/pages/dashboard/login.html')
        
        username=user.username
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, 'Invalid credentials')
            return render(request, 'SuperAdminPanel/pages/dashboard/login.html')

        login(request, user)
        return redirect('/super-admin/admin')

    return render(request, 'SuperAdminPanel/pages/dashboard/login.html')