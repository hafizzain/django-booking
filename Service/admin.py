from django.contrib import admin

from .models import Service , PriceService , ServiceGroup

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'is_active'
    ]
admin.site.register(PriceService)
admin.site.register(ServiceGroup)