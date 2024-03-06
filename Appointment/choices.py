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
    CANCELLED = 'Cancelled', 'Cancelled'


class AppointmentServiceStatus(models.TextChoices):
    BOOKED = 'Booked', 'Booked'
    STARTED = 'Started', 'Started'
    FINISHED = 'Finished', 'Finished'
    VOID = 'Void', 'Void'


class PaymentChoices(models.TextChoices):
    PAID = 'Paid', 'Paid'
    UNPAID = 'Unpaid', 'Unpaid'

class ClientType(models.TextChoices):
    INHOUSE = 'IN HOUSE', 'IN HOUSE'
    SALOON = 'SALOON', 'SALOON'


class MissedOpportunityReason(models.TextChoices):
    TECHNICIAN = 'Technician', 'Technician'
    OUT_OF_STOCK = 'Out of stock', 'Out of stock'

class EmployeeUpAndDownSaleChoices(models.TextChoices):
        UPSALE = 'UpSale', 'UpSale'
        DOWNSALE = 'DownSale', 'DownSale'
        