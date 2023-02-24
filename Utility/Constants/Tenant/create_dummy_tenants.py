


from Tenants.models import Tenant

from django.conf import settings
from Authentication.Constants.CreateTenant import add_business_types, add_software_types, add_data_to_tenant_thread
from Utility.Constants.add_data_db import add_business_types, add_countries, add_software_types, add_states, add_cities, add_currencies, add_languages



def CreateDummyTenants():
    total_tenants = Tenant.objects.all()
    total_tenants = len(total_tenants)
    for i in range(5):
        count = total_tenants + i

        name = f'NST-{count}'

        tenant_name = f'NStyle-Tenancy0-{count}'
        
        tenant = Tenant.objects.create(
            name = name,
            domain=f'{tenant_name}.{settings.BACKEND_DOMAIN_NAME}',
            schema_name = tenant_name,
            is_active = False
        )

        if tenant is not None:
            add_business_types(tenant = tenant)
            add_software_types(tenant = tenant)
            add_currencies(tenant=tenant)
            add_languages(tenant=tenant)
            add_countries(tenant=tenant)
            add_states(tenant=tenant)
            add_cities(tenant=tenant)

        tenant.is_ready = True
        tenant.save()
