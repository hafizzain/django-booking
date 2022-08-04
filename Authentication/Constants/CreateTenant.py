


from Authentication.models import AccountType
import string
import random
from Tenants.models import Tenant, Domain
from rest_framework.authtoken.models import Token
from .AuthTokenConstants import create_user_token


def create_tenant(request=None, user=None):
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
 

    