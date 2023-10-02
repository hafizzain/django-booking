from django.db import models
from django.conf import settings
from fcm_django.models import AbstractFCMDevice


class CustomFCMDevice(AbstractFCMDevice):
    """
    A custom model inherit from AbstractFCMDevice because
    by default its user is pointing to setttings.USER_MODEL
    butt we have settings.AUTH_USER_MODEL
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE)
