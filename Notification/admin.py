from django.contrib import admin

from .models import CustomFCMDevice


@admin.register(CustomFCMDevice)
class CustomFCMDevices(admin.ModelAdmin):
    list_display = ['id', 'user', 'device_id', 'registration_id']