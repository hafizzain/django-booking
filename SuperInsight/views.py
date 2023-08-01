from django.shortcuts import render, redirect, HttpResponse
from MultiLanguage.models import *
from Utility.models import ExceptionRecord
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout



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
    return render(request, 'SuperAdminPanel/pages/dashboard/login.html')