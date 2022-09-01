
from django.urls import path, include

urlpatterns = [
    path('v1/auth/', include('Authentication.urls.urls_v1')),
    path('v1/utility/', include('Utility.urls')),
    path('v1/business/', include('Business.urls.v1.urls')),
    path('v1/product/', include('Product.urls.v1.urls')),
    path('v1/employee/', include('Employee.urls.v1.urls')),
    path('v1/client/', include('Client.urls.v1.urls')),


]
