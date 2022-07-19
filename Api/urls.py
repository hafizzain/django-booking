
from django.urls import path, include

urlpatterns = [
    path('v1/auth/', include('Authentication.urls.urls_v1')),
]
