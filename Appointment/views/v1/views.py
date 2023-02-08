from django.shortcuts import render
from Appointment.Constants.ConvertTime import convert_24_to_12

from Appointment.Constants.Reschedule import reschedule_appointment
from Appointment.Constants.AddAppointment import Add_appointment
from Appointment.Constants.cancelappointment import cancel_appointment

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from rest_framework import status
from Appointment.Constants.durationchoice import DURATION_CHOICES
from Business.models import Business , BusinessAddress
from datetime import datetime
from Order.models import Checkout, MemberShipOrder, ProductOrder, VoucherOrder
from Sale.serializers import MemberShipOrderSerializer, ProductOrderSerializer, VoucherOrderSerializer

#from Service.models import Service
from Service.models import Service
from Employee.models import CategoryCommission, CommissionSchemeSetting, EmployeDailySchedule, Employee, EmployeeSelectedService
from Authentication.models import User
from NStyle.Constants import StatusCodes
import json
from django.db.models import Q
from Client.models import Client, Membership, Promotion, Rewards, Vouchers
from datetime import date, timedelta
from threading import Thread


from Appointment.models import Appointment, AppointmentService, AppointmentNotes , AppointmentCheckout
from Appointment.serializers import  CheckoutSerializer, AppoinmentSerializer, ServiceClientSaleSerializer, ServiceEmployeeSerializer,SingleAppointmentSerializer ,BlockSerializer ,AllAppoinmentSerializer, SingleNoteSerializer, TodayAppoinmentSerializer, EmployeeAppointmentSerializer, AppointmentServiceSerializer, UpdateAppointmentSerializer
from Tenants.models import ClientTenantAppDetail, Tenant
from django_tenants.utils import tenant_context
from Utility.models import ExceptionRecord
from django.db.models import Prefetch


@api_view(['GET'])
@permission_classes([AllowAny])
def get_single_appointments(request):
    appointment_id = request.GET.get('appointment_id', None) 
    
    if not all([appointment_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Appointment id is required',
                    'fields' : [
                        'appointment_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        appointment = AppointmentService.objects.get(id=appointment_id, is_blocked=False, is_deleted=False )
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_APPOINMENT_ID_4038,
                    'status_code_text' : 'INVALID_APPOINMENT_ID_4038',
                    'response' : {
                        'message' : 'Appointment Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
    serialized = SingleAppointmentSerializer(appointment)
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Single Appointment',
                'error_message' : None,
                'appointment' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_appointments_service(request):
    appointment_id = request.GET.get('appointment_group_id', None) 
    
    if not all([appointment_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Appointment id is required',
                'fields' : [
                            'appointment_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        appointment = Appointment.objects.get(id=appointment_id, is_deleted=False )
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_APPOINMENT_ID_4038,
                    'status_code_text' : 'INVALID_APPOINMENT_ID_4038',
                    'response' : {
                        'message' : 'Appointment Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
    serialized = SingleNoteSerializer(appointment)
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'All Appointments',
                'error_message' : None,
                'appointment' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_appointments_device(request):
    employee_id = request.GET.get('employee_id', None) 
    
    if not all([employee_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Employee id is required',
                'fields' : [
                            'employee_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        employee = Employee.objects.get(id = employee_id,  is_deleted=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
                    'status_code_text' : 'INVALID_EMPLOYEE_4025',
                    'response' : {
                        'message' : 'Employee Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

    
    try:
        appointment = Appointment.objects.filter(appointment_services__member = employee ).order_by('-created_at').distinct()
#appointment = Appointment.objects.filter(member = employee )
        # .prefetch_related(
        #     Prefetch('appointment_services', queryset=AppointmentService.objects.filter(member=employee))#[0]
        # )
        
    #     #prefetch_related('appointment_services')
    # except Appointment.MultipleObjectsReturned:
    #     appointment = Appointment.objects.filter(appointment_services__member = employee )
        
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_APPOINMENT_ID_4038,
                    'status_code_text' : 'INVALID_APPOINMENT_ID_4038',
                    'response' : {
                        'message' : 'Appointment Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
    serialized = SingleNoteSerializer(appointment, many = True)
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'All Appointments',
                'error_message' : None,
                'appointment' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_today_appointments(request):
    today = date.today()
    today_appointment = AppointmentService.objects.filter(appointment_date__icontains = today, is_blocked=False )
    serialize = TodayAppoinmentSerializer(today_appointment, many=True)
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Today Appointments',
                'error_message' : None,
                'appointments' : serialize.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_appointments(request):
    test = AppointmentService.objects.filter(is_blocked=False).order_by('-created_at')
    serialize = AllAppoinmentSerializer(test, many=True)
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Appointment',
                'error_message' : None,
                'appointments' : serialize.data
            }
        },
        status=status.HTTP_200_OK
    )

    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_calendar_appointment(request):
    all_memebers= Employee.objects.filter(
        is_deleted = False,
        is_active = True,
    ).order_by('-created_at')
    print(all_memebers)
    serialized = EmployeeAppointmentSerializer(all_memebers, many=True, context={'request' : request})

    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Calender Appointment',
                'error_message' : None,
                'appointments' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_appointment(request):
    user = request.user  
    business_id = request.data.get('business', None)
    appointments = request.data.get('appointments', None)
    appointment_date = request.data.get('appointment_date', None)
    text = request.data.get('appointment_notes', None)
    business_address_id = request.data.get('business_address', None)
    member = request.data.get('member', None)
    #business_id, member, appointment_date, appointment_time, duration

    client = request.data.get('client', None)
    client_type = request.data.get('client_type', None)
    
    payment_method = request.data.get('payment_method', None)
    discount_type = request.data.get('discount_type', None)    
    Errors = []
        
    if not all([ client_type, appointment_date, business_id  ]):
         return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                         # 'client',
                          'client_type',
                          'member', 
                          'appointment_date', 
                          'business',
                          'appointments', 
                        ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business=Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Business not found',
                    'error_message' : str(err),
                }
            }
    
        )

    if business_address_id is not None:
        try:
            business_address = BusinessAddress.objects.get(id=business_address_id)
        except Exception as err:
            return Response(
            {
                    'status' : False,
                    # 'error_message' : str(err),
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Business not found',
                }
            }
        )
    try:
        client = Client.objects.get(id=client)
    except Exception as err:
        client = None
       
    appointment = Appointment.objects.create(
            user = user,
            business=business,
            client=client,
            client_type=client_type,
            payment_method=payment_method,
            discount_type=discount_type,
        )
    if business_address_id is not None:
        appointment.business_address = business_address
        appointment.save()
    
    if type(appointments) == str:
        appointments = appointments.replace("'" , '"')
        appointments = json.loads(appointments)

    elif type(appointments) == list:
        pass
    if text:
        if type(text) == str:
            try:
                text = text.replace("'" , '"')
                text = json.loads(text)
            except:
                AppointmentNotes.objects.create(
                    appointment=appointment,
                    text = text
                )
        elif type(text) == list:
            pass
            for note in text:
                AppointmentNotes.objects.create(
                    appointment=appointment,
                    text = note
                )
    
    all_members = []
    for appoinmnt in appointments:
        member = appoinmnt['member']
        service = appoinmnt['service']
        app_duration = appoinmnt['duration']
        price = appoinmnt['price']
        date_time = appoinmnt['date_time']
        fav = appoinmnt.get('favourite', None)
        
        client_can_book = appoinmnt.get('client_can_book', None)
        slot_availible_for_online = appoinmnt.get('slot_availible_for_online', None)
        
        voucher_id = appoinmnt.get('voucher', None)
        reward_id = appoinmnt.get('reward', None)
        membership_id = appoinmnt.get('membership', None)
        promotion_id = appoinmnt.get('promotion', None)
        # tip = appoinmnt['tip']
        
        app_date_time = f'2000-01-01 {date_time}'
        
        duration = DURATION_CHOICES[app_duration]
        app_date_time = datetime.fromisoformat(app_date_time)
        datetime_duration = app_date_time + timedelta(minutes=duration)
        datetime_duration = datetime_duration.strftime('%H:%M:%S')
        end_time = datetime_duration
        
        service_commission = 0
        service_commission_type = ''
        toValue = 0
        
        try:
            commission = CommissionSchemeSetting.objects.get(employee = str(member))
            category = CategoryCommission.objects.filter(commission = commission.id)
            for cat in category:
                try:
                    toValue = int(cat.to_value)
                except :
                    sign  = cat.to_value
                if cat.category_comission == 'Service':
                    if (int(cat.from_value) <= price and  price <  toValue) or (int(cat.from_value) <= price and sign ):
                        if cat.symbol == '%':
                            service_commission = price * int(cat.commission_percentage) / 100
                            service_commission_type = str(service_commission_type) + cat.symbol
                        else:
                            service_commission = int(cat.commission_percentage)
                            service_commission_type = str(service_commission) + cat.symbol
                                            
        except Exception as err:
            Errors.append(str(err))
        
        try:
            voucher = Vouchers.objects.get(id = voucher_id )
        except:
            voucher = None
            
        try:
            reward = Rewards.objects.get(id = reward_id )
        except:
            reward = None
        try:
            membership = Membership.objects.get(id = membership_id )
        except:
            membership = None
        
        try:
            promotion = Promotion.objects.get(id = promotion_id )
        except:
            promotion = None
            
        try:
            member=Employee.objects.get(id=member)
            all_members.append(str(member.id))
        except Exception as err:
            return Response(
            {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
                    'response' : {
                    'message' : 'Employee not found',
                    'error_message' : str(err),
                }
            }
        )
        try:
            service=Service.objects.get(id=service)
        except Exception as err:
            return Response(
            {
                    'status' : False,
                    'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
                    'response' : {
                    'message' : 'Service not found',
                    'error_message' : str(err),
                }
            }
        )
            
        appointment_service = AppointmentService.objects.create(
            user = user,
            business = business,
            appointment = appointment,
            duration=app_duration,
            appointment_time=date_time,
            appointment_date = appointment_date,
            end_time = end_time,
            service = service,
            member = member,
            price = price,
            service_commission = service_commission,
            service_commission_type= service_commission_type,
            
            slot_availible_for_online = slot_availible_for_online,
            client_can_book = client_can_book,
            # voucher = voucher,
            # reward = reward,
            # membership = membership,
            # promotion = promotion
            # tip=tip,
        )
        if fav is not None:
            appointment_service.is_favourite = True
            appointment_service.save()
            
        if business_address_id is not None:
            appointment_service.business_address = business_address
            appointment_service.save()
    serialized = AppoinmentSerializer(appointment)
    
    try:
        thrd = Thread(target=Add_appointment, args=[], kwargs={'appointment' : appointment, 'tenant' : request.tenant})
        thrd.start()
    except Exception as err:
        ExceptionRecord.objects.create(
            text=str(err)
        )
    
    all_memebers= Employee.objects.filter(
        is_deleted = False,
        is_active = True,
        is_blocked = False,
    ).order_by('-created_at')
    serialized = EmployeeAppointmentSerializer(all_memebers, many=True, context={'request' : request})

    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Appointment Create!',
                    'error_message' : None,
                    'error' : Errors,
                    'appointments' : serialized.data,
                }
            },
            status=status.HTTP_201_CREATED
    )    
 
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_appointment(request):
    appointment_service_id = request.data.get('id', None)
    appointment_status = request.data.get('appointment_status', None)
    if appointment_service_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required.',
                    'fields' : [
                        'id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
          
    try:
        service_appointment = AppointmentService.objects.get(id=appointment_service_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Appointment ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = UpdateAppointmentSerializer(service_appointment , data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Appointment Serializer Invalid',
                'error_message' : str(serializer.errors),
            }
        },
        status=status.HTTP_404_NOT_FOUND
        )
    serializer.save()
    if appointment_status == 'Cancel':
        try:
            thrd = Thread(target=cancel_appointment, args=[] , kwargs={'appointment' : service_appointment, 'tenant' : request.tenant} )
            thrd.start()
        except Exception as err:
            print(err)
            pass
        
    else :
        try:
            thrd = Thread(target=reschedule_appointment, args=[] , kwargs={'appointment' : service_appointment, 'tenant' : request.tenant})
            thrd.start()
        except Exception as err:
            print(err)
            pass
        
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Update Appointment Successfully',
                'error_message' : None,
                'Appointment' : serializer.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_appointment_service(request):
    appointment_id = request.data.get('id', None)
    appointments = request.data.get('appointments', None)
    client_type = request.data.get('client_type', None)
    appointment_notes = request.data.get('appointment_notes', None)
    appointment_date = request.data.get('appointment_date', None)
    client = request.data.get('client', None)
    
    ExceptionRecord.objects.create(
        text = f'{request.data}'
    )
    
    errors = []
    if appointment_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required.',
                    'fields' : [
                        'id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
          
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Appointment ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    if client:
        try:
            client = Client.objects.get(id=client)
            appointment.client = client
            appointment.save()
        except Exception as err:
            client = None
        
    if client_type:
        appointment.client_type = client_type
        appointment.save()
    if appointment_notes:
        try:
            notes = AppointmentNotes.objects.filter(appointment =appointment )
            for no in notes:
                no.delete()
            notes =  AppointmentNotes.objects.create(
                appointment =appointment ,
                text = appointment_notes 
            )
        except Exception as err:
            errors.append(str(err))
            
    if appointments is not None:
        if type(appointments) == str:
            appointments = json.loads(appointments)

        elif type(appointments) == list:
            pass
        
        for app in appointments:
            appointment_date = app.get('appointment_date', None)
            date_time = app.get('date_time', None)
            service = app.get('service', None)
            client_can_book = app.get('client_can_book', None)
            slot_availible_for_online = app.get('slot_availible_for_online', None)
            duration = app.get('duration', None)
            price = app.get('price', None)
            member = app.get('member', None)
            is_deleted = app.get('is_deleted', None)
            id = app.get('id', None)
            try:
                service_id =Service.objects.get(id=service)
            except Exception as err:
                errors.append(str(err))
            try:
                member_id =Employee.objects.get(id=member)
            except Exception as err:
                errors.append(str(err))
            if id is not None:
                try:
                    service_appointment = AppointmentService.objects.get(id=str(id))
                    ExceptionRecord.objects.create(
                        text = f'{is_deleted} id {service_appointment}'
                    )
                    if str(is_deleted) == "true":
                        service_appointment.delete()
                    service_appointment.appointment_date = appointment_date
                    service_appointment.appointment_time = date_time
                    service_appointment.service = service_id
                    service_appointment.client_can_book = client_can_book
                    service_appointment.slot_availible_for_online = slot_availible_for_online
                    service_appointment.duration = duration
                    service_appointment.price = price
                    service_appointment.member = member_id
                    service_appointment.save()                    
                except Exception as err:
                    errors.append(str(err))
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Update Appointment Successfully',
                'error_message' : None,
                'errors': errors,
                #'Appointment' : serializer.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_appointment(request):
    appointment_service_id = request.data.get('id', None)

    if appointment_service_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
          
    try:
        app_service = AppointmentService.objects.get(id=appointment_service_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Appointment Service Not Found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    app_service.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Appointment Service deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_blockTime(request):
    user = request.user    
    business_id = request.data.get('business', None)
    
    date = request.data.get('date', None)
    start_time = request.data.get('start_time', None)
    duration = request.data.get('duration',None)
    
    member = request.data.get('member',None)
    details = request.data.get('details', None)
    
    if not all([business_id, date, start_time, duration , member]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                          'business_id',
                          'date',
                          'start_time', 
                          'duration', 
                          'member',
                        ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )    
    try:
        business=Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Business not found',
                    'error_message' : str(err),
                }
            }
    
        )
    try:
        member=Employee.objects.get(id=member)
    except Exception as err:
        return Response(
            {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
                    'response' : {
                    'message' : 'Employee not found',
                    'error_message' : str(err),
                }
            }
        )
    block_time = AppointmentService.objects.create(
            user = user,
            business = business,
            appointment_time=start_time,
            duration = duration, 
            appointment_date = date,
            member = member,
            details = details,
            is_blocked = True,
        )
    
    all_members =Employee.objects.filter(is_deleted=False, is_active = True).order_by('-created_at')
    
    serialized = EmployeeAppointmentSerializer(all_members, many=True, context={'request' : request})

    #serialized = BlockSerializer(block_time)
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'BlockTime Create!',
                    'error_message' : None,
                    'appointments' : serialized.data,
                }
            },
            status=status.HTTP_201_CREATED
    ) 

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_blocktime(request):
    block_id = request.data.get('id', None)
    end_time = request.data.get('end_time', None)
    start_time = request.data.get('start_time', None)
    if block_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
       
    try:
        block = AppointmentService.objects.get(id=block_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid BlockTime ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    # end = start_time + timedelta(minutes=23)
    # print(F"{end} -- {end_time}")
    serializer = UpdateAppointmentSerializer(block , data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Block Serializer Invalid',
                'error_message' : str(serializer.errors),
            }
        },
        status=status.HTTP_404_NOT_FOUND
        )
    serializer.save()
    all_members =Employee.objects.filter(is_deleted=False, is_active = True).order_by('-created_at')

    serialized = EmployeeAppointmentSerializer(all_members, many=True, context={'request' : request})
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Update BlockTime Successfully',
                'error_message' : None,
                'asset' : serialized.data
            }
        },
        status=status.HTTP_200_OK
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_block_time(request):
    block_id = request.data.get('id', None)
    if block_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
       
    try:
        block = AppointmentService.objects.get(id=block_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid BlockTime ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    block.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Delete BlockTime Successfully',
                'error_message' : None,
            }
        },
        status=status.HTTP_200_OK
        )
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout(request):
    appointment = request.data.get('appointment', None)
    appointment_service = request.data.get('appointment_service', None)
    
    payment_method = request.data.get('payment_method', None)
    service = request.data.get('service', None)
    member = request.data.get('member', None)
    business_address = request.data.get('business_address', None)
    
    tip = request.data.get('tip', None)
    gst = request.data.get('gst', None)
    service_price = request.data.get('service_price', None)
    total_price = request.data.get('total_price', None)
    
    # if not all([]){
        
    # }
    try:
        members=Employee.objects.get(id=member)
    except Exception as err:
        members = None
        # return Response(
        #     {
        #             'status' : False,
        #             'status_code' : StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
        #             'response' : {
        #             'message' : 'Employee not found',
        #             'error_message' : str(err),
        #         }
        #     },
        #     status=status.HTTP_404_NOT_FOUND
        # )
    try:
        services=Service.objects.get(id=service)
    except Exception as err:
        services = None
        # return Response(
        #     {
        #             'status' : False,
        #             'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
        #             'response' : {
        #             'message' : 'Service not found',
        #             'error_message' : str(err),
        #         }
        #     },
        #     status=status.HTTP_404_NOT_FOUND
        # )
    try:
        service_appointment = AppointmentService.objects.get(id=appointment_service)
    except Exception as err:
        service_appointment = None
        # return Response(
        #     {
        #         'status' : False,
        #         'status_code' : 404,
        #         'status_code_text' : '404',
        #         'response' : {
        #             'message' : 'Invalid Appointment ID!',
        #             'error_message' : str(err),
        #         }
        #     },
        #     status=status.HTTP_404_NOT_FOUND
        # )
    try:
        appointments = Appointment.objects.get(id=service_appointment.appointment.id)
    except Exception as err:
        appointments = None
    print(appointments)
        # return Response(
        #     {
        #         'status' : False,
        #         'status_code' : 404,
        #         'status_code_text' : '404',
        #         'response' : {
        #             'message' : 'Invalid Appointment ID!',
        #             'error_message' : str(err),
        #         }
        #     },
        #     status=status.HTTP_404_NOT_FOUND
        # )
    try:
        business_address=BusinessAddress.objects.get(id=business_address)
    except Exception as err:
        business_address = None
    
    checkout =AppointmentCheckout.objects.create(
        appointment = appointments,
        appointment_service = service_appointment,
        payment_method =payment_method,
        service= services,
        member=members,
        business_address=business_address,
        tip = tip,
        gst = gst,
        service_price =service_price,
        total_price =total_price,
        
    )
    checkout.business_address = service_appointment.business_address
    checkout.save()
    
    serialized = CheckoutSerializer(checkout)
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Appointment Checkout Created!',
                    'error_message' : None,
                    'checkout' : serialized.data,
                }
            },
            status=status.HTTP_201_CREATED
    ) 
    
@api_view(['GET'])
@permission_classes([AllowAny])
def service_appointment_count(request):
    address = request.GET.get('address', None)
    duration = request.GET.get('duration', None) 
    
    
    try:
        adds = BusinessAddress.objects.get(id = address)
    except Exception as err:
        adds = None
        print(err)
    services = Service.objects.all()
    return_data =[]
    for ser in services:
        if duration is not None:
            today = datetime.today()
            day = today - timedelta(days=int(duration))
            app_service = AppointmentService.objects.filter(service = ser, business_address =adds , created_at__gte = day )
        else:
            app_service = AppointmentService.objects.filter(service = ser, business_address =adds )
        count = app_service.count()
        data = {
            # 'id' : str(ser.id),
            'name' : str(ser.name),
            'count' : count
        }
        return_data.append(data)
    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : 'Appointment Checkout Create!',
                    'error_message' : None,
                    'data' : return_data,
                    
                }
            },
            status=status.HTTP_201_CREATED
    ) 
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_service_employee(request):
    address = request.GET.get('service', None)
    data = {}
    employee_ids = []
    if address is None :
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'address id is required',
                    'fields' : [
                        'address',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    Employee =  EmployeeSelectedService.objects.filter(service = address)
    serializer =  ServiceEmployeeSerializer(Employee, many = True)
    data =serializer.data
    for i in data:
        employee_ids.append(i['employee'])
    
    #test = data['employee']
    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : 'Appointment Checkout Create!',
                    'error_message' : None,
                    'data' : employee_ids,
                    
                }
            },
            status=status.HTTP_201_CREATED
    ) 

@api_view(['GET'])
@permission_classes([AllowAny])
def get_employees_for_selected_service(request):
    service = request.GET.get('service', None)
    if service is None :
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'service id is required',
                    'fields' : [
                        'service',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    Employee =  EmployeeSelectedService.objects.filter(service = service)
    serializer =  ServiceEmployeeSerializer(Employee, many = True)
        
    #test = data['employee']
    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : 'Employee Selected Service!',
                    'error_message' : None,
                    'data' : serializer.data,
                    
                }
            },
            status=status.HTTP_201_CREATED
    ) 
   
@api_view(['GET'])
@permission_classes([AllowAny])
def get_client_sale(request):
    client = request.GET.get('client', None)
    data = []
    employee_ids = []
    if client is None :
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'client id is required',
                    'fields' : [
                        'client',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        
    product_order = ProductOrder.objects.filter(checkout__client = client).order_by('-created_at')
    product = ProductOrderSerializer(product_order,  many=True,  context={'request' : request, })
    
    voucher_order = VoucherOrder.objects.filter(checkout__client = client).order_by('-created_at')
    voucher = VoucherOrderSerializer(voucher_order,  many=True,  context={'request' : request, })
    data.extend(voucher.data)
    
    membership_order = MemberShipOrder.objects.filter(checkout__client = client).order_by('-created_at')
    membership = MemberShipOrderSerializer(membership_order,  many=True,  context={'request' : request, })
    data.extend(membership.data)
    
    # appointment_checkout = AppointmentCheckout.objects.filter(appointment__client = client)
    # serialized = CheckoutSerializer(appointment_checkout, many = True)
    
    appointment_checkout = AppointmentService.objects.filter(appointment__client = client).order_by('-created_at')
    serialized = ServiceClientSaleSerializer(appointment_checkout, many = True)
    
    #test = checkout.count()
    #serialized = CheckoutSerializer(checkout, many = True, context = {'request' : request})
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Client Order Sales!',
                    'error_message' : None,
                    'product' : product.data,
                    'voucher' : data,
                    'appointment' : serialized.data
                }
            },
            status=status.HTTP_201_CREATED
        )
    
@api_view(['POST'])
@permission_classes([AllowAny])
def create_appointment_client(request):
    #user = request.user
    tenant_id = request.data.get('hash', None)
    business_id = request.data.get('business', None)
    appointments = request.data.get('appointments', None)
    appointment_date = request.data.get('appointment_date', None)
    text = request.data.get('appointment_notes', None)

    client = request.data.get('client', None)
    client_type = request.data.get('client_type', None)
    
    payment_method = request.data.get('payment_method', None)
    discount_type = request.data.get('discount_type', None)
    
    #if tenant_id is None:
    if not all([tenant_id , client_type, appointment_date, business_id  ]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'hash',
                        'client_type',
                        'appointment_date',
                        'business_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    
    try:
        tenant = Tenant.objects.get(id = str(tenant_id))
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'status_code_text' : 'Invalid Data',
                'response' : {
                    'message' : 'Invalid Tenant Id',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        tenant_client = ClientTenantAppDetail.objects.create(
            # user = user 
            tenant = tenant,
            client_id = client,
            is_appointment = True
        )
    except Exception as err:
        ExceptionRecord.objects.create(text = f'Tenant Created Customer error and  {str(err)}')
    
    with tenant_context(tenant):
        try:
            business=Business.objects.get(id=business_id)
        except Exception as err:
            return Response(
                {
                        'status' : False,
                        'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                        'response' : {
                        'message' : 'Business not found',
                        'error_message' : str(err),
                    }
                }
        
            )
        
        business_address_id = request.data.get('business_address', None)

        if business_address_id is not None:
            try:
                business_address = BusinessAddress.objects.get(id=business_address_id)
            except Exception as err:
                return Response(
                {
                        'status' : False,
                        # 'error_message' : str(err),
                        'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                        'response' : {
                        'message' : 'Business not found',
                    }
                }
            )
        try:
            client = Client.objects.get(id=client)
        except Exception as err:
            client = None
            # return Response(
            #     {
            #             'status' : False,
            #             'status_code' : StatusCodes.INVALID_CLIENT_4032,
            #             'response' : {
            #             'message' : 'Client not found',
            #             'error_message' : str(err),
            #         }
            #     }
            # )
        
                
        appointment = Appointment.objects.create(
                user = business.user,
                business=business,
                client=client,
                client_type='IN HOUSE',
                payment_method=payment_method,
                discount_type=discount_type,
            )
        if business_address_id is not None:
            appointment.business_address = business_address
            appointment.save()
        
        if type(appointments) == str:
            appointments = json.loads(appointments)

        elif type(appointments) == list:
            pass
        
        if type(text) == str:
            text = json.loads(text)
        else:
            pass
        if text is not None:
            for note in text:
                AppointmentNotes.objects.create(
                    appointment=appointment,
                    text = note
                )
        
        all_members = []
        for appoinmnt in appointments:
            member = appoinmnt['member']
            service = appoinmnt['service']
            app_duration = appoinmnt['duration']
            price = appoinmnt['price']
            date_time = appoinmnt['date_time']
            fav = appoinmnt.get('favourite', None)
            
            voucher_id = appoinmnt.get('voucher', None)
            reward_id = appoinmnt.get('reward', None)
            membership_id = appoinmnt.get('membership', None)
            promotion_id = appoinmnt.get('promotion', None)
            # tip = appoinmnt['tip']
            
            app_date_time = f'2000-01-01 {date_time}'
            
            duration = DURATION_CHOICES[app_duration]
            app_date_time = datetime.fromisoformat(app_date_time)
            datetime_duration = app_date_time + timedelta(minutes=duration)
            datetime_duration = datetime_duration.strftime('%H:%M:%S')
            end_time = datetime_duration
                
            try:
                member=Employee.objects.get(id=str(member))
                all_members.append(str(member.id))
            except Exception as err:
                return Response(
                {
                        'status' : False,
                        'status_code' : StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
                        'response' : {
                        'message' : 'Employee not found',
                        'error_message' : str(err),
                    }
                }
            )
            try:
                service=Service.objects.get(id=service)
            except Exception as err:
                return Response(
                {
                        'status' : False,
                        'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
                        'response' : {
                        'message' : 'Service not found',
                        'error_message' : str(err),
                    }
                }
            )
                
            appointment_service = AppointmentService.objects.create(
                user = business.user,
                business = business,
                appointment = appointment,
                duration=app_duration,
                appointment_time=date_time,
                appointment_date = appointment_date,
                end_time = end_time,
                service = service,
                member = member,
                price = price,
                # voucher = voucher,
                # reward = reward,
                # membership = membership,
                # promotion = promotion
                # tip=tip,
            )
            if fav is not None:
                appointment_service.is_favourite = True
                appointment_service.save()
                
            if business_address_id is not None:
                appointment_service.business_address = business_address
                appointment_service.save()
        serialized = AppoinmentSerializer(appointment)
        
        try:
            thrd = Thread(target=Add_appointment, args=[], kwargs={'appointment' : appointment, 'tenant' : request.tenant})
            thrd.start()
        except Exception as err:
            ExceptionRecord.objects.create(
                text=str(err)
            )
        
        all_memebers= Employee.objects.filter(
            is_deleted = False,
            is_active = True,
            is_blocked = False,
        ).order_by('-created_at')
        serialized = EmployeeAppointmentSerializer(all_memebers, many=True, context={'request' : request})

        return Response(
                {
                    'status' : True,
                    'status_code' : 201,
                    'response' : {
                        'message' : 'Appointment Create!',
                        'error_message' : None,
                        'appointments' : serialized.data,
                    }
                },
                status=status.HTTP_201_CREATED
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def get_employee_check_time(request):                  
    emp_id = request.data.get('member_id', None)
    duration = request.data.get('duration', None)
    start_time = request.data.get('app_time', None)
    date = request.data.get('date', None)
    
    dtime = datetime.strptime(start_time, "%H:%M:%S")
    start_time = dtime.time()
    
    dt = datetime.strptime(date, "%Y-%m-%d")
    date = dt.date()
    
    app_date_time = f'2000-01-01 {start_time}'

    duration = DURATION_CHOICES[duration]
    app_date_time = datetime.fromisoformat(app_date_time)
    datetime_duration = app_date_time + timedelta(minutes=duration)
    datetime_duration = datetime_duration.strftime('%H:%M:%S')
    tested = datetime.strptime(datetime_duration ,'%H:%M:%S').time()
    end_time = datetime_duration
    
    EmployeDaily = False
    data = []
        
    try:
        employee = Employee.objects.get(
                id = emp_id,
                ) 
        try:
            daily_schedule = EmployeDailySchedule.objects.get(
                employee = employee,
                is_vacation = False,
                date = date,
                )      
            if start_time >= daily_schedule.start_time and start_time < daily_schedule.end_time :
                pass
            elif daily_schedule.start_time_shift != None:
                if start_time >= daily_schedule.start_time_shift and start_time < daily_schedule.end_time_shift:
                    pass
                else:
                    st_time = convert_24_to_12(str(start_time))
                    ed_time = convert_24_to_12(str(tested))
                    return Response(
                    {
                        'status' : True,
                        'status_code' : 200,
                        'response' : {
                            'message' : f'{employee.full_name} isn’t available on the selected date {st_time} and {ed_time}, but your team member can still book appointments for them.',
                            'error_message' : f'This Employee day off, {employee.full_name} date {date}',
                            'Availability': False
                        }
                    },
                    status=status.HTTP_200_OK
                )
            else:
                st_time = convert_24_to_12(str(start_time))
                ed_time = convert_24_to_12(str(tested))
                return Response(
                {
                    'status' : True,
                    'status_code' : 200,
                    'response' : {
                        'message' : f'{employee.full_name} isn’t available on the selected date {st_time} and {ed_time}, but your team member can still book appointments for them.',
                        #'message' : f'{employee.full_name} isn’t available on the selected date, but your team member can still book appointments for them.',
                        'error_message' : f'This Employee day off, {employee.full_name} date {date}',
                        'Availability': False
                    }
                },
                status=status.HTTP_200_OK
            )
                
        except Exception as err:
            # st_time = convert_24_to_12(str(start_time))
            # ed_time = convert_24_to_12(str(tested))
            return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    #'message' : f'{employee.full_name} isn’t available on the selected date {st_time} and {ed_time}, but your team member can still book appointments for them.',
                    'message' : f'{employee.full_name} isn’t available on the selected date, but your team member can still book appointments for them.',
                    'error_message' : f'This Employee day off, {employee.full_name} date {date} {str(err)}',
                    'Availability': False
                }
            },
            status=status.HTTP_200_OK
        )                               
        try:
            av_staff_ids = AppointmentService.objects.filter(
                member__id = employee.id,
                appointment_date = date,
                is_blocked = False,
            )
            
            for ser in av_staff_ids:
                if tested <= ser.appointment_time:# or start_time >= ser.end_time:
                    if start_time >= ser.end_time:
                        data.append(f'Employees are free, employee name {employee.full_name}')
                        
                    else:
                        #data.append(f'The selected staff is not available at this time  {employee.full_name}')
                        st_time = convert_24_to_12(str(start_time))
                        ed_time = convert_24_to_12(str(tested))
                        data.append(f'{employee.full_name} isn’t available between {st_time} and {ed_time}, but your team member can still book appointments for them.')
                                                                
                else:
                    data.append(f'Employees are free, employee name: {employee.full_name}')
                    
            if len(av_staff_ids) == 0:
                data.append(f'Employees are free, you can proceed further employee name {employee.full_name}')
                                    
        except Exception as err:
            data.append(f'the employe{employee}, start_time {str(err)}')
    except Exception as err:
        data.append(f'the Error  {str(err)},  Employee Not Available on this time')
                    
    return Response(
            {
                'status' : True,
                'status_code' : 200,
                'status_code_text' : '200',
                'response' : {
                    'message' : 'Employee Availability',
                    'error_message' : None,
                    'employee':data,
                }
            },
            status=status.HTTP_200_OK
        )