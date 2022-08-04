
from django.urls import path, include

from ..views.v1 import nstyle

urlpatterns = [
    path('create_tenant_business_user/', nstyle.create_tenant_business_user ),
    path('nstyle_login/', nstyle.login ),
    path('nstyle_change_password/', nstyle.change_password ),
    
    # OTP 
    path('verify_otp/', nstyle.verify_otp ),
    path('resend_otp/', nstyle.resend_otp ),
]
