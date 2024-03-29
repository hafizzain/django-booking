from threading import Thread
from django.core.management.base import BaseCommand, CommandError

from Tenants.models import Tenant
from django_tenants.utils import tenant_context
from Reports.models import SaleReport
from Appointment.models import AppointmentService

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        
        tenants = Tenant.objects.filter(
            is_active = True,
            is_ready = True,
            is_deleted = False
        ).exclude(schema_name='public')
        apps_data = {}
        for t in tenants:
            with tenant_context(t):
                apps = AppointmentService.objects.filter(
                    appointment_status__in = ['Appointment_Booked', 'Arrived', 'In Progress', 'Done', 'Paid'],
                    is_active = True,
                    is_deleted = False,
                    service__isnull = False
                )
                for app in apps:

                    service = apps_data.get(app.service.name)
                    if not service:
                        service = {}
                        service['id'] = str(app.service.id)
                        service['total_count'] = 1
                    else:
                        service['total_count'] = service['total_count'] + 1

                    apps_data[app.service.name] = service
        
        for key, val in apps_data.items():
            repo_service, created = SaleReport.objects.get_or_create(
                sale_type = 'Service',
                name = key,
            )
            if created:
                repo_service.instance_id = val['id']
            
            repo_service.total_count = val['total_count']
            repo_service.save()

        print('updated')
        self.stdout.write(self.style.SUCCESS(
            'Sent!'
        ))
