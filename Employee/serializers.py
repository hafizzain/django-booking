from dataclasses import fields
from genericpath import exists
from pyexpat import model
from rest_framework import serializers
from .models import( Employee, EmployeeProfessionalInfo ,
               EmployeePermissionSetting, EmployeeModulePermission 
               , EmployeeMarketingPermission,
               StaffGroup, StaffGroupModulePermission, Attendance
               ,Payroll
)
class EmployeInformationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfessionalInfo
        exclude = ['employee', 'id', 'services']
        
        
class EmployPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeePermissionSetting
        exclude = ['employee', 'created_at', 'id']
        
class EmployeModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeModulePermission
        exclude = ['employee', 'created_at', 'id']
        
class EmployeeMarketingSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeeMarketingPermission
        exclude = ['employee', 'created_at', 'id']
        
class EmployeSerializer(serializers.ModelSerializer):
    employee_info = serializers.SerializerMethodField(read_only=True)
    permissions = serializers.SerializerMethodField(read_only=True)
    module_permissions =serializers.SerializerMethodField(read_only=True)
    marketing_permissions= serializers.SerializerMethodField(read_only=True)
    
    # def get_field_names(self, declared_fields , obj):
        
    #       expanded_fields = super(EmployPermissionSerializer, self).get_field_names(declared_fields, obj)
          
    #       if getattr(self.Meta, 'extra_fields', None):
    #          return expanded_fields + self.Meta.extra_fields
    #       else:
    #           return expanded_fields

    def get_employee_info(self, obj):
        try:
            professional = EmployeeProfessionalInfo.objects.get(employee=obj)
            return EmployeInformationsSerializer(professional).data
        except EmployeeProfessionalInfo.DoesNotExist:
            return None
    #EmployeePermission
    def get_permissions(self, obj):
        try:
            Permission= EmployeePermissionSetting.objects.get(employee=obj)
            
            return EmployPermissionSerializer(Permission).data
        except EmployeePermissionSetting.DoesNotExist:
            return None
    #EmployeeModulePermission 
    def get_module_permissions(self, obj):
        try: 
            ModulePermission= EmployeeModulePermission.objects.get(employee=obj)      
            return EmployeModulesSerializer(ModulePermission).data
        except EmployeeModulePermission.DoesNotExist:
            return None
    #EmployeeMarketingPermission
    def get_marketing_permissions(self, obj):
        try:
            MarketingPermission = EmployeeMarketingPermission.objects.get(employee=obj)
            return EmployeeMarketingSerializers(MarketingPermission).data
        except EmployeeMarketingPermission.DoesNotExist:
            return None       
    # def get(self, obj):
    #     return {
    #         "brand": "test",
    #         "model": "test2",
    #     }
    class Meta:
        model = Employee
        fields = [
                'id', 
                'user',
                'business',
                'full_name',
                'employee_id',
                'email',
                'mobile_number', 
                'image',
                'dob', 
                'gender', 
                'country', 
                'state', 
                'city', 
                'postal_code', 
                'address' ,
                'joining_date', 
                'to_present', 
                'ending_date',  
                'employee_info',
                'permissions',       
                'module_permissions',
                'marketing_permissions',
            ]
    # def to_representation(self, instace):
    #     permissions = self.get_permissions(instace)
    #     # return permissions.update({
    #     #     'id': instace.id,
    #     #     'name': instace.full_name,
            
    #     # })
    #     return {
    #         "nme": instace.full_name,
    #         permissions: permissions
    #     }

        
        

class StaffGroupSerializers(serializers.ModelSerializer):
    #employe = serializers.SerializerMethodField()
    
    # def get_employe(self, obj):
    #     employe_id = self.context.get('employee')
    #     return employee_id
    
    staff_permission = serializers.SerializerMethodField()
    
    def get_staff_permission(self, obj):
        
        try:
            permission, created = StaffGroupModulePermission.objects.get_or_create(staff_group=obj)
            return StaffpermisionSerializers(permission).data
        except StaffGroupModulePermission.DoesNotExist:
            return None    
    
    class Meta:
        model = StaffGroup
        fields = [
            'id',
            'user',
            'business',
            'name', 
            'is_active',
            'staff_permission', 
            'employees',
        ]
        
class StaffpermisionSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = StaffGroupModulePermission
        exclude = ['id']
#        fields ='__all__'

class AttendanceSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = Attendance
        fields = '__all__'
        
class InformationPayrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfessionalInfo
        exclude = ['employee', 'id', 'services', 'designation']
        
class EmployPayrollSerializers(serializers.ModelSerializer):
    salary = serializers.SerializerMethodField(read_only=True)
    income_type = serializers.SerializerMethodField(read_only=True)
    
    def get_salary(self, obj):
        try:
            salary_info = EmployeeProfessionalInfo.objects.get(employee=obj)
            return salary_info.salary
        except Exception:
            return None
        
    def get_income_type(self, obj):
        try:
            income_info = EmployeeProfessionalInfo.objects.get(employee=obj)
            return income_info.income_type 
        except: 
            return None
    
    class Meta:
        model= Employee
        fields = [
           'id',
            'income_type',
            'salary'
         ]        
class PayrollSerializers(serializers.ModelSerializer):
    employee = EmployPayrollSerializers(read_only=True)
    class Meta:
        model = Payroll
        fields = [
            'id',
            'name',
            'created_at', 
            #'employee',
            'employee'
            ]
class singleEmployeeSerializer(serializers.ModelSerializer):
    salary = serializers.SerializerMethodField(read_only=True)
    income_type = serializers.SerializerMethodField(read_only=True)
    designation = serializers.SerializerMethodField(read_only=True)
    
    def get_salary(self, obj):
        try:
            salary_info = EmployeeProfessionalInfo.objects.get(employee=obj)
            return salary_info.salary
        except Exception:
            return None
        
    def get_income_type(self, obj):        
        try:
            income_info = EmployeeProfessionalInfo.objects.get(employee=obj)
            return income_info.income_type 
        except: 
            return None
        
    def get_designation(self, obj):        
        try:
            designation = EmployeeProfessionalInfo.objects.get(employee=obj)
            return designation.designation 
        except: 
            return None
        
    class Meta:
        model =Employee
        fields = [
            'id',
            'full_name',
            'salary',
            'income_type',
            'designation',           
            ]   