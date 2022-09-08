import uuid
from django.db import models

from Authentication.models import User
from Business.models import Business, BusinessAddress
from django.utils.timezone import now
from Service.models import Service
from Employee.models import Employee


class Appointment(models.Model):

    DURATION_CHOICES = [
        (''),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_appointments', verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_appointments')
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='')

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='serivce_appointments')
    member = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='member_appointments')
    
    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    duration = models.CharField()

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)