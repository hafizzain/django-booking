

from uuid import uuid4
from django.db import models
from django.utils.timezone import now

from Authentication.models import User
from Business.models import Business

class Service(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_services')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_services')

    name = models.CharField(max_length=500, default='')
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)