from pickle import GET
from django.shortcuts import render
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
from Client.models import Client
from datetime import date

from Appointment.models import Appointment, AppointmentService
from Appointment.serializers import AppoinmentSerializer,SingleAppointmentSerializer ,BlockSerializer ,AllAppoinmentSerializer, TodayAppoinmentSerializer, EmployeeAppointmentSerializer, AppointmentServiceSerializer, UpdateAppointmentSerializer


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
        is_blocked = False,
    ).order_by('-created_at')
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


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_appointment(request):
    appointment_id = request.data.get('appointment_id', None)
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
                        'appointment_id'                         
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
    
    appointment.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Appointment deleted successfully',
                'error_message' : None
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
    #[business_id, member, appointment_date, appointment_time, duration

    client = request.data.get('client', None)
    client_type = request.data.get('client_type', None)
    
    payment_method = request.data.get('payment_method', None)
    discount_type = request.data.get('discount_type', None)

    if not all([ client, client_type, appointments, appointment_date, business_id, payment_method  ]):
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
                          'payment_method',
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


    for appoinmnt in appointments:
        member = appoinmnt['member']
        service = appoinmnt['service']
        duration = appoinmnt['duration']
        date_time = appoinmnt['date_time']
        tip = appoinmnt['tip']
        
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
            tip=tip,
        )
        if business_address_id is not None:
            appointment_service.business_address = business_address
            appointment_service.save()
    
    serialized = AppoinmentSerializer(appointment)
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Appointment Create!',
                    'error_message' : None,
                    'appointment' : serialized.data,
                }
            },
            status=status.HTTP_201_CREATED
    ) 
 
 
 
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_appointment(request):
    appointment_service_id = request.data.get('id', None)
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
        service_appointment = Appointment.objects.get(id=appointment_service_id)
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
                'message' : 'Attendence Serializer Invalid',
                'error_message' : str(serializer.errors),
            }
        },
        status=status.HTTP_404_NOT_FOUND
        )
    serializer.save()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Update Appointment Successfully',
                'error_message' : None,
                'StaffGroupUpdate' : serializer.data
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
            appointment_date = date,
            member = member,
            destails = details,
            is_blocked = True,
        )
    
    serialized = BlockSerializer(block_time)
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Appointment Create!',
                    'error_message' : None,
                    'appointment' : serialized.data,
                }
            },
            status=status.HTTP_201_CREATED
    ) 