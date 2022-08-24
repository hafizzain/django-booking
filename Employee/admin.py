from django.contrib import admin

from .models import Employee, EmployeeProfessionalInfo
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