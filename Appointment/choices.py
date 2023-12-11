from django.db import models



BOOKED_CHOICES = [
        ('Appointment_Booked',  'Appointment Booked'),
        ('Arrived', 'Arrived'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
        ('Paid', 'Paid'),
        ('Cancel', 'Cancel'),
    ]

class AppointmentStatus(models.TextChoices):
    BOOKED = 'Booked', 'Booked'
    STARTED = 'Started', 'Started'
    FINISHED = 'Finished', 'Finished'
    DONE = 'Done', 'Done'
    CANCELLED = 'cancelled', 'Cancelled'


class AppointmentServiceStatus(models.TextChoices):
    BOOKED = 'Booked', 'Booked'
    STARTED = 'Started', 'Started'
    FINISHED = 'Finished', 'Finished'
    VOID = 'Void', 'Void'



