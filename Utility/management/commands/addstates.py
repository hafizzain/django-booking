from django.core.management.base import BaseCommand, CommandError

from Utility.Constants.add_data_db import add_states

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        add_states()
        self.stdout.write(self.style.SUCCESS(
            'States added Successfully!!'
        ))
