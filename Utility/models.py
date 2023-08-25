from uuid import uuid4
from django.db import models
from django.utils.timezone import now

#from Employee.models import Employee


class GlobalPermissionChoices(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)
    
    #employee = models.ForeignKey('Employee.Employee', on_delete=models.CASCADE, related_name='employee_global_permission')
        
    text = models.CharField(max_length=1000, default='')
    slug = models.CharField(max_length=1000, default='')
    
    def save(self, *args, **kwargs):
        self.slug = self.text.upper()
        super(GlobalPermissionChoices, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.text)


class Currency(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)

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
    is_flag_uploaded_s3 = models.BooleanField(default=False)

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
    is_flag_uploaded_s3 = models.BooleanField(default=False)

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
    is_flag_uploaded_s3 = models.BooleanField(default=False)

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
    is_image_uploaded_s3 = models.BooleanField(default=False)

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

    status_code = models.TextField(null=True, blank=True)
    text = models.TextField()    
    path = models.TextField(null=True, blank=True)
    method = models.TextField(null=True, blank=True)
    
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def save(self, *args, **kwargs):
        if self.text:
            text = f'{self.text}'.replace('\\n', '<br/>')
            self.text = text
        super(ExceptionRecord, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)

class TurnOverProductRecord(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)

    text = models.TextField()
    i_email = models.CharField(default='', max_length=200)
    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)
    