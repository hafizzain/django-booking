from django.db import models

from django_tenants.models import TenantMixin, DomainMixin

from django.contrib.auth.models import User
# Create your models here.

class Tenant(TenantMixin):
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    domain_name = models.CharField(max_length=20)


    auto_create_schema = True
    auto_drop_schema = True


    def __str__(self):
        return self.domain_name
    
class Domain(DomainMixin):
    pass