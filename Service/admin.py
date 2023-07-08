from django.contrib import admin

from .models import Service , PriceService , ServiceGroup

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'is_active',
        'is_default'
    ]
@admin.register(PriceService)
class PriceServiceAdmin(admin.ModelAdmin):
    list_filter = [
        'service__name',
        'currency__code'
    ]

    list_display = [
        'id',
        'service_name',
        'currency',
        'duration',
        'duration_added',
        'price',
    ]

    def duration_added(self, instance):
        return instance.duration

    def service_name(self, instance):
        return instance.service.name


admin.site.register(ServiceGroup)