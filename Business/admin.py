from django.contrib import admin
from .models import BusinessType, Business, BusinessSocial, BusinessAddress, BusinessOpeningHour, BusinessTheme


@admin.register(BusinessType)
class BusinessTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'is_deleted']


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ['id', 'business_name', 'is_active', 'is_deleted']

@admin.register(BusinessSocial)
class BusinessSocialAdmin(admin.ModelAdmin):
    list_display = ['id', 'website', 'facebook', 'instagram']

@admin.register(BusinessAddress)
class BusinessAddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'address_name', 'address', 'postal_code']

@admin.register(BusinessOpeningHour)
class BusinessOpeningHourAdmin(admin.ModelAdmin):
    list_display = ['id', 'day', 'start_time', 'close_time', 'is_closed', 'is_deleted']


@admin.register(BusinessTheme)
class BusinessThemeAdmin(admin.ModelAdmin):
    list_display = ['id', 'primary_color' , 'secondary_color' , 'menu_option' ,'calendar_option' , 'is_active', 'is_deleted']

