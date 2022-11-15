from django.contrib import admin

from .models import Service , PriceService

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name'
    ]
admin.site.register(PriceService)