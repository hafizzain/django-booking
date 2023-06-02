from rest_framework import serializers
from Business.models import BusinessAddress
from Employee.models import Employee, EmployeeProfessionalInfo
from Product.Constants.index import tenant_media_base_url
from Product.models import Brand
from Service.models import ServiceGroup

from TragetControl.models import ServiceTarget, StaffTarget, StoreTarget, TierStoreTarget , RetailTarget


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        fields = ['id', 'address_name']
class EmployeeNameSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)
    designation = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    
    def get_location(self, obj):
        loc = obj.location.all()
        return LocationSerializer(loc, many = True).data
    
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
                'designation',
                'location'
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
        fields = ['id','month', 'service_target', 'retail_target', 'year','employee','created_at','years']

class ServiceGroupSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = ServiceGroup
        fields = ['id', 'name' ]

class BusinessAddressSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = BusinessAddress
        fields = ['id', 'address_name' ]

class BrandSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = Brand
        fields = ['id', 'name' ]

class TierStoreTargetSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = TierStoreTarget
        fields = '__all__'
        
class GETStoreTargetSerializers(serializers.ModelSerializer):
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
            tier = TierStoreTarget.objects.filter(storetarget = obj, )#is_primary = True )
            return TierStoreTargetSerializers(tier, many = True ,context=self.context).data
        except Exception as err:
            print(err)
    
    class Meta:
        model = StoreTarget
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
            tier = TierStoreTarget.objects.filter(storetarget = obj)
            return TierStoreTargetSerializers(tier,many = True ,context=self.context).data
        except Exception as err:
            print(err)
    
    class Meta:
        model = StoreTarget
        fields = '__all__'

class RetailTargetSerializers(serializers.ModelSerializer):
    
    location = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    
    def get_location(self, obj):
        try:
            loc = BusinessAddress.objects.get(id = str(obj.location))
            return BusinessAddressSerializers(loc).data
        except Exception as err:
            print(err)
            
    def get_brand(self, obj):
        try:
            brand = Brand.objects.get(id = str(obj.brand))
            return BrandSerializers(brand).data
        except Exception as err:
            print(err)
    
    class Meta:
        model = RetailTarget
        fields = ['id', 'location', 'brand', 'month','brand_target','year']
    
class ServiceTargetSerializers(serializers.ModelSerializer):
    
    location = serializers.SerializerMethodField()
    service_group = serializers.SerializerMethodField()
    
    def get_location(self, obj):
        try:
            loc = BusinessAddress.objects.get(id = str(obj.location))
            return BusinessAddressSerializers(loc).data
        except Exception as err:
            print(err)
            
    def get_service_group(self, obj):
        try:
            loc = ServiceGroup.objects.get(id = str(obj.service_group))
            return ServiceGroupSerializers(loc).data
        except Exception as err:
            print(err)
    
    class Meta:
        model = ServiceTarget
        fields = ['id', 'location', 'service_group', 'month','service_target','year']