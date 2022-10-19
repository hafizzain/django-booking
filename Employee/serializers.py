from dataclasses import fields
from genericpath import exists
from pyexpat import model
from Product.Constants.index import tenant_media_base_url
from Utility.Constants.Data.PermissionsValues import ALL_PERMISSIONS, PERMISSIONS_MODEL_FIELDS
from Utility.models import Country, GlobalPermissionChoices, State, City
from Service.models import Service
from Permissions.models import EmployePermission

from rest_framework import serializers
from .models import( Employee, EmployeeProfessionalInfo ,
               EmployeePermissionSetting, EmployeeModulePermission 
               , EmployeeMarketingPermission,
               StaffGroup, StaffGroupModulePermission, Attendance
               ,Payroll , CommissionSchemeSetting , Asset ,AssetDocument, EmployeeSelectedService
)

class ServicesEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields=['id', 'name', 'location']

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        exclude = ['is_deleted', 'created_at', 'unique_code', 'key']
    
class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        exclude = ['is_deleted', 'created_at', 'unique_code', 'key']
        
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        exclude = ['is_deleted', 'created_at', 'unique_code', 'key']
        
class EmployeInformationsSerializer(serializers.ModelSerializer):
    # services = serializers.SerializerMethodField(read_only=True)
    
    # def get_services(self, obj):
    #     return ServicesEmployeeSerializer(obj.services, many = True).data
    
    class Meta:
        model = EmployeeProfessionalInfo
        exclude = ['employee', 'id']
        
        
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
        
class EmployeeServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSelectedService
        fields = '__all__'
        
class GlobalPermissionOptionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = GlobalPermissionChoices
        fields = ['text']

class EmployeeGlobelPermission(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    def get_permissions(self, obj):
        returned_value = {}
        for permit in ALL_PERMISSIONS:
            returned_value[permit] = []
            for opt in PERMISSIONS_MODEL_FIELDS[permit](obj).all():
                returned_value[permit].append(opt.text)
        return returned_value
    
    
    class Meta:
        model = EmployePermission
        fields = ['permissions']
        
class EmployeSerializer(serializers.ModelSerializer):
    employee_info = serializers.SerializerMethodField(read_only=True)   
    image = serializers.SerializerMethodField()
    
    country = serializers.SerializerMethodField(read_only=True)
    state = serializers.SerializerMethodField(read_only=True)
    city = serializers.SerializerMethodField(read_only=True)   
    services = serializers.SerializerMethodField(read_only=True)
    
    staff_group = serializers.SerializerMethodField(read_only=True)
    
    def get_staff_group(self, obj):
        try:
            staff = StaffGroup.objects.get(employees = obj)
            print(staff)
            return str(staff.id)
            
            #return StaffGroupSerializers(staff).data 
            #
            print(staff)
        except Exception as err:
            print(err)
    
    # def get_staff_group(self, obj):
    #     try:
    #         staff = self.context["staff_id"]
    #         print(f"fsdgsd {staff}")
    #         return staff
    #     except Exception as err:
    #         print(err)
    
    
    def get_services(self, obj):
        try:
            service = EmployeeSelectedService.objects.filter(employee=obj)
            return EmployeeServiceSerializer(service, many = True).data
            # return EmployeeServiceSerializer(obj.services).data
        except Exception as err:
            print(err)
            None
    def get_country(self, obj):
        try:
            return CountrySerializer(obj.country).data
        except Country.DoesNotExist:
            return None
    def get_state(self, obj):
        try:
            return StateSerializer(obj.state).data
        except State.DoesNotExist:
            return None
    
    def get_city(self, obj):
        try:
            return CitySerializer(obj.city).data
        except City.DoesNotExist:
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
     
    permissions = serializers.SerializerMethodField()

    def get_permissions(self, obj):
        try:
            permission = EmployePermission.objects.get(employee=obj)
        except:
            return {}
        else:
            returned_value = {}
            for permit in ALL_PERMISSIONS:
                returned_value[permit] = []
                for opt in PERMISSIONS_MODEL_FIELDS[permit](permission).all():
                    returned_value[permit].append(opt.text)
            return returned_value
       
           
    # def get(self, obj):
    #     return {
    #         "brand": "test",
    #         "model": "test2",
    #     }
    class Meta:
        model = Employee
        fields = [
                'id', 
                'full_name',
                'employee_id',
                'email',
                'mobile_number', 
                'image',
                'dob', 
                'services',
                'gender', 
                'country',
                'state',
                'city',
                'postal_code', 
                'address' ,
                'joining_date', 
                'to_present', 
                'ending_date',  
                'is_active',
                'employee_info',
                'staff_group',
                # 'globel_permission',
                'permissions',       
                #'module_permissions',
                #'marketing_permissions',
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

    staff_permission = serializers.SerializerMethodField()
    employees = serializers.SerializerMethodField()
    #staff_permission = serializers.SerializerMethodField()
    
    def get_employees(self, obj):
        all_employees = obj.employees.all()
        return singleEmployeeSerializer(all_employees, many=True, context=self.context).data
            
    
    def get_staff_permission(self, obj):
        try:
            permission = EmployePermission.objects.get(staffgroup=obj)
        except:
            return {}
        else:
            returned_value = {}
            for permit in ALL_PERMISSIONS:
                returned_value[permit] = []
                for opt in PERMISSIONS_MODEL_FIELDS[permit](permission).all():
                    returned_value[permit].append(opt.text)
                    
            return returned_value
           
    
    class Meta:
        model = StaffGroup
        fields = [
            'id',
            'user',
            'business',
            'name', 
            'is_active',
            'staff_permission', 
            'created_at',
            'employees',
        ]
        
class StaffpermisionSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = StaffGroupModulePermission
        exclude = ['id']
#        fields ='__all__'

class AttendanceSerializers(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()

    #employee= EmployeSerializer(read_only=True)
    def get_employee(self, obj):
        try:
            data = Employee.objects.get(id=obj.employee.id)
            return EmployeSerializer( data, context=self.context).data
        except Exception as err:
            print(err)
    
    class Meta:
        model = Attendance
        
        fields = ['id','user','business','employee','in_time','out_time','is_active','employee']
        
class InformationPayrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfessionalInfo
        exclude = ['employee', 'id', 'designation']
        
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
    level = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField()
    employee_info = serializers.SerializerMethodField(read_only=True)
    
    country_name = serializers.SerializerMethodField(read_only=True)
    state_name = serializers.SerializerMethodField(read_only=True)
    city_name = serializers.SerializerMethodField(read_only=True)   
    
    def get_country_name(self, obj):
        try:
           return obj.country.name
        except Exception as err:
            return None
    def get_state_name(self, obj):
        try:
           return obj.state.name
        except Exception as err:
            return None
    
    def get_city_name(self, obj):
        try:
           return obj.city.name
        except Exception as err:
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
    
    def get_salary(self, obj):
        try:
            salary_info = EmployeeProfessionalInfo.objects.get(employee=obj)
            return salary_info.salary
        except Exception:
            return None
    def get_level(self, obj):
        try:
            level = EmployeeProfessionalInfo.objects.get(employee=obj)
            return level.level
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
        
    def get_employee_info(self, obj):
        try:
            professional = EmployeeProfessionalInfo.objects.get(employee=obj)
            return EmployeInformationsSerializer(professional).data
        except EmployeeProfessionalInfo.DoesNotExist:
            return None
        
    class Meta:
        model =Employee
        fields = [
            'id',
            'image',
            'salary',
            'email',
            'gender',
            'address', 
            'full_name',
            'country_name',
            'state_name',
            'city_name',
            'income_type',
            'designation', 
            'level',
            'employee_id',
            'employee_info'        
            ]   
        
class CommissionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CommissionSchemeSetting
        fields = '__all__'
      
class AssetdocmemtSerializer(serializers.ModelSerializer):
    document = serializers.SerializerMethodField()
    
    def get_document(self, obj):
        try:
            request = self.context["request"]
            url = tenant_media_base_url(request)
            return f'{url}{obj.document}'
        except Exception as err:
            print(err)
            return None
    
    class Meta:
        model = AssetDocument
        fields= ['id', 'document']
        
class AssetSerializer(serializers.ModelSerializer):
    document = serializers.SerializerMethodField()
    
    def get_document(self, obj):
        try:
            doc = AssetDocument.objects.filter(asset=obj)
            return AssetdocmemtSerializer(doc,many =True, context=self.context ).data
        
        except Exception as err:
            print(err)
            return None
    
    class Meta:
        model = Asset
        fields = ['id','name','employee','given_date','return_date', 'document']


class WorkingScheduleSerializer(serializers.ModelSerializer):
    start_time = serializers.SerializerMethodField(read_only=True)
    end_time = serializers.SerializerMethodField(read_only=True)
    monday =  serializers.SerializerMethodField(read_only=True)
    tuesday =  serializers.SerializerMethodField(read_only=True)
    wednesday =  serializers.SerializerMethodField(read_only=True)
    thursday =  serializers.SerializerMethodField(read_only=True)
    friday =  serializers.SerializerMethodField(read_only=True)
    saturday =  serializers.SerializerMethodField(read_only=True)
    sunday =  serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField()

    
    
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return None
    
    def get_start_time(self, obj):        
        try:
            time = EmployeeProfessionalInfo.objects.get(employee=obj)
            return time.start_time 
        except: 
            return None
    def get_end_time(self, obj):        
        try:
            time = EmployeeProfessionalInfo.objects.get(employee=obj)
            return time.end_time
        except: 
            return None
    
    def get_monday(self, obj):
        try:
            day = EmployeeProfessionalInfo.objects.get(employee=obj)
            return day.monday
        except Exception as err:
            print(err)
            return None
    def get_tuesday(self, obj):
        try:
            day = EmployeeProfessionalInfo.objects.get(employee=obj)
            return day.tuesday
        except Exception as err:
            print(err)
            return None
    def get_wednesday(self, obj):
        try:
            day = EmployeeProfessionalInfo.objects.get(employee=obj)
            return day.wednesday
        except Exception as err:
            print(err)
            return None 
    def get_thursday(self, obj):
        try:
            day = EmployeeProfessionalInfo.objects.get(employee=obj)
            return day.thursday
        except Exception as err:
            return None       
    def get_friday(self, obj):
        try:
            day = EmployeeProfessionalInfo.objects.get(employee=obj)
            return day.friday
        except Exception as err:
            return None       
    def get_saturday(self, obj):
        try:
            day = EmployeeProfessionalInfo.objects.get(employee=obj)
            return day.saturday
        except Exception as err:
            return None       
    def get_sunday(self, obj):
        try:
            day = EmployeeProfessionalInfo.objects.get(employee=obj)
            return day.sunday
        except Exception as err:
            return None       
    
    class Meta:
        model = Employee
        fields = ['id', 'full_name','image','start_time', 'end_time', 'monday','tuesday','wednesday','thursday','friday','saturday','sunday']
