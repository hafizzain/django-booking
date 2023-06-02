from django.shortcuts import render

# Create your views here.


def DashboardPage(request):
    return render(request, 'SuperAdminPanel/pages/dashboard/dashboard.html')

def ExceptionPage(request):
    return render(request, 'SuperAdminPanel/pages/exception/exception.html')

def ExceptionDetailPage(request):
    return render(request, 'SuperAdminPanel/pages/exception/exception-detail.html')

def LanguagePage(request):
    return render(request, 'SuperAdminPanel/pages/language/language.html')

def LanguageSectionPage(request):
    return render(request, 'SuperAdminPanel/pages/language/language-section.html')

def LanguageSectionDetailPage(request):
    return render(request, 'SuperAdminPanel/pages/language/language-section-detail.html')
