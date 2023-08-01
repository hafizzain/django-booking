from threading import Thread
from django.core.management.base import BaseCommand, CommandError
from Appointment.models import Appointment, AppointmentService



from Authentication.models import User
from Appointment.Constants.today_appointment import today_appointment


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        
        try:
            today_appointment()
        except Exception as err:
            print(err)

        self.stdout.write(self.style.SUCCESS(
            'Sent!'
        ))
