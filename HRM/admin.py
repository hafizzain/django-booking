from django.contrib import admin
from HRM.models import *
# Register your models here.

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'note', 'start_date', 'end_date', 'created_at', 'updated_at']
    list_filter = ['name', 'start_date', 'end_date']