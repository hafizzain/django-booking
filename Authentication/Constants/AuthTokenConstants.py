
from rest_framework.authtoken.models import Token
from django_tenants.utils import tenant_context

def create_user_token(user=None):
    if user is None:
        return None

    return Token.objects.create(
        user=user
    )