from django.contrib import admin
from Appointment.models import Appointment, AppointmentGroup, AppointmentService, AppointmentNotes, AppointmentCheckout, AppointmentLogs, LogDetails, EmployeeUpAndDownSale
from Service.models import ServiceGroup


@admin.register(AppointmentLogs)
class AppointmentLogsAdmin(admin.ModelAdmin):
    list_display = ['id', 'location', 'appointment', 'is_active', 'is_deleted']

admin.site.register(LogDetails)

admin.site.register(AppointmentNotes)
@admin.register(AppointmentCheckout)
class AppointmentCheckoutAdmin(admin.ModelAdmin):
    ordering = ['-created_at']
    list_display = ['id', 'business_address', 'is_promotion', 'created_at', 'total_price']
    # search_fields = ('id')

@admin.register(EmployeeUpAndDownSale)
class EmployeeUpAndDownSaleAdmin(admin.ModelAdmin):
    list_display = ['id','old_price','new_price','price_difference','status']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    ordering = ['-created_at']
    list_filter = [
        'status'
    ]

    list_display = [
        'id',
        'business_name',
        'is_active',
        'is_promotion',
        'created_at',
        'discount_price',
        'discount_percentage'
    ]
    # search_fields = ('id')
@admin.register(AppointmentService)
class AppointmentServiceAdmin(admin.ModelAdmin):
    ordering = ['-created_at']
    list_filter = [
        'business_address__address_name',
        'created_at',
        'is_blocked',
        'status'
    ]
    list_display = [
        'id',
        'member_name',
        'service_group_name',
        'appointment_status',
        'appointment_date',
        'appointment',
        'appointment_time',
        'end_time',
        'total_price',
        'price',
        'duration',
        'appointment_end_time',
        'is_active',
        'is_blocked',
        'discount_price',
        'discount_percentage',
    ]

    def service_group_name(self, appointment):
        groups = ServiceGroup.objects.filter(
            services = appointment.service,
            is_deleted = False
        )
        if len(groups) > 0:
            return groups[0].name


@admin.register(AppointmentGroup)
class AppointmentGroupAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'total_appointments'
    ]

    def total_appointments(self, obj):
        return obj.appointment.all().count()