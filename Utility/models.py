from cgitb import text
from uuid import uuid4
from django.db import models
from django.utils.timezone import now

class GlobalPermissionChoices(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)
    
    text = models.CharField(max_length=100, default='')
    slug = models.CharField(max_length=100, default='')

    # def save(self, obj):
    #     self.slug = self.text.upper()
    #     super()
    
    def __str__(self):
        return str(self.id)


class Currency(models.Model):

    name = models.CharField(default='', max_length=200)
    code = models.CharField(default='', max_length=20)
    symbol = models.TextField(default='')
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class Country(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)

    name = models.CharField(default='', max_length=200)
    flag = models.ImageField(upload_to='Utility/country/', null=True, blank=True)
    dial_code = models.CharField(max_length=50, default='')
    code = models.CharField(default='', max_length=20)
    key = models.CharField(default='', max_length=20)
    unique_code = models.CharField(max_length=1000, default='', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(f'{self.id} - {self.name}')


class State(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='country_states')

    name = models.CharField(default='', max_length=200)
    flag = models.ImageField(upload_to='Utility/country/', null=True, blank=True)
    code = models.CharField(default='', max_length=20, null=True, blank=True)
    key = models.CharField(default='', max_length=20, null=True, blank=True)
    unique_code = models.CharField(max_length=1000, default='', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(f'{self.id} - {self.name}')


class City(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='country_cities')
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='state_cities')

    name = models.CharField(default='', max_length=200)
    flag = models.ImageField(upload_to='Utility/country/', null=True, blank=True)
    code = models.CharField(default='', max_length=20, null=True, blank=True)
    key = models.CharField(default='', max_length=20, null=True, blank=True)
    unique_code = models.CharField(max_length=1000, default='', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class Software(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)

    name = models.CharField(default='', max_length=200)
    image = models.ImageField(upload_to='Utility/softwares/', null=True, blank=True)
    image_path = models.CharField(default='', max_length=2000, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class Language(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)

    name = models.CharField(default='', max_length=200)
    code = models.CharField(default='', max_length=200)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)
    
class NstyleFile(models.Model):
    file = models.FileField(upload_to='utility/files/')

    def __str__(self):
        try:
            return str(self.file.path)
        except:
            pass

        return 'Custom file uploaded'
    

class ExceptionRecord(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)

    text = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)


    def __str__(self):
        return str(self.id)
    