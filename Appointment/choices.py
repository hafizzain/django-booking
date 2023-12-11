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
    BOOKED = 'booked', 'Booked'
    STARTED = 'started', 'Started'
    FINISHED = 'finished', 'Finished'
    DONE = 'done', 'Done'
    CANCELLED = 'cancelled', 'Cancelled'


class AppointmentServiceStatus(models.TextChoices):
    BOOKED = 'booked', 'Booked'
    STARTED = 'started', 'Started'
    FINISHED = 'finished', 'Finished'
    VOID = 'void', 'Void'



