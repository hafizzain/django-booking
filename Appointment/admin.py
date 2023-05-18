from django.contrib import admin
from Appointment.models import Appointment, AppointmentService, AppointmentNotes, AppointmentCheckout, AppointmentLogs, LogDetails


@admin.register(AppointmentLogs)
class AppointmentLogsAdmin(admin.ModelAdmin):
    list_display = ['id', 'location', 'appointment', 'is_active', 'is_deleted']

admin.site.register(LogDetails)

admin.site.register(AppointmentNotes)
@admin.register(AppointmentCheckout)
class AppointmentCheckoutAdmin(admin.ModelAdmin):
    ordering = ['-created_at']
    list_display = ['id', 'is_promotion', 'created_at', 'total_price']



@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    ordering = ['-created_at']

    list_display = [
        'id',
        'business_name',
        'is_active',
        'is_promotion',
        'created_at',
        'discount_price',
        'discount_percentage'
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
        'discount_price',
        'discount_percentage'
    ]