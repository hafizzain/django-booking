from itertools import count
from django.db import models

from uuid import uuid4
from Authentication.models import User
from Business.models import Business, BusinessAddress

from django.utils.timezone import now
from Client.models import Client
from Product.models import Product
from Service.models import Service

# Create your models here.

class Segment(models.Model):
    SEGMENT_CHOICE = [
        ('Static', 'Static'),
        ('Dynamic', 'Dynamic'),
        
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='segment')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_segment')
    
    name = models.CharField(max_length=300, default='')
    segemnt_type =  models.CharField(choices=SEGMENT_CHOICE, default='Dynamic' , verbose_name='Segment Type', max_length=30)
    
    client = models.ManyToManyField(Client, related_name='segment_clients')
    description =  models.CharField(max_length=300, null=True, blank=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)