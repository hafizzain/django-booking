from pkgutil import read_code
from pyexpat import model
from re import A
from rest_framework import serializers
from Appointment.models import Appointment, AppointmentService
from Client.serializers import ClientAppointmentSerializer
from Employee.models import Employee
from Service.models import Service
from datetime import datetime, timedelta
from Product.Constants.index import tenant_media_base_url


from Utility.Constants.Data.Durations import DURATION_CHOICES_DATA

class UpdateAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentService
        fields = '__all__'


class ServiceAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name', 'price')

class EmployeAppoinmentSerializer(serializers.ModelSerializer):
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
    
    class Meta:
        model = Employee
        fields = ('id', 'full_name', 'image')
        
class TodayAppoinmentSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField(read_only=True)
    service = serializers.SerializerMethodField(read_only=True)
    end_time = serializers.SerializerMethodField(read_only=True)
    
    def get_member(self, obj):
        try: 
            return obj.member.full_name
        except Exception as err:
            None
    def get_service(self, obj):
        try:
            return obj.service.name
        except Exception as err:
            None
    
    def get_end_time(self, obj):
        app_date_time = f'2000-01-01 {obj.appointment_time}'

        try:
            duration = DURATION_CHOICES_DATA[obj.duration]
            app_date_time = datetime.fromisoformat(app_date_time)
            datetime_duration = app_date_time + timedelta(minutes=duration)
            datetime_duration = datetime_duration.strftime('%H:%M:%S')
            return datetime_duration
        except Exception as err:
            print(err)
            return None
    class Meta:
        model = AppointmentService
        fields = ('id', 'appointment_time', 'appointment_date', 'member' , 'service', 'end_time' )
        
class AppointmentServiceSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    service = serializers.SerializerMethodField(read_only=True)
    appointment_id= serializers.SerializerMethodField(read_only=True)
    client_type= serializers.SerializerMethodField(read_only=True)
    end_time = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    currency = serializers.SerializerMethodField(read_only=True)

    def get_currency(self, obj):
        return 'AED'
    
    def get_price(self, obj):
        try:
            return obj.service.price
        except Exception as err:
            None
        
    def get_end_time(self, obj):
        app_date_time = f'2000-01-01 {obj.appointment_time}'

        try:
            duration = DURATION_CHOICES_DATA[obj.duration]
            app_date_time = datetime.fromisoformat(app_date_time)
            datetime_duration = app_date_time + timedelta(minutes=duration)
            datetime_duration = datetime_duration.strftime('%H:%M:%S')
            return datetime_duration
        except Exception as err:
            return None
    
    def get_client_type(self, obj):
        try:
            return obj.appointment.client_type
        except Exception as err:
            None
    
    def get_appointment_id(self, obj):
        try:
            return obj.appointment.id
        except Exception as err:
            None
    
    def get_service(self, obj):
        try:
            return ServiceAppointmentSerializer(obj.service).data
        except Exception:
            return None
    
    def get_client(self, obj):
        if obj.appointment and obj.appointment.client:
            return ClientAppointmentSerializer(obj.appointment.client).data
        else:
            return None
    
    class Meta:
        model = AppointmentService
        fields =['id','appointment_id','appointment_date','appointment_status', 'price','appointment_time', 'end_time','client_type','duration', 'currency','created_at','service', 'client']

class AppoinmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'
        
class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentService
        fields = '__all__'


class EmployeeAppointmentSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    appointments = serializers.SerializerMethodField()

    def get_appointment_id(self, obj):
        return None

    def get_appointments(self, obj):
        appoint_services = AppointmentService.objects.filter(
            member=obj,
            is_active = True,
            is_deleted = False,
            is_blocked = False
        ).values_list('id','appointment_time', 'duration', 'appointment_date')
        selected_ids = {}

        for appoint in appoint_services:
            app_time = appoint[1]
            app_duration = appoint[2]
            app_date = appoint[3]
            
            app_date_time = f'2000-01-01 {app_time}'

            duration = DURATION_CHOICES_DATA[app_duration]
            app_date_time = datetime.fromisoformat(app_date_time)
            datetime_duration = app_date_time + timedelta(minutes=duration)
            datetime_duration = datetime_duration.strftime('%H:%M:%S')
            c_end_time = datetime_duration # Calculated End Time

            current_time = selected_ids.get(app_time , None)
            if current_time is None:
                selected_ids[app_time] = []
            selected_ids[app_time].append(str(appoint[0]))
            
           #d = datetime.strptime("20.12.2016 09:38:42,76", "%d.%m.%Y %H:%M:%S,%f").strftime('%s.%f')
            # d = datetime.strptime(f{app_date} {app_time} , "%Y.%m.%d %H:%M:%S,%f").strftime('%s.%f')
            # d_in_ms = int(float(d)*1000)
            # print(app_date)
            print(c_end_time)
            
            print(app_time)
            #if app_time 


        returned_list = []
        for selected_time in selected_ids.values():
            loop_return = []
            for id_ in selected_time:
                app_service = AppointmentService.objects.get(id=id_)
                serialized_service = AppointmentServiceSerializer(app_service)
                loop_return.append(serialized_service.data)
            
            returned_list.append(loop_return)
            
        # serialized = AppointmentServiceSerializer(appoint_services, many=True)
        # returned_list.append(serialized.data)
        return returned_list

# {
#     'time' : ['id' , 'id'],
#     'diff' : ['id' , 'id'],
# }

    def get_employee(self, obj):
        try:
            return EmployeAppoinmentSerializer(obj, context=self.context ).data
        except:
            return None

    class Meta:
        model = Employee
        fields = [
            'employee',
            'appointments',
        ]

class AllAppoinmentSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField(read_only=True)
    service = serializers.SerializerMethodField(read_only=True)
    client = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    
    def get_client(self, obj):
        return obj.appointment.client.full_name
    
    def get_member(self, obj):
        return obj.member.full_name

    def get_service(self, obj):
        return obj.service.name
            
    def get_price(self, obj):
        return obj.service.price
    
    class Meta:
        model = AppointmentService
        fields= ('id', 'service', 'member', 'price', 'client')
        
class SingleAppointmentSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    end_time = serializers.SerializerMethodField(read_only=True)
    location =  serializers.SerializerMethodField(read_only=True)
    service = ServiceAppointmentSerializer()
    currency = serializers.SerializerMethodField(read_only=True)
    booked_by = serializers.SerializerMethodField(read_only=True)
    client_type = serializers.SerializerMethodField(read_only=True)
    booking_id = serializers.SerializerMethodField(read_only=True)

    def get_booked_by(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'
    
    def get_booking_id(self, obj):
        id = str(obj.id).split('-')[0:2]
        id = ''.join(id)
        return id
    
    def get_client_type(self, obj):
        try:
            return obj.appointment.client_type
        except Exception :
            None
    
    def get_currency(self, obj):
        return 'AED'
    
    def get_location(self, obj):
        try:
            return obj.business_address.address_name
        except Exception as err:
            None
    
    def get_client(self, obj):
        return obj.appointment.client.full_name
    
    def get_end_time(self, obj):
        app_date_time = f'2000-01-01 {obj.appointment_time}'

        try:
            duration = DURATION_CHOICES_DATA[obj.duration]
            app_date_time = datetime.fromisoformat(app_date_time)
            datetime_duration = app_date_time + timedelta(minutes=duration)
            datetime_duration = datetime_duration.strftime('%H:%M:%S')
            return datetime_duration
        except Exception as err:
            return None
    
        
    class Meta:
        model = AppointmentService
        fields= ('id', 'location','client','service',
                 'appointment_time', 'end_time',
                 'appointment_status', 'currency', 'booked_by', 'booking_id', 'appointment_date', 'client_type'
            )