from threading import Thread
from django.core.management.base import BaseCommand, CommandError

from Tenants.models import Tenant
from django_tenants.utils import tenant_context

from Appointment.models import AppointmentService

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        
        tenants = Tenant.objects.filter(
            is_active = True,
            is_ready = True,
            is_deleted = False
        ).exclude(schema_name='public')
        apps_data = []
        for t in tenants:
            with tenant_context(t):
                apps = AppointmentService.objects.filter(
                    appointment_status__in = ['Appointment_Booked', 'Arrived', 'In Progress', 'Done', 'Paid'],
                    is_active = True,
                    is_deleted = False,
                )
                for app in apps:
                    apps_data.append({
                        'id' : app.service.id,
                        'name' : app.service.name,
                        'sale_type' : 'Service'
                    })
        
        print(apps_data)
        
        self.stdout.write(self.style.SUCCESS(
            'Sent!'
        ))
