from rest_framework import serializers
from .models import( Employee, EmployeeProfessionalInfo ,
               EmployeePermissionSetting, EmployeeModulePermission 
               , EmployeeMarketingPermission,
               StaffGroup, StaffGroupModulePermission
)
class EmployeSerializer(serializers.ModelSerializer):
    employee_info = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    module_permissions =serializers.SerializerMethodField()
    marketing_permissions= serializers.SerializerMethodField()
    
    def get_employee_info(self, obj):
        try:
            professional = EmployeeProfessionalInfo.objects.get(employee=obj)
            return EmployeInformationsSerializer(professional).data
        except EmployeeProfessionalInfo.DoesNotExist:
            return None
    #EmployeePermission
    def get_permissions(self, obj):
        try:
            Permission = EmployeePermissionSetting.objects.get(employee=obj)
            return EmployPermissionSerializer(Permission).data
        except EmployeePermissionSetting.DoesNotExist:
            return None
    #EmployeeModulePermission 
    def get_module_permissions(self, obj):
        try: 
            ModulePermission = EmployeeModulePermission.objects.get(employee=obj)
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

    class Meta:
        #EmployeeProfessional
       
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
        
        
class EmployeInformationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfessionalInfo
        fields = '__all__'
        
        
class EmployPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeePermissionSetting
        fields = '__all__'
        
class EmployeModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeModulePermission
        fields = '__all__'
        
class EmployeeMarketingSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeeMarketingPermission
        fields = '__all__'
        
class StaffGroupSerializers(serializers.ModelSerializer):
    class Meta:
        model = StaffGroup
        fields = '__all__'
        
class StaffermisionSerializers(serializers.ModelSerializer):
    class Meta:
        model = StaffGroupModulePermission
        fields = '__all__'  