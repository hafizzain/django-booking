
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

    ]