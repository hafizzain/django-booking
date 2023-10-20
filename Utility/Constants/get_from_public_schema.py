from django_tenants.utils import tenant_context
from Tenants.models import Tenant
from Utility.models import Country, State

def get_country_from_public(unique_id):
    public_tenant = Tenant.objects.get(schema_name='public')
    with tenant_context(public_tenant):
        return Country.objects.get(unique_id=unique_id)
    
def get_state_from_public(unique_id):
    public_tenant = Tenant.objects.get(schema_name='public')
    with tenant_context(public_tenant):
        return State.objects.get(unique_id=unique_id)