from rest_framework import serializers
from Business.models import BusinessAddress
from Employee.models import Employee, EmployeeProfessionalInfo
from Product.Constants.index import tenant_media_base_url

from TragetControl.models import ServiceTarget, StaffTarget, StoreTarget, TierStoreTarget


class EmployeeNameSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)
    designation = serializers.SerializerMethodField(read_only=True)
    
    def get_designation(self, obj):        
        try:
            designation = EmployeeProfessionalInfo.objects.get(employee=obj)
            return designation.designation 
        except: 
            return None
    
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return None
    class Meta:
        model = Employee
        fields = [
                'id', 
                'full_name',
                'employee_id',
                'image',
                'designation'
        ]
class StaffTargetSerializers(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    
    def get_employee(self,obj):
        try:
            emp = Employee.objects.get(id = str(obj.employee))
            return EmployeeNameSerializer(emp, context=self.context).data
        except Exception as err:
            print(err)
    class Meta:
        model = StaffTarget
        fields = '__all__'

class BusinessAddressSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = BusinessAddress
        fields = ['id', 'address_name' ]

class TierStoreTargetSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = TierStoreTarget
        fields = '__all__'
class StoreTargetSerializers(serializers.ModelSerializer):
    tier = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    
    def get_location(self, obj):
        try:
            loc = BusinessAddress.objects.get(id = str(obj.location))
            return BusinessAddressSerializers(loc).data
        except Exception as err:
            print(err)
    
    def get_tier(self,obj):
        try:
            tier = TierStoreTarget.objects.filter(storetarget = obj, is_primary = True )
            return TierStoreTargetSerializers(tier,many = True ,context=self.context).data
        except Exception as err:
            print(err)
    
    class Meta:
        model = StoreTarget
        fields = '__all__'
        
class ServiceTargetSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = ServiceTarget
        fields = '__all__'