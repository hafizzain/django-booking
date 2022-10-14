from django.contrib import admin

from .models import(CommissionSchemeSetting, Employee, EmployeeProfessionalInfo, EmployeePermissionSetting, EmployeeModulePermission, 
                    EmployeeMarketingPermission ,StaffGroup , 
                    StaffGroupModulePermission , Attendance , 
                    Payroll, Asset, AssetDocument, EmployeeSelectedService )
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
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'in_time',
        'out_time', 
        'is_active',
    ]
    
@admin.register(Payroll)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'name',
        'created_at', 
        'Total_hours',
    ]
    
@admin.register(CommissionSchemeSetting)
class CommissionSchemeSettingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'sale_price_before_discount',
        'sale_price_including_tax',
        'service_price_before_membership_discount',
        'created_at', 
    ]
admin.site.register(Asset)
admin.site.register(AssetDocument)
admin.site.register(EmployeeSelectedService)