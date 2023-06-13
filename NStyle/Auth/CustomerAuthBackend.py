# from django.conf import settings
# from django.contrib.auth.models import User
# from django.db.models import Q
from Utility.models import ExceptionRecord

# class CustomerAuthBackend(object):    
#     def authenticate(self, username=None, password=None, **kwargs):
#         try:
#             user = User.objects.get(
#                 Q(is_active = True) |
#                 Q(is_active = False),
#                 username = username
#             )
#             if user.check_password(password):
#                 return user
#         except Exception as err:
#             ExceptionRecord.objects.create(text = f'EMAIL AUTTH : {str(err)}')
#             # Run the default password hasher once to reduce the timing
#             # difference between an existing and a non-existing user (#20760).
#             # User().set_password(password)
#             return None

from django.contrib.auth import backends, get_user_model
from django.db.models import Q

class CustomerAuthBackend(backends.ModelBackend):

    def authenticate(self, username=None, password=None, **kwargs):
        usermodel = get_user_model()
        try:
            user = usermodel.objects.get(
                Q(is_active = True) |
                Q(is_active = False),
                username = username
            )

            if user.check_password(password):
                return user
        except Exception as err:
            ExceptionRecord.objects.create(text = f'EMAIL AUTTH : {str(err)}')
            return None