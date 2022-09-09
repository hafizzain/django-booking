from django.contrib import admin
from Appointment.models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'business',
        'service', 
        'is_active',
    ]


