
from rest_framework.authtoken.models import Token

def create_user_token(user=None):
    if user is None:
        return
    Token.objects.create(
        user=user
    )