from django.shortcuts import render

# Create your views here.


def DashboardPage(request):
    return render(request, 'SuperAdminPanel/SuperInsights/home_page.html')