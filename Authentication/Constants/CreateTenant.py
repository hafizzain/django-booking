


from Authentication.models import VerificationOTP
import string
import random
from Tenants.models import Tenant, Domain
from rest_framework.authtoken.models import Token
from .OTP import generate_user_mobile_otp
from .AuthTokenConstants import create_user_token


def create_tenant_Thread(request, user=None ):
    if user is None:
        return
    
    user_tenant = Tenant.objects.create(
        user=user,
        name=user.username,
        domain=user.username,
        schema_name=user.username
    )

    Domain.objects.create(
        user=user,
        schema_name=user.username,
        domain=user.username,
        tenant=user_tenant,
    )
    create_user_token()
    generate_user_mobile_otp(user=user)

    