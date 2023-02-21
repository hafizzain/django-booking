from django.core.management.base import BaseCommand, CommandError


from Tenants.models import Tenant
from django.conf import settings


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        for i in range(10):
            name = f'NDT-{i}'
            print('Creating Dummy Tenant ... ', end='')
            tenant_name = f'NDT-Dummy-Tenant-{i}'
            Tenant.objects.create(
                name = name,
                domain=f'{tenant_name}.{settings.BACKEND_DOMAIN_NAME}',
                schema_name = tenant_name,
                is_active = False
            )
            print('Created')
        self.stdout.write(self.style.SUCCESS(
            'Tenants Created Successfully!!'
        ))
