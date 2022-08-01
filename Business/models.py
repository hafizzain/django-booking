from django.db import models
from django.utils.timezone import now
from Authentication.models import User
from Profile.models import Profile
from Utility.models import Country, State, City, Software


import uuid


class BusinessType(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    name = models.CharField(default='', max_length=100)
    image = models.ImageField(upload_to='business/business_types/images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class Business(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_business')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile_business')

    business_name = models.CharField(default='', max_length=300)

    logo = models.ImageField(upload_to='business/logo/')
    banner = models.ImageField(upload_to='business/banner/')


class BusinessCountry(Country):
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='business_country')

class BusinessState(State):
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='business_state')

class BusinessCity(City):
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='business_city')