from django.conf import settings
from operator import ge
from Utility.Constants.Data.months import  FIXED_MONTHS
from Dashboard.serializers import EmployeeDashboradSerializer
from Employee.models import Employee
from TragetControl.models import StaffTarget
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Appointment.models import Appointment, AppointmentCheckout
from Client.models import Client
from NStyle.Constants import StatusCodes
from Business.models import Business, BusinessAddress
from Product.models import ProductStock

from datetime import datetime
from datetime import timedelta

@api_view(['GET'])
@permission_classes([AllowAny])
def get_busines_client_appointment(request):
    business_id = request.GET.get('location', None)
    duration = request.GET.get('duration', None) 
    
    if business_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    revenue = 0
    appointment = 0
        
    #client_count = Client.objects.filter(client_appointments__business_address__id = business_id).prefetch_related('client_appointments__business_address')
    client_count = Client.objects.prefetch_related('client_appointments__business_address').filter(client_appointments__business_address__id = business_id).count()
 
    # checkouts = AppointmentCheckout.objects.filter(business_address__id = business_id).values_list('total_price', flat=True)
    # check = [int(ck) for ck in checkouts]
    # checkouts = sum(check)
    if duration is not None:
        today = datetime.today()
        day = today - timedelta(days=int(duration))
        checkouts = AppointmentCheckout.objects.filter(business_address__id = business_id, created_at__gte = day)
    else:
        checkouts = AppointmentCheckout.objects.filter(business_address__id = business_id)
    for check in checkouts:
        appointment +=1
        if check.total_price is not None:
            revenue += check.total_price

    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Total Revenue',
                'error_message' : None,
                'revenue' : revenue,
                'client_count': client_count,
                'appointments_count': appointment,
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_dashboard_day_wise(request):
    date = request.GET.get('date', None)
    #date = '2022-10-22'
    
    total_revenue = 0
    appointments_count = 0
    total_client = 0
    
    appointment = AppointmentCheckout.objects.filter(is_deleted=False)
    for app in appointment:
        
        create_at = str(app.created_at)
        if (create_at.split(" ")[0] == date ):
            appointments_count +=1
            if app.total_price is not None:
                total_revenue += app.total_price
        
    client = Client.objects.filter(is_deleted=False)
    for cl in client:
        create_at = str(cl.created_at)
        if (create_at.split(" ")[0] == date ):
            total_client +=1
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Total Revenue',
                'error_message' : None,
                'revenue' : total_revenue,
                'appointments_count': appointments_count,
                'total_client': total_client,
        
            }
        },
        status=status.HTTP_200_OK
    )
@api_view(['GET'])
@permission_classes([AllowAny])
def get_appointments_client(request):
    businesaddress= request.data.get('businesaddress', None)
    
    appointment = AppointmentCheckout.objects.filter(appointment_service__business_address= businesaddress)
    
    for i in appointment:
        print(i)
    print('hello')
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Appointment',
                'error_message' : None,
                #'appointments' : serialize.data
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_dashboard_targets(request):
    employee_id = request.data.get('employee_id', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    if not all([employee_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Employee id are required',
                    'fields' : [
                        'employee_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try: 
        employee_id = Employee.objects.get(id=employee_id, is_deleted=False)
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
    serialized = EmployeeDashboradSerializer(employee_id, context={
                        'request' : request, 
                        'range_start': start_date, 
                        'range_end': end_date, 
            })
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Employee',
                'error_message' : None,
                'employee' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_acheived_target_report(request):
    employee_id = request.GET.get('employee_id', None)
    start_month =  request.GET.get('start_month', None)
    end_month = request.GET.get('end_month', None)
    start_year = request.GET.get('start_year', 1900)
    end_year = request.GET.get('end_year', 3000)

    if not all([employee_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required',
                    'fields' : [
                        'employee_id',
                        'start_month',
                        'start_year',
                        'end_month',
                        'end_year',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try: 
        employee = Employee.objects.get(id=employee_id, is_deleted=False)
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
    if start_month is not None and end_month is not None :

        start_index = FIXED_MONTHS.index(start_month) # 1
        end_index = FIXED_MONTHS.index(end_month) # 9

        fix_months = FIXED_MONTHS[start_index : end_index]
    else:
        fix_months = FIXED_MONTHS
        print(fix_months)
    
    targets = StaffTarget.objects.filter(
        employee_id = employee_id,
        month__in = fix_months, # 8
        year__gte = start_year,
        year__lte = end_year,
    )
    acheived=0
    if len(targets) >0:
        for target in targets :
            s = target.service_target
            r = target.retail_target
            acheived = acheived + s + r
    print(acheived)
    return Response(
            {
                'status' : 200,
                'status_code' : '200',
                'response' : {
                    'message' : 'achieved Target',
                    'error_message' : None,
                    'employee_id' : employee_id,
                    'total_achieved_targets' : acheived,
                }
            },
            status=status.HTTP_200_OK
        )
    
    
    