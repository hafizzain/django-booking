from django.contrib import admin

# Register your models here.


from .models import EmployeeTenantDetail, Tenant, Domain, TenantDetail, ClientTenantAppDetail, ClientIdUser

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'domain_name',
        'schema_name',
        'username',
        'is_active',
        'is_ready',
        'is_deleted',
        'is_blocked',
        'created_at',
    ]

    list_filter = ['is_ready', 'is_active']
    search_fields = ['id', 'domain', 'schema_name']

    def domain_name(self, obj):
        if obj.domain:
            this_domain = str(obj.domain)
            this_domain = this_domain.split('.')
            return f'{this_domain[0]}'
        else :
            return '--------------' 

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
        'user_username',
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
@admin.register(EmployeeTenantDetail)
class EmployeeTenantDetailAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'tenant',
        'is_tenant_staff',
    ]
    
admin.site.register(ClientTenantAppDetail)
admin.site.register(ClientIdUser)
#admin.site.register(EmployeeTenantDetail)