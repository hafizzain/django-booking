from threading import Thread
from django.core.management.base import BaseCommand, CommandError
from Appointment.models import Appointment, AppointmentService



from Authentication.models import User
from Appointment.Constants.AddAppointment import Add_appointment


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        #user = User.objects.get(email='developeracount211@gmail.com')
        appointment=  Appointment.objects.all()[0]
        
        try:
            thrd = Thread(target=Add_appointment, args=[appointment])
            thrd.start()
        except Exception as err:
            pass
        
        
        #Add_appointment(appointment = appointment)

        self.stdout.write(self.style.SUCCESS(
            'Sent!'
        ))
