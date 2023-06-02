from django.shortcuts import render

# Create your views here.


def DashboardPage(request):
    return render(request, 'SuperAdminPanel/SuperInsights/dashboard.html')

def ExceptionPage(request):
    return render(request, 'SuperAdminPanel/SuperInsights/exception.html')

def ExceptionDetailPage(request):
    return render(request, 'SuperAdminPanel/SuperInsights/exception-detail.html')

def LanguagePage(request):
    return render(request, 'SuperAdminPanel/SuperInsights/language.html')

def LanguageSectionPage(request):
    return render(request, 'SuperAdminPanel/SuperInsights/language-section.html')

def LanguageSectionDetailPage(request):
    return render(request, 'SuperAdminPanel/SuperInsights/language-section-detail.html')
