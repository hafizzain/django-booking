from rest_framework import serializers
from .models import( Employee, EmployeeProfessionalInfo ,
               EmployeePermissionSetting, EmployeeModulePermission 
               , EmployeeMarketingPermission
)
class EmployeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'
        
        
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
        model = EmployeeProfessionalInfo
        fields = '__all__'
        
class EmployeeMarketingSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeeMarketingPermission
        fields = '__all__'