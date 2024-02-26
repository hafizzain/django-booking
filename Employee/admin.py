from django.contrib import admin

from .models import(CommissionSchemeSetting, EmployeDailySchedule, Employee, EmployeeProfessionalInfo, EmployeePermissionSetting, EmployeeModulePermission, 
                    EmployeeMarketingPermission ,StaffGroup , CategoryCommission,
                    StaffGroupModulePermission , Attendance , 
                    Payroll, Asset, AssetDocument, EmployeeSelectedService, Vacation, EmployeeCommission, GiftCards, GiftDetail )
# Register your models here.

@admin.register(Vacation)
class VacationAdmin(admin.ModelAdmin):
    list_display = ['id', 'from_date', 'to_date']


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
        'is_deleted',
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

@admin.register(EmployeeCommission)
class EmployeeCommissionAdmin(admin.ModelAdmin):

    list_display = [
        'id', 
        'commission_category',
        'item_name',
        'commission_type',
        'commission_rate',
        'symbol',
        'sale_value',
        'quantity',
        'total_sale_value',
        'single_item_commission',
        'full_commission',
        'created_at',
    ]
    ordering = ['-created_at']

    def total_sale_value(self, instance):
        return instance.sale_value * instance.quantity
    
    def single_item_commission(self, instance):
        return instance.single_item_commission

    single_item_commission.short_description = 'Commission/Item'


@admin.register(EmployeDailySchedule)
class EmployeDailyScheduleAdmin(admin.ModelAdmin):
    ordering = ['-date']
    list_filter = ['employee__full_name']
    list_display = [
        'id',
        'employee_name',
        'today_day',
        'start_time',
        'end_time',
        'start_time_shift',
        'end_time_shift',
        # 'from_date',
        # 'to_date',
        'date',
        'is_leave',
        'is_off',
        'is_vacation',
        'is_active',
        'created_at',
    ]

    @admin.display(empty_value='-------')
    def today_day(self, employee_instance):
        if employee_instance.date:
            day = employee_instance.date.strftime('%A')
            return day

    @admin.display(empty_value='-------')
    def employee_name(self, employee_instance):
        if employee_instance.employee:
            return f'{employee_instance.employee.full_name}'



admin.site.register(Asset)
admin.site.register(AssetDocument)
admin.site.register(EmployeeSelectedService)
@admin.register(CategoryCommission)
class CategoryCommissionAdmin(admin.ModelAdmin):
    ordering = ['commission__employee', 'category_comission', 'from_value']
    list_display = ['id', 'employee', 'category_comission', 'from_value', 'to_value','commission_percentage','comission_choice','symbol']

    def employee(self, obj):
        if obj.commission and obj.commission.employee:
            return f'{obj.commission.employee.full_name}'
        
        return '-------'

@admin.register(GiftCards)
class GiftCardsAdmin(admin.ModelAdmin):
    list_display = ['id']
    
    
    
@admin.register(GiftDetail)
class GiftCardsAdmin(admin.ModelAdmin):
    list_display = ['id']
# from django.db.migrations.recorder import MigrationRecorder
# @admin.register(MigrationRecorder.Migration)
# class MigrationRecorderAdmin(admin.ModelAdmin):

#     search_fields = [
#         'name'
#     ]
#     list_filter = [
#         'name'
#     ]