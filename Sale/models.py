from django.db import models

from uuid import uuid4
from Authentication.models import User
from Business.models import Business

from Utility.models import Country, State, City
from django.utils.timezone import now
from Product.models import Product
from Service.models import Service
import uuid
from Employee.models import Employee
from Business.models import BusinessAddress

# Create your models here.
class Service(models.Model):
    TREATMENT_TYPES = [
        ('Hair_Color' , 'Hair Color'),
        ('test2' , 'test2'),
    ]
    
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_services_or_packages')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_services_or_packages')
    
    name = models.CharField(max_length=300, default='')
    treatment_type = models.CharField(default='test2', choices=TREATMENT_TYPES, max_length=20, null=True, blank=True)
    service = models.ManyToManyField('Service', null=True, blank=True, related_name='package_services')
    
    description = models.CharField(max_length=100, default='')
    employee = models.ManyToManyField(Employee, related_name='service_or_package_employe')
    location = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_or_package_address')
    
    price = models.PositiveIntegerField(default=0, verbose_name='Sale Price')
    duration = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    enable_team_comissions = models.BooleanField(default=True, null=True, blank=True, verbose_name='Enable Team Member Comission')
    enable_vouchers = models.BooleanField(default=False, null=True, blank=True)
    
    is_package = models.BooleanField(default=False, )
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)