import uuid
from django.db import models

from Authentication.models import User
from Business.models import Business, BusinessAddress
from django.utils.timezone import now
from Service.models import Service
from Client.models import Client
from Employee.models import Employee


class Appointment(models.Model):

    DURATION_CHOICES = [
        ('30 MIN', '30 MIN'), 
        ('45 MIN', '45 MIN'),
        ('1 HOUR', '1 HOUR'),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_appointments', verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_appointments')
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='b_address_appointments')

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='serivce_appointments')
    member = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='member_appointments', null=True, blank=True)
    
    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    duration = models.CharField(choices=DURATION_CHOICES, max_length=100, default='')

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)
    
    
class Checkout(models.Model):
    TYPE_CHOICES = [
        ('IN HOUSE', 'IN HOUSE'),
        ('SALOON', 'SALOON'),
    ]
    
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_checkout', verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_checkout')
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name = 'client_details', verbose_name= 'checkout_name'  )
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='b_address_checkout')
    
    client_type= models.CharField(choices=TYPE_CHOICES, max_length=50, null=True, blank=True, )
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)