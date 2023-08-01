from django.db import models
from django.utils.timezone import now
from Authentication.models import User
from Utility.models import Language
import uuid


class Profile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    gender = models.CharField(choices=GENDER_CHOICES, default='Male', max_length=10)
    address = models.TextField(default='', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

class UserLanguage(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_languages')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile_languages')

    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)