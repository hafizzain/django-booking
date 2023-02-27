from django.contrib import admin
from .models import (BusinessType, Business, BusinessSocial, BusinessAddress, BusinessOpeningHour, BusinessTheme, StaffNotificationSetting, ClientNotificationSetting, AdminNotificationSetting, StockNotificationSetting, 
                     BookingSetting, BusinessPaymentMethod, 
                     BusinessTax , BusinessVendor, BusinessAddressMedia
                    
                     )

admin.site.register(BusinessVendor)
admin.site.register(BusinessAddressMedia)

@admin.register(BusinessPaymentMethod)
class BusinessPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['id', 'method_type', 'is_active']

@admin.register(BusinessTax)
class BusinessTaxAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'tax_rate', 'tax_type', 'is_active']


@admin.register(BusinessType)
class BusinessTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'is_active', 'is_deleted']


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
    list_display = ['id', 'theme_name', 'primary_color' , 'secondary_color' , 'menu_option' ,'calendar_option' , 'is_active', 'is_deleted']


@admin.register(StaffNotificationSetting)
class StaffNotificationSettingAdmin(admin.ModelAdmin):
    def business_name(self, obj):
        try:
            return obj.business.business_name
        except:
            return 'N/A'
    list_display = ['id', 'business_name', 'is_active', 'created_at' ]


@admin.register(AdminNotificationSetting)
class AdminNotificationSettingAdmin(admin.ModelAdmin):
    def business_name(self, obj):
        try:
            return obj.business.business_name
        except:
            return 'N/A'
    list_display = ['id', 'business_name', 'is_active', 'created_at' ]

@admin.register(ClientNotificationSetting)
class ClientNotificationSettingAdmin(admin.ModelAdmin):
    def business_name(self, obj):
        try:
            return obj.business.business_name
        except:
            return 'N/A'
    list_display = ['id', 'business_name', 'is_active', 'created_at' ]
@admin.register(StockNotificationSetting)
class StockNotificationSettingAdmin(admin.ModelAdmin):
    def business_name(self, obj):
        try:
            return obj.business.business_name
        except:
            return 'N/A'
    list_display = ['id', 'business_name', 'is_active', 'created_at' ]

@admin.register(BookingSetting)
class BookingSettingAdmin(admin.ModelAdmin):
    def business_name(self, obj):
        try:
            return obj.business.business_name
        except:
            return 'N/A'
    list_display = ['id', 'business_name', 'is_active', 'created_at' ]

