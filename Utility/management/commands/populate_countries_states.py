from django.core.management.base import BaseCommand
from django_tenants.utils import tenant_context

from Tenants.models import Tenant
from Utility.Constants.add_data_db import add_countries, add_states


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        try:
            tenant = Tenant.objects.get(schema_name='public')
            with tenant_context(tenant):
                add_countries()
                add_states()
        except Exception as err:
            self.stdout.write(self.style.ERROR(
                str(err)
            ))
