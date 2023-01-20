from dataclasses import field
from getopt import error
from pkgutil import read_code
from pyexpat import model
from re import A
from rest_framework import serializers
from Appointment.Constants.durationchoice import DURATION_CHOICES
from Appointment.models import Appointment, AppointmentCheckout, AppointmentNotes, AppointmentService
from Business.models import BusinessAddress
from Business.serializers.v1_serializers import BusiessAddressAppointmentSerializer
from Client.serializers import ClientAppointmentSerializer
from Employee.models import Employee, EmployeeSelectedService
from Service.models import PriceService, Service
from datetime import datetime, timedelta
from Product.Constants.index import tenant_media_base_url
from django.db.models import Q



from Utility.Constants.Data.Durations import DURATION_CHOICES_DATA
from Utility.models import ExceptionRecord

class PriceServiceSaleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PriceService
        fields = ['id','service', 'duration', 'price']

class MemberSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'full_name']
class ServiceSaleSerializer(serializers.ModelSerializer):
    price_service = serializers.SerializerMethodField(read_only=True)
    
    def get_price_service(self, obj):
        price = PriceService.objects.filter(service = str(obj))
        return PriceServiceSaleSerializer(price, many = True).data
    class Meta:
        model = Service
        fields = ['id', 'name', 'price_service']

class UpdateAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentService
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BusinessAddress
        fields = ('id', 'address_name')

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
    location = serializers.SerializerMethodField(read_only=True)
    
    def get_location(self, obj):
        try:
            loc = BusinessAddress.objects.get(id = obj.business_address.id)
            return LocationSerializer(loc).data
        except Exception as err:
            print(err)      
    
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
        fields = ('id', 'appointment_time', 'appointment_date',
                  'member' , 'service', 'end_time', 'location' )
        
class AppointmentServiceSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    service = serializers.SerializerMethodField(read_only=True)
    appointment_id= serializers.SerializerMethodField(read_only=True)
    client_type= serializers.SerializerMethodField(read_only=True)
    end_time = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    currency = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    
    def get_location(self, obj):
        try:
            loc = BusinessAddress.objects.get(id =  str(obj.business_address) )
            return LocationSerializer(loc, ).data
           # return obj.appointment.business_address.address
        except Exception as err:
            print(err)      

    def get_currency(self, obj):
        return 'AED'
    
    def get_price(self, obj):
        try:
            return obj.price
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
        fields =['id',
        'appointment_id','appointment_date','appointment_status', 
        'price',
        'appointment_time', 
        'end_time',
        'client_type','duration', 'currency','created_at','service', 'client','location', 'is_blocked' ,'details' 
        ]

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
        excluded_list = ['Cancel', 'Done', 'Paid']
        appoint_services = AppointmentService.objects.filter(
            member=obj,
            is_active = True,
            is_deleted = False
            #is_blocked = False
        ).exclude(appointment_status__in=excluded_list)
        selected_data = []
        
        try:
            for appoint in appoint_services:
                
                app_id = appoint.id
                appointment_time = appoint.appointment_time
                app_duration = appoint.duration
                app_date = appoint.appointment_date
                
                app_date_time = f'2000-01-01 {appointment_time}'

                #duration = DURATION_CHOICES_DATA[app_duration]
                duration = DURATION_CHOICES[app_duration]
                app_date_time = datetime.fromisoformat(app_date_time)
                datetime_duration = app_date_time + timedelta(minutes=duration)
                datetime_duration = datetime_duration.strftime('%H:%M:%S')
                #second_end = datetime_duration.strftime('%H:%M:%S')
                end_time = datetime_duration # Calculated End Time

                #print(appointment_time.microsecond)
                #print(appointment_time)

                find_values = []
                new_start_time = None
                new_end_time = None

                for dt in selected_data:
                    if ((dt['range_start'] >= appointment_time and dt['range_end'] <= end_time) and dt['date'] == app_date):
                        
                        ExceptionRecord.objects.create(
                            text = f'tested successfully'
                        )
                        find_values.append(dt)
                    else:
                        new_start_time = appointment_time
                    
                    if ((dt['range_start'] <= appointment_time and dt['range_end'] >= end_time) and dt['date'] == app_date):
                        find_values.append(dt)
                    else:
                        pass

                    # if str(dt['range_end']) == str(appointment_time) and dt['date'] == app_date:
                    #     find_values.append(dt)
                    #     new_end_time = end_time
                    
                       ##OLD
                        
                    if ((dt['range_start'] == appointment_time or str(dt['range_start']) == str(end_time)) and dt['date'] == app_date):
                        find_values.append(dt)
                    else:
                        new_start_time = appointment_time
                    
                    if str(dt['range_end']) == str(end_time) and dt['date'] == app_date:
                        find_values.append(dt)
                    else:
                        # new_end_time = end_time
                        pass

                    if str(dt['range_end']) == str(appointment_time) and dt['date'] == app_date:
                        find_values.append(dt)
                        new_end_time = end_time


                if len(find_values) > 0:
                    current_obj = find_values[0]
                    if new_start_time is not None:
                        current_obj['range_start'] = new_start_time
                    if new_end_time is not None:
                        current_obj['range_end'] = new_end_time

                    current_obj['ids'].append(app_id)
                else:
                    selected_data.append({
                        'date' : app_date,
                        'range_start' : appointment_time,
                        'range_end' : end_time,
                        'ids' : [app_id]
                    })
            
            returned_list = []
            for data in selected_data:
                loop_return =[]
                for id in data['ids']:
                    app_service = AppointmentService.objects.get(id=id)
                    serialized_service = AppointmentServiceSerializer(app_service)
                    loop_return.append(serialized_service.data)
                returned_list.append(loop_return)
                

            # for selected_time in selected_ids.values():
            #     loop_return = []
            #     for id_ in selected_time:
            #         app_service = AppointmentService.objects.get(id=id_)
            #         serialized_service = AppointmentServiceSerializer(app_service)
            #         loop_return.append(serialized_service.data)
                
            #     returned_list.append(loop_return)
                
            # serialized = AppointmentServiceSerializer(appoint_services, many=True)
            # returned_list.append(serialized.data)
            return returned_list
        except Exception as err:
            ExceptionRecord.objects.create(
                text = f'errors happen on appointment {str(err)}'
            )

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
    booked_by = serializers.SerializerMethodField(read_only=True)
    booking_id = serializers.SerializerMethodField(read_only=True)
    appointment_type = serializers.SerializerMethodField(read_only=True)
    appointment_status = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    
    def get_location(self, obj):
        try:
            loc = BusinessAddress.objects.get(id = obj.business_address.id)
            return LocationSerializer(loc).data
        except Exception as err:
            print(err)      
    
    def get_appointment_status(self, obj):
        if obj.appointment_status == 'Appointment Booked' or  obj.appointment_status ==  'Arrived'  or obj.appointment_status == 'In Progress' :
            return 'Upcomming'
        
        if obj.appointment_status == 'Paid' or obj.appointment_status == 'Done': 
            return 'Completed'
        
        if obj.appointment_status == 'Cancel':
            return 'Cancelled'
            
    def get_appointment_type(self, obj):
        try:
            return obj.appointment.client_type
        except Exception as err:
            return None
            
    def get_booked_by(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'
    
    def get_booking_id(self, obj):
        id = str(obj.id).split('-')[0:2]
        id = ''.join(id)
        return id
    
    def get_client(self, obj):
        try:
            return obj.appointment.client.full_name
        except Exception as err:
            return None
        
    def get_member(self, obj):
        try:
            return obj.member.full_name
        except Exception as err:
            return None
        
    def get_service(self, obj):
        try:
            return obj.service.name
        except Exception as err:
            return None
            
    def get_price(self, obj):
        try:
            return obj.service.price
        except Exception as err:
            return None
    
    class Meta:
        model = AppointmentService
        fields= ('id', 'service', 'member', 'price', 'client', 
                 'appointment_date', 'appointment_time', 
                 'booked_by' , 'booking_id', 'appointment_type',
                 'appointment_status', 'location', 'created_at')
        
        
class SingleAppointmentSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    end_time = serializers.SerializerMethodField(read_only=True)
    location =  serializers.SerializerMethodField(read_only=True)
    service = ServiceAppointmentSerializer()
    currency = serializers.SerializerMethodField(read_only=True)
    booked_by = serializers.SerializerMethodField(read_only=True)
    client_type = serializers.SerializerMethodField(read_only=True)
    booking_id = serializers.SerializerMethodField(read_only=True)
    
    notes = serializers.SerializerMethodField(read_only=True)
    
    def get_notes(self, obj):
        try:
            note = AppointmentNotes.objects.filter(appointment=obj.appointment)
            print(note)
            serializers = NoteSerializer(note, many = True)
            return serializers.data
        except:
            return None

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
            app_location = BusinessAddress.objects.get(id=obj.business_address.id)
            return BusiessAddressAppointmentSerializer(app_location).data
        except Exception as err:
            None
    
    def get_client(self, obj):
        try:
            return obj.appointment.client.full_name
        except Exception as err:
            pass
    
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
                 'appointment_time', 'end_time', 'member','price',
                 'appointment_status', 'currency', 'booked_by', 'booking_id', 'appointment_date', 'client_type', 'duration' , 'notes', 'is_favourite'
            )
        

class NoteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AppointmentNotes
        fields = '__all__'
    

class SingleNoteSerializer(serializers.ModelSerializer):
    
    notes = serializers.SerializerMethodField(read_only=True)
    
    def get_notes(self, obj):
        try:
            note = AppointmentNotes.objects.get(appointment=obj)
            print(note)
            serializers = NoteSerializer(note)
            return serializers.data
        except:
            return None
            
    
    class Meta:
        model = Appointment
        fields = ['id', 'client', 'notes']
  
class AppointmentServiceSeriailzer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentService
        fields = 'appointment_status', 
        
class ServiceClientSaleSerializer(serializers.ModelSerializer):
    service = serializers.SerializerMethodField(read_only=True)
    booked_by = serializers.SerializerMethodField(read_only=True)
    member = serializers.SerializerMethodField(read_only=True)
    
    def get_member(self, obj):
        try:
            emp = Employee.objects.get(id  = obj.member.id)
            return MemberSaleSerializer(emp).data
        except Exception as err:
            print(err)
    
    def get_booked_by(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'
    
    def get_service(self, obj):
        try:
            price = Service.objects.get(id  = obj.service.id)
            return price.name
            #return ServiceSaleSerializer(price).data
        except Exception as err:
            print(err)
    class Meta:
        model = AppointmentService
        fields = ['id','service', 'created_at','booked_by','duration',
                  'price','appointment_status','member', 'is_favourite']
        
class CheckoutSerializer(serializers.ModelSerializer):
    appointment_service_status = serializers.SerializerMethodField(read_only=True)
    appointment_service_duration = serializers.SerializerMethodField(read_only=True)
    service = serializers.SerializerMethodField(read_only=True)
    member = serializers.SerializerMethodField(read_only=True)
    
    def get_service(self, obj):
        try:
            price = Service.objects.get(id  = obj.service.id)
            return ServiceSaleSerializer(price).data
        except Exception as err:
            print(err)
            
    def get_member(self, obj):
        try:
            emp = Employee.objects.get(id  = obj.member.id)
            return MemberSaleSerializer(emp).data
        except Exception as err:
            print(err)
    
    def get_appointment_service_status(self, obj):
        try:
            service = AppointmentService.objects.get(id = obj.appointment_service.id )
            return service.appointment_status
        except Exception as err:
            print(err)   
            
    def get_appointment_service_duration(self, obj):
        try:
            service = AppointmentService.objects.get(id = obj.appointment_service.id )
            return service.duration
        except Exception as err:
            print(err)   
    
    class Meta:
        model = AppointmentCheckout
        fields = ['id', 'appointment', 'appointment_service_status', 'service','member','created_at','appointment_service_duration',
                'payment_method','business_address', 'voucher','promotion',
                'membership','rewards','tip','gst', 'service_price', 'total_price']
        #exclude = ['id' ,'is_deleted', 'is_active']
        

class ServiceEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSelectedService
        fields = ('id','employee')