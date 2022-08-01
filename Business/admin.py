from django.contrib import admin
from .models import BusinessType


@admin.register(BusinessType)
class BusinessTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'is_deleted']