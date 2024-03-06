
from django.urls import path, include
from Api import views

urlpatterns = [
    path('v1/country_code', views.country_code),
    path('v1/auth/', include('Authentication.urls.urls_v1')),
    path('v1/utility/', include('Utility.urls')),
    path('v1/business/', include('Business.urls.v1.urls')),
    path('v1/product/', include('Product.urls.v1.urls')),
    path('v1/employee/', include('Employee.urls.v1.urls')),
    path('v1/client/', include('Client.urls.v1.urls')),
    path('v1/appointment/', include('Appointment.urls.v1.urls')),
    path('v1/service/', include('Service.urls.v1.urls')),
    path('v1/sale/', include('Sale.urls.v1.urls')),
    path('v1/Dashboard/', include('Dashboard.urls.v1.urls')),
    path('v1/CRM/', include('CRM.urls.v1.urls')),
    path('v1/targetcontrol/', include('TragetControl.urls.v1.urls')),
    path('v1/customer/', include('Customer.urls.v1.urls')),
    path('v1/promotions/', include('Promotions.urls.v1.urls')),
    path('v1/reports/', include('Reports.urls.v1.urls')),
    path('Emailtemplate/', views.EmailTemplate),
    path('v1/help/', include('Help.urls.v1.urls')),
    path('v1/multilanguage/', include('MultiLanguage.urls.v1.urls')),
    path('v1/insights/', include('Analytics.urls')),
    path('v1/finance/', include('Finance.urls.v1.urls')),
    path('v1/HRM/', include('HRM.urls.v1.urls')),
    path('v1/sale-records/',include('SaleRecords.urls.v1.urls')),
    path('v1/deal/',include('Deal.urls')),
    
    ]