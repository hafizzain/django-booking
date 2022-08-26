from django.contrib import admin

from .models import Employee, EmployeeProfessionalInfo, EmployeePermissionSetting, EmployeeModulePermission, EmployeeMarketingPermission ,StaffGroup , StaffGroupModulePermission 
# Register your models here.

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'full_name',
        'employee_id',
        'email',
        'mobile_number',
        'is_email_verified',
        'is_mobile_verified',
        'dob',
        'gender',
        'joining_date',
        'to_present',
        'ending_date',
        'is_active',
    ]

@admin.register(EmployeeProfessionalInfo)
class EmployeeProfessionalInfoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'designation',
        'income_type',
        'salary',
    ]

@admin.register(EmployeePermissionSetting)
class EmployeePermissionSettingAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'allow_calendar_booking',
        'access_calendar',
        'change_calendar_color',
    ]
@admin.register(EmployeeModulePermission)
class EmployeeModulePermissionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'access_reports',
        'access_sales',
        'access_inventory',
        'access_expenses',
        'access_products',
    ]
@admin.register(EmployeeMarketingPermission)
class EmployeeMarketingPermissionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'access_voucher',
        'access_member_discount',
        'access_invite_friend',
        'access_loyalty_points',
        'access_gift_cards',
    ]
@admin.register(StaffGroup)
class StaffGroupAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'is_deleted',
         'is_active', 
       
    ]
@admin.register(StaffGroupModulePermission)
class StaffGroupModulePermissionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'access_reports', 
        'access_sales', 
        'access_inventory', 
        'access_expenses', 
        'access_products',
        
    ]
