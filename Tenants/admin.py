from django.contrib import admin

# Register your models here.


from .models import Tenant, Domain, TenantDetail

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'domain',
        'schema_name',
        'username',
        'is_active',
        'is_deleted',
        'is_blocked',
        'created_at',
    ]

    def username(self, obj):
        return str(obj.user.username)

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'domain',
        'is_active',
        'is_deleted',
        'is_blocked',
        'created_at',
    ]


@admin.register(TenantDetail)
class TenantDetailAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'is_tenant_admin',
        'is_tenant_staff',
        'is_tenant_superuser',
    ]