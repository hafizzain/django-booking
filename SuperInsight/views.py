from django.shortcuts import render, redirect, HttpResponse
from MultiLanguage.models import *
from Utility.models import ExceptionRecord
from Tenants.models import Tenant
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist




@login_required(login_url='/super-admin/super-login/')
def DashboardPage(request):
    return render(request, 'SuperAdminPanel/pages/dashboard/dashboard.html')

@login_required(login_url='/super-admin/super-login/')
def ExceptionPage(request):
    exceptions = ExceptionRecord.objects.all().order_by('-created_at')
    context={}
    context['exceptions'] = exceptions
    return render(request, 'SuperAdminPanel/pages/Exception/exception.html', context)

@login_required(login_url='/super-admin/super-login/')
def TenantsListingPage(request):
    tenants = Tenant.objects.all()
    context={}
    context['tenants'] = tenants
    return render(request, 'SuperAdminPanel/pages/Tenants/index.html', context)


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