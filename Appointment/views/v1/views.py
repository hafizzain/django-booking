from django.shortcuts import render

from Appointment.Constants.Reschedule import reschedule_appointment
from Appointment.Constants.AddAppointment import Add_appointment
from Appointment.Constants.cancelappointment import cancel_appointment

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from rest_framework import status
from Business.models import Business , BusinessAddress

#from Service.models import Service
from Service.models import Service
from Employee.models import Employee
from Authentication.models import User
from NStyle.Constants import StatusCodes
import json
from django.db.models import Q
from Client.models import Client, Membership, Promotion, Rewards, Vouchers
from datetime import date
from threading import Thread


from Appointment.models import Appointment, AppointmentService, AppointmentNotes , AppointmentCheckout
from Appointment.serializers import  CheckoutSerializer, AppoinmentSerializer,SingleAppointmentSerializer ,BlockSerializer ,AllAppoinmentSerializer, SingleNoteSerializer, TodayAppoinmentSerializer, EmployeeAppointmentSerializer, AppointmentServiceSerializer, UpdateAppointmentSerializer
from Utility.models import ExceptionRecord

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
def get_today_appointments(request):
    today = date.today()
    today_appointment = AppointmentService.objects.filter(appointment_date__icontains = today )
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
    #[business_id, member, appointment_date, appointment_time, duration

    client = request.data.get('client', None)
    client_type = request.data.get('client_type', None)
    
    payment_method = request.data.get('payment_method', None)
    discount_type = request.data.get('discount_type', None)

    if not all([ client, client_type, appointment_date, business_id  ]):
         return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                          'client',
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
        return Response(
            {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_CLIENT_4032,
                    'response' : {
                    'message' : 'Client not found',
                    'error_message' : str(err),
                }
            }
        )
    
            
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
        duration = appoinmnt['duration']
        date_time = appoinmnt['date_time']
        fav = appoinmnt.get('favourite', None)
        
        voucher_id = appoinmnt.get('voucher', None)
        reward_id = appoinmnt.get('reward', None)
        membership_id = appoinmnt.get('membership', None)
        promotion_id = appoinmnt.get('promotion', None)
        # tip = appoinmnt['tip']
        
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
            duration=duration,
            appointment_time=date_time,
            appointment_date = appointment_date,
            service = service,
            member = member,
            
            voucher = voucher,
            reward = reward,
            membership = membership,
            promotion = promotion
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
    end_time = request.data.get('end_time',None)
    
    member = request.data.get('member',None)
    details = request.data.get('details', None)
    
    if not all([business_id, date, start_time, end_time , member]):
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
                          'end_time', 
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
            duration = end_time, 
            appointment_date = date,
            member = member,
            destails = details,
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

    # if not serialized.is_valid():
    #     return Response(
    #             {
    #         'status' : False,
    #         'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
    #         'response' : {
    #             'message' : 'Block Serializer Invalid',
    #             'error_message' : str(err),
    #         }
    #     },
    #     status=status.HTTP_404_NOT_FOUND
    #     )
    # serialized.save()
    
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
        appointments = AppointmentService.objects.get(id=appointment)
    except Exception as err:
        appointments = None
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
    
    serialized = CheckoutSerializer(checkout)
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Appointment Checkout Create!',
                    'error_message' : None,
                    'checkout' : serialized.data,
                }
            },
            status=status.HTTP_201_CREATED
    ) 
    
@api_view(['GET'])
@permission_classes([AllowAny])
def service_appointment_count(request):
    services = Service.objects.all()
    return_data =[]
    for ser in services:
        app_service = AppointmentService.objects.filter(service = ser)
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
    