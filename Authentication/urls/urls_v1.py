
from django.urls import path, include

from ..views.v1 import nstyle, tenant

urlpatterns = [
    path('create_tenant_business_user/', nstyle.create_tenant_business_user ),
    path('nstyle_login/', nstyle.login ),
    path('nstyle_login_flag/', nstyle.login_flagged ),
    path('nstyle_change_password/', nstyle.change_password ),
    
    # OTP 
    path('verify_otp/', nstyle.verify_otp ),
    path('get_tenant_detail/', nstyle.get_tenant_detail),
    path('send_verification_otp/', nstyle.send_verification_otp ),

    path('all_users/', nstyle.all_users),
    path('make_me_login/', nstyle.make_me_login),

    # Tenant Special 

    path('tenant_login/', tenant.login ),
    path('get_user/', tenant.get_user ),
]