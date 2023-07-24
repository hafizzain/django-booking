from dataclasses import field
from getopt import error
from pkgutil import read_code
from pyexpat import model
from re import A
from Client.models import Client
#from Sale.serializers import LocationServiceSerializer
from rest_framework import serializers
from Appointment.Constants.durationchoice import DURATION_CHOICES
from Appointment.models import Appointment, AppointmentCheckout, AppointmentNotes, AppointmentService, AppointmentLogs, LogDetails, AppointmentEmployeeTip
from Business.models import BusinessAddress
from Business.serializers.v1_serializers import BusiessAddressAppointmentSerializer
from Client.serializers import ClientAppointmentSerializer
from Employee.models import Employee, EmployeeProfessionalInfo, EmployeeSelectedService, EmployeDailySchedule
from Service.models import PriceService, Service
from datetime import datetime, timedelta
from Product.Constants.index import tenant_media_base_url
from django.db.models import Q, F
from Business.serializers.v1_serializers import CurrencySerializer
from Client.serializers import ClientSerializer


from Utility.Constants.Data.Durations import DURATION_CHOICES_DATA
from Utility.models import ExceptionRecord

class PriceServiceSaleSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer()
    
    class Meta:
        model = PriceService
        fields = ['id','service', 'duration', 'price', 'currency']

class MemberSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'full_name']
class ServiceSaleSerializer(serializers.ModelSerializer):
    price_service = serializers.SerializerMethodField(read_only=True)
    
    def get_price_service(self, obj):
        price = PriceService.objects.filter(service = str(obj)).order_by('-created_at')
        return PriceServiceSaleSerializer(price, many = True).data
    class Meta:
        model = Service
        fields = ['id', 'name', 'price_service', 'arabic_name']

class UpdateAppointmentSerializer(serializers.ModelSerializer):
    service_name  = serializers.SerializerMethodField(read_only=True)
    service_arabic_name  = serializers.SerializerMethodField(read_only=True)
    
    def get_service_name(self, obj):
        try:
            cli = f"{obj.service.name}"
            return cli

        except Exception as err:
            print(err)

    def get_service_arabic_name(self, obj):
        try:
            cli = f"{obj.service.arabic_name}"
            return cli

        except Exception as err:
            print(err)

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
        fields = ('id', 'name', 'price', 'arabic_name')

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
        fields = ('id', 'appointment_time', 'appointment_date','duration',
                  'member' , 'service', 'end_time', 'location', 'appointment' )
        
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
        'price','total_price', 'discount_price',
        'appointment_time', 
        'end_time','is_favourite',
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
    unavailable_time = serializers.SerializerMethodField()

    def get_appointment_id(self, obj):
        return None
    

    def get_unavailable_time(self, employee_instance):
        return self.retreive_unavailable_time(employee_instance)

    def retreive_unavailable_time(self, employee_instance):
        errors = []
        selected_date = self.context.get('selected_date', None)
        if not selected_date:
            return []


        data = []

        exluded_times = []
        try:
            employee_working_schedule = EmployeDailySchedule.objects.get(
                employee = employee_instance,
                date = selected_date,
            )
            if employee_working_schedule.is_leave :
                raise Exception('Employee on Leave')
            
            if employee_working_schedule.is_vacation :
                raise Exception('Employee on Vacation')
            
        except Exception as err:
            errors.append(str(err))
            exluded_times.append({
                'start_time' : "00:00:00",
                'end_time' : "00:00:00",
            })
        else:
            first_shift = [employee_working_schedule.start_time, employee_working_schedule.end_time]
            second_shift = [employee_working_schedule.start_time_shift, employee_working_schedule.end_time_shift] if employee_working_schedule.start_time_shift else None

            if not first_shift[0] or not first_shift[1]:
                return []

            if employee_working_schedule.start_time.strftime('%H:%M:%S') == "00:00:00":
                if employee_working_schedule.end_time.strftime('%H:%M:%S') == '00:00:00':
                    pass
                else:
                    start_time = employee_working_schedule.end_time.strftime('%H:%M:%S')
                    end_time = "00:00:00"
                    if employee_working_schedule.start_time_shift:
                        end_time = None

                        if employee_working_schedule.end_time.strftime('%H:%M:%S') == employee_working_schedule.start_time_shift.strftime('%H:%M:%S'):
                            if employee_working_schedule.end_time_shift.strftime('%H:%M:%S') == "00:00:00":
                                start_time = None
                                end_time = None
                            else:
                                start_time = employee_working_schedule.end_time_shift.strftime('%H:%M:%S')
                                end_time = '00:00:00'

                    if start_time and end_time:
                        exluded_times.append({
                            'start_time' : start_time,
                            'end_time' : end_time,
                        })
            else:
                start_time = "00:00:00"
                end_time = employee_working_schedule.start_time.strftime('%H:%M:%S')
                exluded_times.append({
                    'start_time' : start_time,
                    'end_time' : end_time,
                })

                start_time = employee_working_schedule.end_time.strftime('%H:%M:%S')
                end_time = None

                if employee_working_schedule.end_time_shift:
                    if employee_working_schedule.end_time.strftime('%H:%M:%S') == employee_working_schedule.start_time_shift.strftime('%H:%M:%S'):
                        start_time = None
                        end_time = None
                        if employee_working_schedule.end_time_shift.strftime('%H:%M:%S') == "00:00:00":
                            pass
                        else:
                            start_time = employee_working_schedule.end_time_shift.strftime('%H:%M:%S')
                            end_time = "00:00:00"
                            exluded_times.append({
                                'start_time' : start_time,
                                'end_time' : end_time,
                            })
                    else:
                        end_time = employee_working_schedule.start_time_shift.strftime('%H:%M:%S')
                        exluded_times.append({
                            'start_time' : start_time,
                            'end_time' : end_time,
                        })
                        start_time = None
                        end_time = None

                        if employee_working_schedule.end_time_shift.strftime('%H:%M:%S') == "00:00:00":
                            pass
                        else:
                            start_time = employee_working_schedule.end_time_shift.strftime('%H:%M:%S')
                            end_time = "00:00:00"
                            exluded_times.append({
                                'start_time' : start_time,
                                'end_time' : end_time,
                            })
                else:
                    end_time = "00:00:00"
                    exluded_times.append({
                        'start_time' : start_time,
                        'end_time' : end_time,
                    })
                    
        for exl_time in exluded_times:
            start_time = exl_time['start_time']
            end_time = exl_time['end_time']
            if start_time and end_time:
                start_time_f = datetime.strptime(start_time, '%H:%M:%S')
                end_time_f = datetime.strptime( '23:59:59' if end_time == '00:00:00' else end_time, '%H:%M:%S')

                difference = end_time_f - start_time_f
                seconds = difference.seconds
                minutes = seconds // 60
                hours = minutes // 60
                remaining_minutes = minutes % 60
                
                remaining_time = remaining_minutes // 5
                remaining_time = remaining_time * 5

                # remianing_time_less_than_five = remaining_minutes % 5
                # if remianing_time_less_than_five > 2:
                #     remianing_time = remianing_time + 5

                



                

                data.append([
                    {
                        "appointment_id": "51479f52-7943-44d1-b3b5-12e0125ca307",
                        "appointment_date": selected_date,
                        "appointment_time": start_time,
                        "end_time": end_time,
                        # 'difference' : f'{difference}min',
                        # "duration": "35min",
                        "duration": f'{hours}h {remaining_time}min',
                        "created_at": "2023-05-29T06:45:38.035196Z",
                        "is_blocked": True,
                        "is_unavailable": True,
                        'errors' : errors,
                        'exluded_times' : exluded_times
                    }
                ])
        return data




        # single_data = {
        #     "id": "51479f52-7943-44d1-b3b5-12e0125ca307",
        #     "appointment_id": "51479f52-7943-44d1-b3b5-12e0125ca307",
        #     "appointment_date": "2023-05-29",
        #     "appointment_time": "00:00:00",
        #     "end_time": "00:00:00",
        #     "duration": "35min",
        #     "created_at": "2023-05-29T06:45:38.035196Z",
        #     "is_blocked": True,
        # }

        # data.append(single_data)
        return data
    

# "appointment_status": "Appointment Booked",
# "price": 0,
# "total_price": 0,
# "discount_price": 0,
# "is_favourite": false,
# "client_type": null,
# "currency": "AED",
# "service": {
#     "name": "",
#     "price": null
# },
# "client": null,
# "location": null,
# "details": "asdf"


    def get_appointments(self, obj):
        selected_date = self.context.get('selected_date', None)
        if not selected_date:
            return []
        excluded_list = ['Cancel']
        appoint_services = AppointmentService.objects.filter(
            member=obj,
            is_active = True,
            is_deleted = False,
            #is_blocked = False
            appointment_date = selected_date
        ).exclude(appointment_status__in=excluded_list).distinct()
        
        
        try:
            # sort the appointments by start time
            sorted_appointments = sorted(appoint_services, key=lambda a: a.appointment_time)

            selected_data = []
            for appointment in sorted_appointments:
                app_id = appointment.id
                appointment_time = appointment.appointment_time
                app_duration = appointment.duration
                app_date = appointment.appointment_date
                app_date_time = datetime.combine(app_date, appointment_time)

                # calculate the end time
                duration = DURATION_CHOICES[app_duration.lower()]
                end_time = (app_date_time + timedelta(minutes=duration)).time()

                # check for overlaps
                overlap = False
                for data in selected_data:
                    if data['date'] == app_date:
                        if appointment_time < data['range_end'] and end_time > data['range_start']:
                            overlap = True
                            data['ids'].append(app_id)
                            data['range_start'] = min(data['range_start'], appointment_time)
                            data['range_end'] = max(data['range_end'], end_time)
                            break

                # add a new entry if there is no overlap
                if not overlap:
                    selected_data.append({
                        'date': app_date,
                        'range_start': appointment_time,
                        'range_end': end_time,
                        'ids': [app_id]
                    })

            # serialize the data
            returned_list = []
            for data in selected_data:
                loop_return = []
                for id in data['ids']:
                    app_service = AppointmentService.objects.get(id=id)
                    serialized_service = AppointmentServiceSerializer(app_service)
                    loop_return.append(serialized_service.data)
                returned_list.append(loop_return)

            returned_list.extend(self.retreive_unavailable_time(obj))
            return returned_list

        except Exception as err:
            ExceptionRecord.objects.create(
                text=f'errors happen on appointment {str(err)}'
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
            'unavailable_time',
            'appointments',
        ]

class AllAppoinmentSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField(read_only=True)
    member_id = serializers.SerializerMethodField(read_only=True)
    service = serializers.SerializerMethodField(read_only=True)
    service_id = serializers.SerializerMethodField(read_only=True)
    client = serializers.SerializerMethodField(read_only=True)
    #price = serializers.SerializerMethodField(read_only=True)
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
        
    def get_member_id(self, obj):
        try:
            return obj.member.id
        except Exception as err:
            return None
        
    def get_service(self, obj):
        try:
            return obj.service.name
        except Exception as err:
            return None
        
    def get_service_id(self, obj):
        try:
            return obj.service.id
        except Exception as err:
            return None
            
    # def get_price(self, obj):
    #     try:
    #         return obj.service.price
    #     except Exception as err:
    #         return None
    
    class Meta:
        model = AppointmentService
        fields= ('id', 'service', 'member', 'price', 'client', 
                 'appointment_date', 'appointment_time', 'duration','member_id',
                 'booked_by' , 'booking_id', 'appointment_type','client_can_book','slot_availible_for_online','service_id',
                 'appointment_status', 'location', 'created_at')
class AllAppoinment_EmployeeSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(read_only=True)
    #price = serializers.SerializerMethodField(read_only=True)
    booked_by = serializers.SerializerMethodField(read_only=True)
    booking_id = serializers.SerializerMethodField(read_only=True)
    appointment_type = serializers.SerializerMethodField(read_only=True)
    appointment_status = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    srv_name = serializers.SerializerMethodField(read_only=True)
    employee_list = serializers.SerializerMethodField(read_only=True)
    designation = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    appointment_service_member = serializers.SerializerMethodField(read_only=True)

    
    def get_appointment_service_member(self, obj):   
        if obj.member:

            try:
                employee_service = EmployeeSelectedService.objects.get(
                    service = obj.service,
                    employee = obj.member
                )
            except:
                level = 'Average'
            else:
                level = employee_service.level

            return {
                'id' : f'{obj.member.id}',
                'full_name' : f'{obj.member.full_name}',
                'level' : f'{level}',
            }
        return {}

    def get_designation(self, obj):        
        try:
            designation = EmployeeProfessionalInfo.objects.get(employee=obj.member.id)
            return designation.designation 
        except: 
            return None
    
    def get_employee_list(self,obj):
        Employee =  EmployeeSelectedService.objects.filter(service = obj.service.id)
        return ServiceEmployeeSerializer(Employee, many = True).data
    
    def get_service(self, obj):
        try:
            return obj.service.name
        except Exception as err:
            return None
    
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
    def get_status(self, obj):
        return obj.appointment_status
    
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
        
    def get_member_id(self, obj):
        try:
            return obj.member.id
        except Exception as err:
            return None
        
    def get_srv_name(self, obj):
        try:
            return obj.service.name
        except Exception as err:
            return None
        
    def get_service_id(self, obj):
        try:
            return obj.service.id
        except Exception as err:
            return None
            
    # def get_price(self, obj):
    #     try:
    #         return obj.service.price
    #     except Exception as err:
    #         return None
    
    class Meta:
        model = AppointmentService
        fields= ('id', 'service', 'member', 'price', 'client', 'designation',
                 'appointment_date', 'appointment_time', 'duration','srv_name','status',
                 'booked_by' , 'booking_id', 'appointment_type','client_can_book','slot_availible_for_online',
                 'appointment_status', 'location','employee_list', 'created_at', 'is_deleted', 'appointment_service_member')
        
      
class SingleAppointmentSerializer(serializers.ModelSerializer):
    client_id = serializers.SerializerMethodField(read_only=True)
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
    def get_client_id(self, obj):
        try:
            return obj.appointment.client.id
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
        fields= ('id', 'location','client','client_id','service',
                 'appointment_time', 'end_time', 'member','price',
                 'appointment_status', 'currency', 'booked_by', 'booking_id', 'appointment_date', 'client_type', 'duration' , 'notes', 'is_favourite'
            )
        

class NoteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AppointmentNotes
        fields = '__all__'
    

class SingleNoteSerializer(serializers.ModelSerializer):
    
    notes = serializers.SerializerMethodField(read_only=True)
    client = ClientSerializer()
    customer_note = serializers.SerializerMethodField(read_only=True)
    appointmnet_service = serializers.SerializerMethodField(read_only=True)
    appointment_tips = serializers.SerializerMethodField(read_only=True)

    def get_appointment_tips(self, obj):
        tips = AppointmentEmployeeTip.objects.filter(
            appointment = obj
        ).annotate(
            member_name = F('member__full_name')
        ).values('member_name', 'tip')
        return list(tips)
    
    def get_customer_note(self, obj):
        try:
            note = Client.objects.get(id=obj.client)
            return note.customer_note
            #serializers = NoteSerializer(note)
        except:
            return None
        
    def get_notes(self, obj):
        try:
            note = AppointmentNotes.objects.get(appointment=obj)
            serializers = NoteSerializer(note)
            return serializers.data
        except:
            return None
        
    def get_appointmnet_service(self, obj):
            note = AppointmentService.objects.filter(appointment=obj)
            return AllAppoinment_EmployeeSerializer(note, many = True).data
            #return serializers
    class Meta:
        model = Appointment
        fields = ['id', 'client', 'appointment_tips', 'notes', 'business_address','client_type','appointmnet_service', 'customer_note']
  
class AppointmentServiceSeriailzer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentService
        fields = 'appointment_status', 
        
class ServiceClientSaleSerializer(serializers.ModelSerializer):
    service = serializers.SerializerMethodField(read_only=True)
    booked_by = serializers.SerializerMethodField(read_only=True)
    member = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    
    def get_location(self, obj):
        try:
            app_location = BusinessAddress.objects.get(id=obj.business_address.id)
            return BusiessAddressAppointmentSerializer(app_location).data
        except Exception as err:
            None
        
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
        fields = ['id','service', 'created_at','booked_by','duration','location',
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
    employee_name = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    
    def get_location(self, obj):
        try:
            all_location = obj.employee.location.all()
            return LocationSerializer(all_location, many = True).data
        except Exception as err:
            return str(err)
            None
    
    def get_employee_name(self, obj):
        try:
            emp = Employee.objects.get(id  = obj.employee.id)
            return emp.full_name
        except Exception as err:
            return str(err)   
    class Meta:
        model = EmployeeSelectedService
        fields = ('id','employee','employee_name', 'location')



# class AppointmenttLogSerializer(serializers.ModelSerializer):
#     # booking_id = serializers.SerializerMethodField(read_only=True)
#     # log_type = serializers.SerializerMethodField(read_only=True)
#     logged_by = serializers.SerializerMethodField(read_only=True)
#     # date_time = serializers.SerializerMethodField(read_only=True)
#     # log_field = serializers.SerializerMethodField(read_only=True)
#     # services = serializers.SerializerMethodField(read_only=True)
#     # time = serializers.SerializerMethodField(read_only=True)
#     # assigned_staff = serializers.SerializerMethodField(read_only=True)
#     location = serializers.SerializerMethodField(read_only=True)
#     log_details = serializers.SerializerMethodField(read_only=True)
#     # booked_by = serializers.SerializerMethodField(read_only=True)
#     def get_location(self, obj):
#         try:
#             loc = BusinessAddress.objects.get(id = obj.business_address.id)
#             return LocationSerializer(loc).data
#         except Exception as err:
#             print(err)
            
    

#     # def get_booked_by(self, obj):
#     #     return f'{obj.user.first_name} {obj.user.last_name}'

#     # def get_booking_id(self, obj):
#     #     id = str(obj.id).split('-')[0:2]
#     #     id = ''.join(id)
#     #     return id
    
#     # def get_log_type(self, obj):
#     #     try:
#     #         return obj.appointment.client_type
#     #     except Exception as err:
#     #         return None
    
#     def get_logged_by(self, obj):
#         try:
#             return obj.employee.full_name
#         except Exception as err:
#             return str(err)

#     def get_log_details(self,obj):
#         appointments = AppointmentService.objects.filter(appointment = obj.appointment)

#         output = []
#         for appointment in appointments:
#             service = {
#                 'service' : appointment.service.name,
#                 'duration':appointment.duration,
#                 'start_time':appointment.created_at,
#                 'assigned_staff':appointment.member.full_name,
#                 }
#             output.append(service)
#         return output
    
#     # def get_services(self, obj):
#     #     try:
#     #         services = AppointmentService.objects.get(id  = obj.service.id)
#     #         return ServiceSaleSerializer(services).data
#     #     except Exception as err:
#     #         print(err)

#     # def get_assigned_staff(self, obj):
#     #     try:
#     #         emp = Employee.objects.get(id  = obj.employee.id)
#     #         return emp.full_name
#     #     except Exception as err:
#     #         return str(err)
    
#     class Meta:
#         model = AppointmentLogs
#         fields = ('id','log_type','logged_by','created_at','log_details','location')

class AppointmenttLogSerializer(serializers.ModelSerializer):
    logged_by = serializers.SerializerMethodField(read_only=True)
    log_details = serializers.SerializerMethodField(read_only=True)

    
    def get_logged_by(self, obj):
        if obj.member:
            return obj.member.full_name
            
        return ''
    
    def get_log_details(self, obj):
        log_details = LogDetails.objects.filter(
            log = obj,
            is_active = True,
            is_deleted = False,
        )
        output = []
        for log_detail in log_details:
            log = {
                'service': log_detail.appointment_service.service.name,
                'duration': log_detail.duration,
                'appointment_time': log_detail.start_time,
                'assigned_staff': log_detail.member.full_name,
            }
            output.append(log)

        return output

    class Meta:
        model = AppointmentLogs
        fields = ('id', 'log_type', 'logged_by', 'log_details','created_at')
        
