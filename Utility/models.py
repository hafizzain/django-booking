from uuid import uuid4
from django.db import models
from django.utils.timezone import now


class Country(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)

    name = models.CharField(default='', max_length=200)
    flag = models.ImageField(upload_to='Utility/country/', null=True, blank=True)
    code = models.CharField(default='', max_length=20)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class State(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='country_states')

    name = models.CharField(default='', max_length=200)
    flag = models.ImageField(upload_to='Utility/country/', null=True, blank=True)
    code = models.CharField(default='', max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class City(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='country_cities')
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='state_cities')

    name = models.CharField(default='', max_length=200)
    flag = models.ImageField(upload_to='Utility/country/', null=True, blank=True)
    code = models.CharField(default='', max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class Software(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)

    name = models.CharField(default='', max_length=200)
    image = models.ImageField(upload_to='Utility/softwares/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class Language(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)

    name = models.CharField(default='', max_length=200)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)