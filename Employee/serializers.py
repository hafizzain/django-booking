from dataclasses import fields
from genericpath import exists
from pyexpat import model
from Appointment.models import AppointmentCheckout
from Business.models import BusinessAddress
from Employee.Constants.total_sale import total_sale_employee
from Product.Constants.index import tenant_media_base_url, tenant_media_domain
from Tenants.models import Domain, Tenant
from Utility.Constants.Data.PermissionsValues import ALL_PERMISSIONS, PERMISSIONS_MODEL_FIELDS
from Utility.models import Country, Currency, GlobalPermissionChoices, State, City
from Service.models import Service
from Permissions.models import EmployePermission
# from datetime import datetime, timedelta
from datetime import datetime, timedelta
import calendar

from rest_framework import serializers
from .models import( EmployeDailySchedule, Employee, EmployeeProfessionalInfo ,
               EmployeePermissionSetting, EmployeeModulePermission 
               , EmployeeMarketingPermission, SallarySlipPayrol,
               StaffGroup, StaffGroupModulePermission, Attendance
               ,Payroll , CommissionSchemeSetting , Asset ,AssetDocument,
               EmployeeSelectedService, Vacation ,CategoryCommission
)
from Authentication.models import AccountType, User
from django_tenants.utils import tenant_context


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
 
class LocationSerializer(serializers.ModelSerializer):
    currency = serializers.SerializerMethodField(read_only=True)
    
    def get_currency(self, obj):
        try:
            cur = Currency.objects.get(id  = str(obj.currency) )
            return cur.code
        except Exception as err:
            return str(err)
            
    class Meta:
        model = BusinessAddress
        fields = ['id', 'address_name', 'currency']
     
        
class EmployeInformationsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EmployeeProfessionalInfo
        exclude = ['employee', 'id']
        
        
class ScheduleSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField(read_only=True)
    
    def get_employee(self, obj):
        try:
            data = Employee.objects.get(id = str(obj.employee))
            return EmployeeNameSerializer(data, context=self.context).data
        except Exception as err:
            print(err)
         
    class Meta:
        model = EmployeDailySchedule
        fields = '__all__'        
        
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
    service_name = serializers.SerializerMethodField()
    
    def get_service_name(self, obj):
        try:
            name = Service.objects.get(id = obj.service.id)
            return name.name
        except Exception as err:
            print(err)
            return None
    class Meta:
        model = EmployeeSelectedService
        fields = ['employee','level', 'service', 'id', 'service_name']
        
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
    
    monday =  serializers.SerializerMethodField(read_only=True)
    tuesday =  serializers.SerializerMethodField(read_only=True)
    wednesday =  serializers.SerializerMethodField(read_only=True)
    thursday =  serializers.SerializerMethodField(read_only=True)
    friday =  serializers.SerializerMethodField(read_only=True)
    saturday =  serializers.SerializerMethodField(read_only=True)
    sunday =  serializers.SerializerMethodField(read_only=True)
    permissions = serializers.SerializerMethodField()
     
    staff_group = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    schedule = serializers.SerializerMethodField(read_only=True)

    def get_schedule(self, obj):
        try:
            all_schedule = EmployeDailySchedule.objects.filter(employee = obj)
            return ScheduleSerializer(all_schedule, many = True, context=self.context).data
        except Exception as err:
            print(err)
            None
            
    def get_location(self, obj):
        try:
            #loc = BusinessAddress.objects.filter(id=obj.location.id)
            all_location = obj.location.all()
            return LocationSerializer(all_location, many = True).data
            # return EmployeeServiceSerializer(obj.services).data
        except Exception as err:
            print(err)
            None
    
    def get_staff_group(self, obj):
        try:
            staff = StaffGroup.objects.get(employees = obj)
            return str(staff.id)
            
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
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
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
        except Exception as err:
            return None
     
   

    def get_permissions(self, obj):
        try:
            permission = EmployePermission.objects.get(employee=obj)
        except:
            return {}
        else:
            returned_value = {}
            try:            
                for permit in ALL_PERMISSIONS:
                    returned_value[permit] = []
                    for opt in PERMISSIONS_MODEL_FIELDS[permit](permission).all():
                        returned_value[permit].append(opt.text)
                return returned_value
            except Exception as err:
                pass
                #return str(err)

    def get_monday(self, obj):
        try:
            day = EmployeeProfessionalInfo.objects.get(employee=obj)
            return day.monday
        except Exception as err:
            return None
    def get_tuesday(self, obj):
        try:
            day = EmployeeProfessionalInfo.objects.get(employee=obj)
            return day.tuesday
        except Exception as err:
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
                'location',
                'schedule',
                # 'globel_permission',
                'permissions' , 'monday','tuesday','wednesday','thursday','friday','saturday','sunday'    
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
class EmployeeNameSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)
    designation = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    
    def get_location(self, obj):
        loc = obj.location.all()
        return LocationSerializer(loc, many =True ).data
        # try:
        #     loc = BusinessAddress.objects.get(id = str(obj.location))
        #     return LocationSerializer(loc).data
        # except Exception as err:
        #     print(err)
        #     None
    
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
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
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
                'location',
        ]

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
        
        fields = ['id','user','business','employee','in_time','out_time','is_active','created_at','employee']
        
class InformationPayrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfessionalInfo
        exclude = ['employee', 'id', 'designation']
        
class EmployPayrollSerializers(serializers.ModelSerializer):
    salary = serializers.SerializerMethodField(read_only=True)
    income_type = serializers.SerializerMethodField(read_only=True)
    start_time = serializers.SerializerMethodField(read_only=True)
    end_time = serializers.SerializerMethodField(read_only=True)
    # payroll = serializers.SerializerMethodField(read_only=True)


    # def get_salary(self, obj):
    #     try:
    #         salary_info = EmployeeProfessionalInfo.objects.get(employee=obj)
    #         return salary_info.salary
    #     except Exception:
    #         return None
        
    def get_salary(self, obj):
        try:
            salary_info = EmployeeProfessionalInfo.objects.get(employee=obj)
            # income_type = salary_info.income_type
            # salary = salary_info.salary
            
            # if income_type == 'Daily_Income':
            #     total_days = (datetime.today() - obj.date_of_joining).days
            #     absent_days = Attendance.object.filter(out_time=True).count()
            #     salary -= (absent_days * salary / total_days)
                
            return salary_info.salary
        except Exception:
            return None
        
    def get_income_type(self, obj):
        try:
            income_info = EmployeeProfessionalInfo.objects.get(employee=obj)
            return income_info.income_type 
        except: 
            return None
        
    def get_start_time(self, obj):
        try:
            start_time = EmployeeProfessionalInfo.objects.get(employee=obj)
            return start_time.start_time 
        except: 
            return None
    def get_end_time(self, obj):
        try:
            end_time = EmployeeProfessionalInfo.objects.get(employee=obj)
            return end_time.end_time 
        except: 
            return None
        


    # def get_payroll(self, obj):
    #     try:
    #         salary_info = EmployeeProfessionalInfo.objects.get(employee=obj)
    #         payroll = salary_info.salary

    #         if salary_info.income_type == 'Hourly_Rate':
    #             # Calculate payroll based on hourly rate
    #             payroll_per_hour = payroll / 8
    #             total_hours = 8
    #             if total_hours:
    #                 payroll -= total_hours * payroll_per_hour
    #             else:
    #                 payroll = 0

    #         # Deduct payroll for absent day
    #         if Attendance.object.filter(out_time=True).count():
    #             if salary_info.income_type == 'Hourly_Rate':
    #                 payroll -= payroll_per_hour
    #             elif salary_info.income_type == 'Daily_Income':
    #                 payroll = 0
    #             elif salary_info.income_type == 'Monthly_Salary':
    #                 payroll_per_day = payroll / 30
    #                 payroll -= payroll_per_day
                    
    #                 # Deduct additional payroll for each day of absence
    #                 absent_days = Attendance.object.filter(out_time=True).count()
    #                 payroll -= absent_days * payroll_per_day

    #         return payroll

    #     except Exception:
    #         return None
                
    
    class Meta:
        model= Employee
        fields = [
            'id',
            'full_name',
            'income_type',
            'salary',
            'start_time',
            'end_time',
            'employee_id',
            # 'payroll',
            
         ]        

class SallarySlipPayrolSerializers(serializers.ModelSerializer):
    employee = EmployPayrollSerializers(read_only=True)
    class Meta:
        model = SallarySlipPayrol
        fields = [
            'id',
            'created_at',
            'month' ,
            'employee',
            ]
class SallarySlipPayrol_EmployeSerializers(serializers.ModelSerializer):
    class Meta:
        model = SallarySlipPayrol
        fields = [
            'id',
            'created_at',
            'month' ,
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
        
class LocationSerializerOP(serializers.ModelSerializer):

    class Meta:
        model = BusinessAddress
        fields = ['id']

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
    services = serializers.SerializerMethodField(read_only=True)
        
    location = serializers.SerializerMethodField()
    total_sale = serializers.SerializerMethodField()
    
    def get_total_sale(self,obj):
        return total_sale_employee(obj)

    
    def get_location(self, obj):
        all_location = obj.location.all()
        return LocationSerializerOP(all_location, many = True).data


    def get_services(self, obj):
        try:
            service = EmployeeSelectedService.objects.filter(employee=obj)
            return EmployeeServiceSerializer(service, many = True).data
        except Exception as err:
            print(err)
            None
    
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
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
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
            level = EmployeeSelectedService.objects.get(employee=obj)
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
        except:
            return None
        
    class Meta:
        model =Employee
        fields = [
            'id',
            'total_sale',
            'image',
            'salary',
            'email',
            'gender',
            'address', 
            'mobile_number',
            'full_name',
            'country_name',
            'state_name',
            'city_name',
            'income_type',
            'designation', 
            'level',
            'employee_id',
            'employee_info',  
            'services',
            'created_at' ,
            'location', 
            'is_active',
            ]   

class CategoryCommissionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CategoryCommission
        fields = '__all__'
     
class CommissionSerializer(serializers.ModelSerializer):
    category_comission = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()
    
    def get_employee(self,obj):
        try:
            emp = Employee.objects.get(id = str(obj.employee))
            return EmployeeNameSerializer(emp, context=self.context).data
        except Exception as err:
            print(err)
            
    
    def get_category_comission(self, obj):
        category = CategoryCommission.objects.filter(commission = obj)
        return CategoryCommissionSerializer(category, many = True).data
    class Meta:
        model = CommissionSchemeSetting
        #fields = '__all__'
        exclude = ('sale_price_before_discount','created_at' ,'from_value','to_value','percentage','user',
                   'sale_price_including_tax','service_price_before_membership_discount')
        
class VacationSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    
    def get_employee(self,obj):
        try:
            emp = Employee.objects.get(id = str(obj.employee))
            return EmployeeNameSerializer(emp, context=self.context).data
        except Exception as err:
            print(err)
    class Meta:
        model = Vacation
        fields = '__all__'
      
class AssetdocmemtSerializer(serializers.ModelSerializer):
    document = serializers.SerializerMethodField()
    
    def get_document(self, obj):
        try:
            request = self.context["request"]
            url = tenant_media_base_url(request, is_s3_url=False)
            return f'{url}{obj.document}'
        except Exception as err:
            print(err)
            return None
    
    class Meta:
        model = AssetDocument
        fields= ['id', 'document']
       
class AssetSerializer(serializers.ModelSerializer):
    document = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()
    
    def get_employee(self, obj):
        try:
            emp = Employee.objects.get(id = str(obj.employee))
            print(emp)
            return EmployeeNameSerializer(emp).data
        except Exception as err:
            print(err)
    
    def get_document(self, obj):
        try:
            doc = AssetDocument.objects.filter(asset=obj)
            return AssetdocmemtSerializer(doc,many =True, context=self.context ).data
        
        except Exception as err:
            print(err)
            return None
    
    class Meta:
        model =Asset
        fields = ['id','name','employee','given_date','return_date', 'document', 'created_at', 'is_active']

class ScheduleSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField(read_only=True)
    
    def get_employee(self, obj):
        try:
            data = Employee.objects.get(id = str(obj.employee))
            return EmployeeNameSerializer(data, context=self.context).data
        except Exception as err:
            print(err)
            
    class Meta:
        model = EmployeDailySchedule
        fields = '__all__'
        
class WorkingSchedulePayrollSerializer(serializers.ModelSerializer):
    total_hours = serializers.SerializerMethodField(read_only=True)
    end_time = serializers.SerializerMethodField(read_only=True)
    total_hours_dummy = serializers.SerializerMethodField(read_only=True)
    
    def get_end_time(self, obj):
        try:
            if obj.start_time_shift != None:
                return str(obj.end_time_shift)
            if obj.end_time:
                return str(obj.end_time)
        except:
            pass
                    
    def get_total_hours_dummy(self, obj):
        return obj.total_hours
                    
    
    def get_total_hours(self, obj):

        income_type = self.context.get('income_type', None)
        
        try:
            if income_type == 'Hourly_Rate':
                if obj.is_vacation:
                    return '8'
                elif obj.is_leave:
                    return '0'
                else:
                    pass
                
            if obj.start_time is None or obj.end_time is None:
                return '0'  # Return '0' if any of the time values is None

            shift1_start = datetime.strptime(obj.start_time.strftime("%H:%M:%S"), "%H:%M:%S")
            shift1_end = datetime.strptime(obj.end_time.strftime("%H:%M:%S"), "%H:%M:%S")

            if shift1_end < shift1_start:
                shift1_end += timedelta(days=1)  # Add 1 day if the shift ends on the next day

            total_hours = (shift1_end - shift1_start).total_seconds() / 3600  # calculate the time difference in hours

            if obj.start_time_shift and obj.end_time_shift:
                shift2_start = datetime.strptime(obj.start_time_shift.strftime("%H:%M:%S"), "%H:%M:%S")
                shift2_end = datetime.strptime(obj.end_time_shift.strftime("%H:%M:%S"), "%H:%M:%S")

                if shift2_end < shift2_start:
                    shift2_end += timedelta(days=1)  # Add 1 day if the shift ends on the next day

                shift2_hours = (shift2_end - shift2_start).total_seconds() / 3600  # calculate the time difference in hours
                total_hours += shift2_hours

            total_hours = float(total_hours)  # convert to integer
            return float(total_hours)

        except Exception as err:
            return str(err)
        
    class Meta:
        model = EmployeDailySchedule
        fields = ['id','user','business','employee','day','vacation','start_time','end_time',
                  'start_time_shift','end_time_shift','from_date','to_date','total_hours','note',
                  'date','is_leave','is_off','is_vacation','is_active','created_at','updated_at', 'total_hours_dummy']

class WorkingScheduleSerializer(serializers.ModelSerializer):
    start_time = serializers.SerializerMethodField(read_only=True)
    end_time = serializers.SerializerMethodField(read_only=True)
    
    # monday =  serializers.SerializerMethodField(read_only=True)
    # tuesday =  serializers.SerializerMethodField(read_only=True)
    # wednesday =  serializers.SerializerMethodField(read_only=True)
    # thursday =  serializers.SerializerMethodField(read_only=True)
    # friday =  serializers.SerializerMethodField(read_only=True)
    # saturday =  serializers.SerializerMethodField(read_only=True)
    # sunday =  serializers.SerializerMethodField(read_only=True)
    
    schedule =  serializers.SerializerMethodField(read_only=True)
    vacation =  serializers.SerializerMethodField(read_only=True)

    # absense = serializers.SerializerMethodField(read_only=True)
    
    image = serializers.SerializerMethodField()
    
    location = serializers.SerializerMethodField(read_only=True)
    
    def get_location(self, obj):
        loc = obj.location.all()
        return LocationSerializer(loc, many =True ).data

    
    def get_schedule(self, obj):
        schedule =  EmployeDailySchedule.objects.filter(employee= obj )
        return ScheduleSerializer(schedule, many = True,context=self.context).data
    
    def get_vacation(self, obj):
        vacation = Vacation.objects.filter(employee= obj )
        return VacationSerializer(vacation, many = True,context=self.context).data
    
    # def get_absense(self, obj):
    #     absense = Vacation.objects.filter(employee= obj )
    #     return VacationSerializer(absense, many = True,context=self.context).data
    
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
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
    
    class Meta:
        model = Employee
        fields = ['id', 'full_name','image','start_time', 'end_time','vacation','schedule','location','created_at']

class SingleEmployeeInformationSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    employee_permission = serializers.SerializerMethodField()
    
    def get_employee_permission(self, obj):
        try:
            permission = EmployePermission.objects.get(employee=obj)
        except:
            return {}
        else:
            returned_value = {}
            try:            
                for permit in ALL_PERMISSIONS:
                    returned_value[permit] = []
                    for opt in PERMISSIONS_MODEL_FIELDS[permit](permission).all():
                        returned_value[permit].append(opt.text)
                return returned_value
            except Exception as err:
                pass
    
    def get_location(self, obj):
        loc = obj.location.all()
        return LocationSerializer(loc, many =True ).data
    
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return None
    
    class Meta:
        model = Employee
        fields = ['id', 'image','location','full_name', 'email', 
                  'mobile_number','country','state','city', 'address', 'postal_code', 'employee_permission', 'is_active']
class EmployeeInformationSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    def get_image(self, obj):
        if obj.image:
            try:
                tenant = self.context["tenant"]
                url = tenant_media_domain(tenant.schema_name, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return None
    
    class Meta:
        model = Employee
        fields = ['id','business', 'image','full_name', 'email', 'mobile_number','country','state','city', 'address', 'postal_code']

class Payroll_WorkingScheduleSerializer(serializers.ModelSerializer):    
    schedule =  serializers.SerializerMethodField(read_only=True)    
    image = serializers.SerializerMethodField()
    income_type = serializers.SerializerMethodField(read_only=True)
    salary = serializers.SerializerMethodField(read_only=True)
    total_earning = serializers.SerializerMethodField(read_only=True)    
    location = serializers.SerializerMethodField(read_only=True)
    sallaryslip = serializers.SerializerMethodField(read_only=True)
    total_hours = serializers.SerializerMethodField(read_only=True)
    
    def get_location(self, obj):
        loc = obj.location.all()
        return LocationSerializer(loc, many =True ).data
    

    def get_total_hours(self, obj):
        start_date = self.context.get('start_date', None)
        end_date = self.context.get('end_date', None)
        now_date = datetime.now()

        month_start_date = start_date or f'{now_date.year}-{now_date.month}-01'
        month_end_date = end_date or now_date.strftime('%Y-%m-%d')

        employee_schedules =  EmployeDailySchedule.objects.filter(
            employee = obj,
            is_leave = False,
            date__range = (month_start_date, month_end_date)
        ).order_by('-date')
        hours = 0
        for schedule in employee_schedules:
            hours += schedule.total_hours
        
        return hours


    def get_total_earning(self, obj):
        now_date = datetime.now()
        total_days = calendar.monthrange(now_date.year, now_date.month)[1]
        date = now_date.date

        start_date = self.context.get('start_date', None)
        end_date = self.context.get('end_date', None)

        month_start_date = start_date or f'{now_date.year}-{now_date.month}-01'
        month_end_date = end_date or f'{now_date.year}-{now_date.month}-{total_days}'

        employee_schedules =  EmployeDailySchedule.objects.filter(
            employee = obj,
            is_leave = False,
            date__range = (month_start_date, month_end_date)
        ).order_by('-date')

        try:
            income_type_info = EmployeeProfessionalInfo.objects.get(employee=obj)
        except:
            income_type = None
        else:
            total_earning = 0
            salary = income_type_info.salary # 300
            income_type = income_type_info.income_type

            if income_type == 'Monthly_Salary':
                per_day_salary = salary / total_days # 10
                total_earning += (employee_schedules.count() * per_day_salary)

            elif income_type == 'Daily_Income':
                total_earning += (employee_schedules.count() * salary)
                pass
            elif income_type == 'Hourly_Rate':
                total_hours = 0
                for schedule in employee_schedules:
                    total_hours += schedule.total_hours
                
                total_earning += (total_hours * salary)

            return total_earning

    def get_salary(self, obj):        
        try:
            income_info = EmployeeProfessionalInfo.objects.get(employee=obj)
            return income_info.salary 
        except: 
            return None
        
    def get_income_type(self, obj):        
        try:
            income_info = EmployeeProfessionalInfo.objects.get(employee=obj)
            return income_info.income_type 
        except: 
            return None

    def get_schedule(self, obj):
        now_date = datetime.now()
        start_date = self.context.get('start_date', None)
        end_date = self.context.get('end_date', None)

        total_days = calendar.monthrange(now_date.year, now_date.month)[1]

        month_start_date = start_date or f'{now_date.year}-{now_date.month}-01'
        month_end_date = end_date or f'{now_date.year}-{now_date.month}-{total_days}'

        schedule =  EmployeDailySchedule.objects.filter(
            employee = obj,
            date__range = (month_start_date, month_end_date)
        ).exclude(is_leave = True).order_by('-date')
        # ).order_by('employee__employee_employedailyschedule__date')            
        context = self.context
        try:
            context['income_type'] = EmployeeProfessionalInfo.objects.get(employee=obj).income_type
        except:
            context['income_type'] = None
        return WorkingSchedulePayrollSerializer(schedule, many = True,context=context).data
    
    def get_sallaryslip(self, obj):
        sallary =  SallarySlipPayrol.objects.filter(employee= obj )            
        return SallarySlipPayrol_EmployeSerializers(sallary, many = True,context=self.context).data
    
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return None
    
    
    class Meta:
        model = Employee
        fields = ['id', 'employee_id','is_active','full_name','image','location','sallaryslip',
                  'schedule','created_at', 'income_type', 'salary', 'total_earning', 'total_hours']
        

class Payroll_Working_device_attendence_ScheduleSerializer(serializers.ModelSerializer):    
    schedule =  serializers.SerializerMethodField(read_only=True)    
    
    def get_schedule(self, obj):
        range_start = self.context["range_start"]
        range_end = self.context["range_end"]
        
        if range_start:
            range_start = datetime.strptime(range_start, "%Y-%m-%d")#.date()
            range_end = datetime.strptime(range_end, "%Y-%m-%d")#.date()
        else:
            import calendar
            current_date = datetime.now()#.date()
            month = current_date.month
            year = current_date.year

            current_month_days = calendar.monthrange(year, month)[1]

            range_start = f'{year}-{month}-01'
            range_end = f'{year}-{month}-{current_month_days}'
        
        #return f'range_start{range_start} range_end{range_end}' 
        schedule =  EmployeDailySchedule.objects.filter(
            employee = obj, 
            date__range =  (range_start, range_end) ,
            is_vacation = False
            # created_at__gte =  range_start ,
            # created_at__lte = range_end
            ) 
                   
        return WorkingSchedulePayrollSerializer(schedule, many = True,context=self.context).data
    
    class Meta:
        model = Employee
        fields = ['id', 'employee_id','is_active','full_name',
                  'schedule','created_at',]
class Payroll_Working_deviceScheduleSerializer(serializers.ModelSerializer):    
    schedule =  serializers.SerializerMethodField(read_only=True)    
    image = serializers.SerializerMethodField()
    income_type = serializers.SerializerMethodField(read_only=True)
    salary = serializers.SerializerMethodField(read_only=True)
    #employe_id = serializers.SerializerMethodField(read_only=True)
    
    location = serializers.SerializerMethodField(read_only=True)
    working_day = serializers.SerializerMethodField(read_only=True)
    off_day = serializers.SerializerMethodField(read_only=True)
    
    def get_location(self, obj):
        loc = obj.location.all()
        return LocationSerializer(loc, many =True ).data
    
    def get_salary(self, obj):        
        try:
            income_info = EmployeeProfessionalInfo.objects.get(employee=obj)
            return income_info.salary 
        except: 
            return None
        
    def get_income_type(self, obj):
        try:
            income_info = EmployeeProfessionalInfo.objects.get(employee=obj)
            return income_info.income_type 
        except: 
            return None

    def get_schedule(self, obj):
        total_price = 0
        schedule =  EmployeDailySchedule.objects.filter(employee= obj )#.values_list('field1', flat=True)            
        return WorkingSchedulePayrollSerializer(schedule, many = True,context=self.context).data
        # for dt in serializer:
        #     total_price += int(dt['total_hours'])
        # return total_price
        
    def get_working_day(self, obj):
        range_start = self.context["range_start"]
        range_end = self.context["range_end"]
        total = 0
        
        if range_start:
            range_start = datetime.strptime(range_start, "%Y-%m-%d").date()
            range_end = datetime.strptime(range_end, "%Y-%m-%d").date()
        else:
            range_end = datetime.now().date()
            month = range_end.month
            year = range_end.year
            range_start = f'{year}-{month}-01'
            range_start = datetime.strptime(range_start, "%Y-%m-%d").date()
            
        schedule =  EmployeDailySchedule.objects.filter(employee= obj, is_vacation = False )
        for dt in schedule:
            create = str(dt.created_at)
            created_at = datetime.strptime(create, "%Y-%m-%d %H:%M:%S.%f%z").date()
            if created_at >= range_start  and created_at <= range_end:
                total += 1
        return total
    
    def get_off_day(self, obj):
        range_start = self.context["range_start"]
        range_end = self.context["range_end"]
        total = 0
        
        if range_start:
            range_start = datetime.strptime(range_start, "%Y-%m-%d").date()
            range_end = datetime.strptime(range_end, "%Y-%m-%d").date()
        else:
            range_end = datetime.now().date()
            month = range_end.month
            year = range_end.year
            range_start = f'{year}-{month}-01'
            range_start = datetime.strptime(range_start, "%Y-%m-%d").date()
        schedule =  EmployeDailySchedule.objects.filter(employee= obj, is_vacation = True )
        for dt in schedule:
            create = str(dt.created_at)
            created_at = datetime.strptime(create, "%Y-%m-%d %H:%M:%S.%f%z").date()
            if created_at >= range_start  and created_at <= range_end:
                total += 1
        return total
    
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return None
    
    
    class Meta:
        model = Employee
        fields = ['id', 'employee_id','is_active','full_name','image','location','working_day','off_day',
                  'schedule','created_at', 'income_type', 'salary']

class UserEmployeeSerializer(serializers.ModelSerializer): 
    access_token = serializers.SerializerMethodField()
    domain = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()
    
    def get_domain(self,obj):
        try:
            tenant = self.context["tenant"]
            user_domain = Tenant.objects.get(
                id = tenant.id ,
                is_deleted=False,
                is_blocked=False,
                is_active=True
            )
            return user_domain.domain
        except Exception as err:
            return str(err)
        
    def get_access_token(self,obj):
        try:
            token = self.context["token"]
            return token
        except Exception as err:
            return str(err)
        
    def get_employee(self, obj):
        try:
            tenant = self.context["tenant"]
            with tenant_context(tenant):
                employee = Employee.objects.get(
                    #id = 'd35183df-02e4-495e-9b33-976fe16d61fe',
                    email__icontains = obj.email,
                )
                return EmployeeInformationSerializer(employee, context=self.context).data
        except Exception as err:
            return f'{str(obj.email)} {str(err)}'
        
    
    class Meta:
        model = User
        fields = ['id', 'access_token', 'domain','employee',]


class NewScheduleSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = EmployeDailySchedule
        fields = ('id', 'from_date', 'to_date',)

class NewVacationSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField(read_only=True)
    vacation_details = serializers.SerializerMethodField(read_only=True)
    
    def get_employee(self, obj):
        try:
            data = Employee.objects.get(id=str(obj.employee.id))
            return EmployeeNameSerializer(data, context=self.context).data
        except Exception as err:
            print(err)
    
    def get_vacation_details(self, obj):
        vacation = EmployeDailySchedule.objects.filter(vacation = obj, is_vacation = True )
        return NewScheduleSerializer(vacation, many = True,context=self.context).data

    class Meta:
        model = Vacation
        fields = ('id', 'employee', 'from_date', 'to_date', 'vacation_details',)
    
    
class NewAbsenceSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField(read_only=True)
    absence_details = serializers.SerializerMethodField(read_only=True)
    
    def get_employee(self, obj):
        try:
            data = Employee.objects.get(id=str(obj.employee.id))
            return EmployeeNameSerializer(data, context=self.context).data
        except Exception as err:
            print(err)
    
    def get_absence_details(self, obj):
        vacation = EmployeDailySchedule.objects.filter(vacation = obj, is_leave = True )
        return NewScheduleSerializer(vacation, many = True,context=self.context).data

    class Meta:
        model = Vacation
        fields = ('id', 'employee', 'from_date', 'to_date', 'absence_details','holiday_type')


class EmplooyeeAppointmentInsightsSerializer(serializers.ModelSerializer):
    appointments_done = serializers.IntegerField() #annotated field from manager
    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'appointments_done']


class EmployeeDailyInsightSerializer(serializers.ModelSerializer):

    # annotated fields
    morning_count = serializers.IntegerField()
    afternoon_count = serializers.IntegerField()
    evening_count = serializers.IntegerField()
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return None

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'image', 'morning_count', 'afternoon_count', 'evening_count']
