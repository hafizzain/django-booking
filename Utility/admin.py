from django.contrib import admin
from .models import Software

@admin.register(Software)
class SoftwareAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'is_deleted']