from django.contrib import admin
from Appointment.models import Appointment, AppointmentService, AppointmentNotes, AppointmentCheckout, AppointmentLogs, LogDetails


admin.site.register(AppointmentLogs)
admin.site.register(LogDetails)

admin.site.register(AppointmentNotes)
admin.site.register(AppointmentCheckout)
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
        'appointment_time',
        'duration',
        'appointment_end_time',
        'is_active',
        'is_blocked',
    ]