from django.core.management.base import BaseCommand, CommandError
import csv
from Utility.Constants.add_data_db import add_currencies

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        add_currencies(tenant=None)
        self.stdout.write(self.style.SUCCESS(
            'Currencies Added Successfully !!'
        ))
