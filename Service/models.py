from uuid import uuid4
from django.db import models
from django.utils.timezone import now

from Authentication.models import User
from Business.models import Business, BusinessAddress
from Utility.Constants.Data.Durations import DURATION_CHOICES_DATA

class Service(models.Model):
    DURATION_CHOICES=[
        ('30_Min' , '30 Min'),
        ('60_Min' , '60 Min'),
        ('90_Min' , '90 Min'),
        ('120_Min' , '120 Min'),
        ('150_Min' , '150 Min'),
        ('180_Min' , '180 Min'),
        ('210_Min' , '210 Min'),
    ]
    
    TREATMENT_TYPES = [
        ('Hair_Color' , 'Hair Color'),
        ('test2' , 'test2'),
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_services_or_packages')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_services_or_packages', null=True, blank=True)

    name = models.CharField(max_length=500, default='')

    treatment_type = models.CharField(default='test2', choices=TREATMENT_TYPES, max_length=20, null=True, blank=True)
    parrent_service = models.ManyToManyField('Service', null=True, blank=True, related_name='parent_package_services')
    description = models.CharField(max_length=100, default='')
    employee = models.ManyToManyField('Employee.Employee', related_name='employee_services_or_packages')
    location = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='address_services_or_packages')
    #duration = models.PositiveIntegerField(default=0, null=True, blank=True)
    duration = models.CharField(max_length=50, null=True, blank=True, choices=DURATION_CHOICES )
    enable_team_comissions = models.BooleanField(default=True, null=True, blank=True, verbose_name='Enable Team Member Comission')
    enable_vouchers = models.BooleanField(default=False, null=True, blank=True)
    
    price = models.PositiveIntegerField(default=0)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)
    
    is_package = models.BooleanField(default=False, )


    def __str__(self):
        return str(self.id)