from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from rest_framework import status
from Business.models import Business , BusinessAddress

from Service.models import Service
from Employee.models import Employee
from Authentication.models import User
from NStyle.Constants import StatusCodes
import json
from django.db.models import Q
from Client.models import Client

from Appointment.models import Appointment, AppointmentService
from Appointment.serializers import AppoinmentSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def get_appointment(request):
    all_staff_group= Appointment.objects.all().order_by('-created_at')
    serialized = AppoinmentSerializer(all_staff_group, many=True)
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Appointment',
                'error_message' : None,
                'appointment' : serialized.data
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
    business_id= request.data.get('business', None)
    appointments = request.data.get('appointments', None)
    # business_address= request.data.get('business_address', None)
    # service= request.data.get('service', None)
    # member = request.data.get('member', None)
    # appointment_date= request.data.get('appointment_date', None)
    # appointment_time= request.data.get('appointment_time', None)
    # duration= request.data.get('duration')
    #[business_id, member, appointment_date, appointment_time, duration

    client = request.data.get('client', None)
    client_type = request.data.get('client_type', None)
    business_address= request.data.get('business_address', None)
    

    
    if not all([ client]):
         return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                          'business',
                          'service',
                          'member', 
                          'appointment_date', 
                          'appointment_time', 
                          'duration',
                          'client', 


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
    if business_address is not None:
        try:
            business_address=BusinessAddress.objects.get(id=business_address)
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
            
    appointment= Appointment.objects.create(
            user = user,
            business=business,
            client=client,
            business_address=business_address,
            client_type=client_type
            
        )
    
    print(type(appointments))
    print(appointments)
    if type(appointments) == str:
        appointments = json.loads(appointments)

    elif type(appointments) == list:
        pass
    for appointment in appointments:
        member = appointment['member']
        service = appointment['service']
        duration= appointment['duration']
        date_time= appointment['date_time']
        
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
        
        appoinmentservice = AppointmentService.objects.create(
            user = user,
            business = business,
            appointment = appointment,
            duration=duration,
            date_time=date_time
    )
    
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
    serializer = AppoinmentSerializer(appointment, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Attendence Serializer Invalid',
                'error_message' : str(err),
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
    