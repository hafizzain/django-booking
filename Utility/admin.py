from django.contrib import admin
from .models import ExceptionRecord, GlobalPermissionChoices, NstyleFile, Software, Country, State, City, Language, Currency

admin.site.register(NstyleFile)


admin.site.register(GlobalPermissionChoices)

# @admin.register(GlobalPermissionChoices)
# class PermissionAdmin(admin.ModelAdmin):
#     list_display = ['id', 'text', 'slug']


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'is_active', 'is_deleted']

@admin.register(Software)
class SoftwareAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'is_deleted']

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['id', 'key', 'name', 'is_active', 'is_deleted']

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'is_deleted']

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'is_deleted']

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'is_deleted']
@admin.register(ExceptionRecord)
class ExceptionRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'is_resolved']
