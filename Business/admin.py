from django.contrib import admin
from .models import BusinessType, Business, BusinessCountry, BusinessCity, BusinessState


@admin.register(BusinessType)
class BusinessTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'is_deleted']


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ['id', 'business_name', 'is_active', 'is_deleted']


@admin.register(BusinessCountry)
class BusinessCountryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'is_deleted']


@admin.register(BusinessState)
class BusinessStateAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'is_deleted']


@admin.register(BusinessCity)
class BusinessCityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'is_deleted']

