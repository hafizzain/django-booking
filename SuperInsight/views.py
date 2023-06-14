from django.shortcuts import render
from MultiLanguage.models import *
# Create your views here.


def DashboardPage(request):
    return render(request, 'SuperAdminPanel/pages/dashboard/dashboard.html')

def ExceptionPage(request):
    return render(request, 'SuperAdminPanel/pages/exception/exception.html')

def ExceptionDetailPage(request):
    return render(request, 'SuperAdminPanel/pages/exception/exception-detail.html')

def LanguagePage(request):
    languages = Language.objects.all()
    context = {}
    context['languages'] = languages
    return render(request, 'SuperAdminPanel/pages/language/language.html', context)

def LanguageSectionPage(request):
    lang = request.GET.get('language')
    sections = Section.objects.filter(language__title=lang)
    
    return render(request, 'SuperAdminPanel/pages/language/language-section.html', {'sections':sections, 'language':lang})

def LanguageSectionDetailPage(request):
    lang = request.GET.get('language')
    section = request.GET.get('section')

    labels = Labels.objects.filter(section__title=section, section__language__title = lang)
    context = {}
    context['lang'] = lang
    context['section'] = section
    context['labels'] = labels

    return render(request, 'SuperAdminPanel/pages/language/language-section-detail.html', context)



