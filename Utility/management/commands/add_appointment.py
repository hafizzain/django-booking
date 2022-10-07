from django.core.management.base import BaseCommand, CommandError
from Appointment.models import Appointment, AppointmentService



from Authentication.models import User
from Authentication.Constants.AddAppointment import Add_appointment


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        #user = User.objects.get(email='developeracount211@gmail.com')
        appointment=  Appointment.objects.all()[0]

        Add_appointment(appointment = appointment)

        self.stdout.write(self.style.SUCCESS(
            'Sent!'
        ))
