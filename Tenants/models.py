from django.db import models

from django_tenants.models import TenantMixin, DomainMixin
from django.utils.timezone import now
from uuid import uuid4
# from django.contrib.auth.models import User
from Authentication.models import User
# Create your models here.

class Tenant(TenantMixin):
    id = models.CharField(max_length=200, default=uuid4, primary_key=True, unique=True, editable=False)
    user  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant', null=True, blank=True)
    name = models.CharField(max_length=20, default='')
    # schema_name = Already declared in TenantMixin
    domain = models.CharField(default='', max_length=200)

    business_id = models.CharField(default='', max_length=1000, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(auto_now_add=now, null=True, blank=True)

    auto_create_schema = True
    auto_drop_schema = True

    def __str__(self):
        return f'{self.id} - {self.schema_name}'
    
class Domain(DomainMixin):
    id = models.CharField(max_length=200, default=uuid4, primary_key=True, unique=True, editable=False)
    user  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_domain', null=True, blank=True)
    # domain = Already declared in DomainMixin
    # tenant = Already declared in DomainMixin
    schema_name = models.CharField(default='', max_length=200)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(auto_now_add=now , null=True, blank=True)


    def __str__(self):
        return str(self.id)

    
class TenantDetail(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tenant_detail')
    nstyle_user_id = models.CharField(null=True, blank=True, default='', max_length=1000, unique=True)

    is_tenant_admin = models.BooleanField(default=False)
    is_tenant_staff = models.BooleanField(default=False)
    is_tenant_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)

class ClientIdUser(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_user_id', null=True, blank=True)
    client_id = models.CharField(null=True, blank=True, default='', max_length=1000, unique=True)
    
    is_everyone = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)
    
class ClientTenantAppDetail(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant_detail_client', null=True, blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='tenant_client')
    client_id = models.CharField(null=True, blank=True, default='', max_length=1000, unique=True)
    
    is_appointment = models.BooleanField(default=False)
    is_tenant_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)
    
# class EmployeeTenantDetail(models.Model):
#     id = models.UUIDField(default=uuid4, unique=True, primary_key=True, editable=False)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_tenant_detail', null=True, blank=True)
#     tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='tenant_employee')
#     client_id = models.CharField(null=True, blank=True, default='', max_length=1000, unique=True)
    
#     is_appointment = models.BooleanField(default=False)
#     is_tenant_staff = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=now)

#     def __str__(self):
#         return str(self.id)
