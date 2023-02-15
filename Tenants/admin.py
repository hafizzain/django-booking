from django.contrib import admin

# Register your models here.


from .models import EmployeeTenantDetail, Tenant, Domain, TenantDetail, ClientTenantAppDetail, ClientIdUser

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
        try:
            return str(obj.user.username)
        except:
            return '--------------'

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'domain',
        'domain_schema_name',
        'is_active',
        'is_deleted',
        'is_blocked',
        'created_at',
    ]

    def domain_schema_name(self, obj):
        return str(obj.tenant.schema_name)


@admin.register(TenantDetail)
class TenantDetailAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'is_tenant_admin',
        'is_tenant_staff',
        'is_tenant_superuser',
    ]
    
admin.site.register(ClientTenantAppDetail)
admin.site.register(ClientIdUser)
admin.site.register(EmployeeTenantDetail)