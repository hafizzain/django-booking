from django.contrib import admin
from .models import Software, Country, State, City, Language

@admin.register(Software)
class SoftwareAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'is_deleted']

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'is_deleted']

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'is_deleted']

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'is_deleted']

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'is_deleted']