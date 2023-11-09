from django.core.management.base import BaseCommand, CommandError

from django.db.migrations.recorder import MigrationRecorder
from django.db import connection

from Tenants.models import Tenant
from django_tenants.utils import tenant_context

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        tenants = Tenant.objects.all()

        ts = 0

        for t in tenants:
            with tenant_context(t):
                data = MigrationRecorder.Migration.objects.all()
                for m in data:
                    app_name = m.app
                    migration_name = m.name
                    if app_name == 'Promotions' and migration_name in ['0001_initial_squashed_0033_alter_bundlefixed_spend_amount_and_more', '0002_userrestricteddiscount_client']:
                        print(migration_name)
                        ts += 1
                        m.delete()
        
        print(ts)
        self.stdout.write(self.style.SUCCESS(
            'Table deleted Successfully!!'
        ))
