from django.db import models

from django_tenants.models import TenantMixin, DomainMixin
from uuid import uuid4
from django.contrib.auth.models import User
# Create your models here.

class Tenant(TenantMixin):
    id = models.CharField(max_length=200, default=uuid4, primary_key=True, unique=True, editable=False)
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)

    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    auto_create_schema = True
    auto_drop_schema = True

    def __str__(self):
        return self.id
    
class Domain(DomainMixin):
    id = models.CharField(max_length=200, default=uuid4, primary_key=True, unique=True, editable=False)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.id
    