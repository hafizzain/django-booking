from django.shortcuts import render, redirect, HttpResponse
from MultiLanguage.models import *
from Utility.models import ExceptionRecord
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages



@login_required(login_url='/admin')
def DashboardPage(request):
    return render(request, 'SuperAdminPanel/pages/dashboard/dashboard.html')

@login_required(login_url='/admin')
def ExceptionPage(request):
    exceptions = ExceptionRecord.objects.all().order_by('-created_at')
    context={}
    context['exceptions'] = exceptions
    return render(request, 'SuperAdminPanel/pages/Exception/exception.html', context)


@login_required(login_url='/admin')
def ExceptionDetailPage(request):
    if request.method == 'GET':
        id = request.GET.get('id')
    
    exception = ExceptionRecord.objects.get(id = id)
    
    context={}
    context['exception'] = exception
    return render(request, 'SuperAdminPanel/pages/Exception/exception-detail.html', context)


@login_required(login_url='/admin')
def LanguagePage(request):
    languages = Language.objects.all()
    context = {}
    context['languages'] = languages
    return render(request, 'SuperAdminPanel/pages/language/language.html', context)


@login_required(login_url='/admin')
def LanguageSectionPage(request):
    lang = request.GET.get('language')
    sections = Section.objects.filter(language__title=lang)
    
    return render(request, 'SuperAdminPanel/pages/language/language-section.html', {'sections':sections, 'language':lang})


@login_required(login_url='/admin')
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
    return redirect('/admin')

def SuperLogin(request):
    if request.method == "POST":
        username = request.data.get('username', None)
        password = request.data.get('password', None)
    else:
        pass

    try:
        user = User.objects.get(
                username=username,
                is_deleted=False,
                is_admin=True,
                user_account_type__account_type = 'Everyone'
            )
    except:
        messages.error(request, 'Invalid Username')
    
    user = authenticate(request, username=username, password=password)

    if user:    
        login(request, user)
        messages.success(request, 'Logged in Successfully')
        return redirect('super-admin/admin')
    else:
        messages.error(request, 'Invalid Credentials')
    return render(request, 'SuperAdminPanel/pages/dashboard/login.html')