from django.core.management.base import BaseCommand, CommandError


from threading import Thread

from Utility.Constants.Tenant.create_dummy_tenants import CreateDummyTenants

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        try:
            thrd = Thread(target=CreateDummyTenants)
            thrd.start()
        except Exception as err:
            self.stdout.write(self.style.ERROR(
                str(err)
            ))
            
        else:
            self.stdout.write(self.style.SUCCESS(
                'Your Tenants Request Accepted Successfully, You will get Notify when tenants will be created!!'
            ))
