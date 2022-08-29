from rest_framework import serializers
from .models import( Employee, EmployeeProfessionalInfo ,
               EmployeePermissionSetting, EmployeeModulePermission 
               , EmployeeMarketingPermission,
               StaffGroup, StaffGroupModulePermission, Attendance
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
            Permission, created = EmployeePermissionSetting.objects.get_or_create(employee=obj)
            return EmployPermissionSerializer(Permission).data
        except EmployeePermissionSetting.DoesNotExist:
            return None
    #EmployeeModulePermission 
    def get_module_permissions(self, obj):
        try: 
            ModulePermission, created = EmployeeModulePermission.objects.get_or_create(employee=obj)
            return EmployeModulesSerializer(ModulePermission).data
        except EmployeeModulePermission.DoesNotExist:
            return None
    #EmployeeMarketingPermission
    def get_marketing_permissions(self, obj):
        try:
            MarketingPermission, created = EmployeeMarketingPermission.objects.get_or_create(employee=obj)
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
            permission = StaffGroupModulePermission.objects.get(staff_group=obj)
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