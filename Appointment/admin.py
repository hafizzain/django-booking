from django.contrib import admin
from Appointment.models import Appointment, AppointmentService

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'business_name',
        'is_active',
    ]
@admin.register(AppointmentService)
class AppointmentServiceAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'member_name',
        'appointment_date',
        'is_active',
        
    ]