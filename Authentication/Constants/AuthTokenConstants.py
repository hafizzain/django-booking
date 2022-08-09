
from rest_framework.authtoken.models import Token
from django_tenants.utils import tenant_context

def create_user_token(user=None, tenant=None):
    if user is None:
        return
    
    print(user, tenant)
    if tenant is not None:
        with tenant_context(tenant):
            new_token = Token.objects.create(
                user=user
            )
            print(new_token)
    
    else:
        Token.objects.create(
            user=user
        )