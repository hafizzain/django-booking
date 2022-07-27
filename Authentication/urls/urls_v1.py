
from django.urls import path, include

from ..views.v1 import nstyle

urlpatterns = [
    path('create_tenant_business_user/', nstyle.create_tenant_business_user )
]
