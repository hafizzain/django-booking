from threading import Thread
from django.core.management.base import BaseCommand, CommandError

from Tenants.models import Tenant
from django_tenants.utils import tenant_context

from Client.models import Client

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        
        tenants = Tenant.objects.filter(
            is_active = True,
            is_ready = True,
            is_deleted = False
        ).exclude(schema_name='public')
        clients_data = []
        for t in tenants:
            with tenant_context(t):
                clients = Client.objects.filter(
                    is_deleted = False,
                    is_active = True,
                    is_blocked = False,
                ).values(
                    'full_name',
                    'client_id',
                    'country',
                )
                clients_data.extend(list(clients))
        
        print(clients_data)


        self.stdout.write(self.style.SUCCESS(
            'Sent!'
        ))
