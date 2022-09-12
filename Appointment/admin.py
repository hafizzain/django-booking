from django.contrib import admin
from Appointment.models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'business_name',
        'is_active',
    ]
