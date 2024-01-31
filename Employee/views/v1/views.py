import threading
from rest_framework.decorators import action
from django.db.models import Count, IntegerField, Sum, FloatField, Q, Subquery, OuterRef, Case, When, F, Value, \
    CharField
from django.utils import timezone
from django.db import models
from datetime import datetime, timedelta
import random
import string
from rest_framework import viewsets
from time import strptime
from django.shortcuts import render

from Appointment.models import AppointmentService
from Employee.models import (CategoryCommission, EmployeDailySchedule, Employee, EmployeeProfessionalInfo,
                             EmployeePermissionSetting, EmployeeModulePermission
, EmployeeMarketingPermission, EmployeeSelectedService, SallarySlipPayrol, StaffGroup
, StaffGroupModulePermission, Attendance
, Payroll, CommissionSchemeSetting, Asset, AssetDocument, Vacation, LeaveManagements, WeekManagement,
                             VacationDetails, GiftCard, GiftCards, GiftDetails,
                             )
from Employee.services import annual_vacation_check, check_available_vacation_type
from HRM.models import Holiday
from Tenants.models import EmployeeTenantDetail, Tenant
from django_tenants.utils import tenant_context
from Utility.Constants.Data.PermissionsValues import ALL_PERMISSIONS, PERMISSIONS_MODEL_FIELDS
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from Employee.serializers import (EmployeSerializer, EmployeInformationsSerializer,
                                  Payroll_Working_device_attendence_ScheduleSerializer,
                                  Payroll_Working_deviceScheduleSerializer, Payroll_WorkingScheduleSerializer,
                                  SallarySlipPayrolSerializers,
                                  ScheduleSerializer, SingleEmployeeInformationSerializer, StaffGroupSerializers,
                                  EmployeeDropdownSerializer,
                                  AttendanceSerializers, PayrollSerializers, UserEmployeeSerializer, VacationSerializer,
                                  singleEmployeeSerializer,
                                  CommissionSerializer, AssetSerializer, WorkingScheduleSerializer,
                                  NewVacationSerializer,
                                  NewAbsenceSerializer, singleEmployeeSerializerOP, Payroll_WorkingScheduleSerializerOP,
                                  WeekendManagementSerializer, LeaveManagementSerializer, ScheduleSerializerOP,
                                  ScheduleSerializerResponse, GiftCardSerializer, GiftCardSerializerResponse,GiftDetail,
                                  EmployeDailyScheduleResponse, VacationDetailsSerializer,
                                  VacationDetailsResponseSerializer, Allscedulae
                                  )
from Employee.optimized_serializers import OptimizedEmployeeSerializerDashboard
from django.db import connection, transaction
from threading import Thread
from Employee.Constants.Add_Employe import add_employee
from Service.models import Service
from rest_framework import status
from Business.models import Business, BusinessAddress
from Utility.models import Country, ExceptionRecord, State, City
from Authentication.models import AccountType, User, VerificationOTP
from NStyle.Constants import StatusCodes
import json
from Utility.models import NstyleFile
from django.db.models import Q, F, Sum, When, Case, IntegerField, FloatField
import csv
from Utility.models import GlobalPermissionChoices
from Permissions.models import EmployePermission
from django.contrib.auth import authenticate, logout
from rest_framework.authtoken.models import Token
from Authentication.Constants import OTP
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
from django.core.paginator import Paginator

from Notification.models import CustomFCMDevice
from Notification.serializers import FCMDeviceSerializer
from Notification.notification_processor import NotificationProcessor

from Utility.Constants.get_from_public_schema import get_country_from_public, get_state_from_public
from Sale.Constants.Custom_pag import CustomPagination
from Employee.serializers import *


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_employee(request):
    employee_csv = request.data.get('file', None)
    user = request.user
    business_id = request.data.get('business', None)

    file = NstyleFile.objects.create(
        file=employee_csv
    )
    with open(file.file.path, 'r', encoding='utf-8') as imp_file:
        for index, row in enumerate(imp_file):
            if index == 0:
                continue

            row = row.split(',')
            row = row
            if len(row) < 10:
                print(len(row))
                continue
                # pass
            name = row[0].strip('"')
            designation = row[1].strip('"')

            email = row[2].strip('"')
            income_type = row[3].strip('"')
            salary = row[4].strip('"')
            address = row[5].strip('"')
            gender = row[6].strip('"')
            country = row[7].strip('"')
            city = row[8].strip('"')
            state = row[9].strip('"').replace('\n', '').strip('"')
            # employee_id = row[10]
            print(city)

            try:
                business = Business.objects.get(id=business_id)
            except Exception as err:
                return Response(
                    {
                        'status': True,
                        'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                        'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                        'response': {
                            'message': 'Business not found!',
                            'error_message': str(err),
                        }
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            try:
                country, created = Country.objects.get_or_create(name__icontains=country)
                state, created = State.objects.get_or_create(name__icontains=state)
                city, created = City.objects.get_or_create(name__icontains=city)
            except Exception as err:
                return Response(
                    {
                        'status': True,
                        'status_code': StatusCodes.INVALID_COUNTRY_STATE_CITY_4021,
                        'status_code_text': 'INVALID_COUNTRY_STATE_CITY_4021',
                        'response': {
                            'message': 'Invalid Country, State, City not found!',
                            'error_message': str(err),
                        }
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            employee = Employee.objects.create(
                user=user,
                business=business,
                full_name=name,
                email=email,
                address=address,
                gender=gender,
                country=country,
                state=state,
                city=city,
            )

            EmployeeProfessionalInfo.objects.create(
                employee=employee,
                designation=designation,
                income_type=income_type,
                salary=salary,
            )

            EmployeePermissionSetting.objects.create(
                employee=employee,
                allow_calendar_booking=True,
                access_calendar=False,
                change_calendar_color=False,
            )

            EmployeeModulePermission.objects.create(
                employee=employee,
                access_reports=False,
                access_sales=False,
                access_inventory=False,
                access_expenses=False,
                access_products=False,
            )

            EmployeeMarketingPermission.objects.create(
                employee=employee,
                access_voucher=False,
                access_member_discount=False,
                access_invite_friend=False,
                access_loyalty_points=False,
                access_gift_cards=False
            )

    file.delete()
    return Response({'Status': 'Success'})


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_attendance(request):
    attendence_csv = request.data.get('file', None)
    business_id = request.data.get('business', None)
    user = request.user

    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            }

        )
    file = NstyleFile.objects.create(
        file=attendence_csv
    )
    with open(file.file.path, 'r', encoding='utf-8') as imp_file:
        for index, row in enumerate(imp_file):
            if index == 0:
                continue
            # row =  row.replace("'", '"')
            row = row.split(',')
            row = row
            if len(row) < 4:
                continue
                # pass
            emp_name = row[0].strip('"')
            # if emp_name == '':
            #     return Response(
            #         {
            #             'status' : False,
            #             'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
            #             'status_code_text' : 'INVALID_EMPLOYEE_4025',
            #             'response' : {
            #                 'message' : 'Employee Not Found',
            #                 'error_message' : 'Error' ,
            #             }
            #         },
            #         status=status.HTTP_404_NOT_FOUND
            #     )

            try:
                employee_id = Employee.objects.filter(full_name=emp_name, is_deleted=False).first()
            except Exception as err:
                return Response(
                    {
                        'status': False,
                        'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                        'status_code_text': 'INVALID_EMPLOYEE_4025',
                        'response': {
                            'message': 'Employee Not Found',
                            'error_message': str(err),
                        }
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            in_time = row[1].strip('"')
            out_time = row[2].strip('"')
            status_att = row[3].strip('"')

            create_attendence = Attendance.objects.create(
                user=user,
                business=business,
                employee=employee_id,
                in_time=in_time,
                out_time=out_time,
                # is_active = status_att,

            )
            if status_att.strip() == 'Active':
                create_attendence.is_active = True
                create_attendence.save()
            else:
                create_attendence.is_active = False
                create_attendence.save()
            # if out_time == strptime('%H:%M:%S') :
            #     print('enter')
            #     create_attendence.out_time =out_time
            #     create_attendence.save()
            # else:
            #     create_attendence.out_time =None
            #     create_attendence.save()

            # print(f'Added Product {create_attendence} ... {employee_id} ')

    file.delete()
    return Response({'Status': 'Success'})


# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def search_employee(request):
    text = request.GET.get('text', None)

    if text is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Fields are required.',
                    'fields': [
                        'text',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    search_employee = Employee.objects.filter(
        Q(full_name__icontains=text) |
        Q(employee_id__icontains=text) |
        Q(email__icontains=text) |
        Q(mobile_number__icontains=text) |
        Q(gender__icontains=text) |
        Q(employee_professional_details__designation__icontains=text) |
        Q(employee_professional_details__income_type__icontains=text),
        is_deleted=False
    )
    serialized = singleEmployeeSerializer(search_employee, many=True, context={'request': request})
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'All Search Products!',
                'error_message': None,
                'count': len(serialized.data),
                'Employees': serialized.data,
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_employees_mainpage(request):
    no_pagination = request.GET.get('no_pagination', None)
    search_text = request.GET.get('search_text', None)
    location_id = request.GET.get('location_id', None)
    designation = request.GET.get('designation', None)
    income_type = request.GET.get('income_type', None)
    is_active = request.GET.get('is_active', None)

    query = Q(is_deleted=False, is_blocked=False)

    if is_active:
        query &= Q(is_active=is_active)

    if search_text:
        query &= Q(full_name__icontains=search_text) | Q(mobile_number__icontains=search_text)

    if designation:
        query &= Q(employee_professional_details__designation=designation)

    if income_type:
        query &= Q(employee_professional_details__income_type=income_type)

    if location_id:
        location = BusinessAddress.objects.get(id=str(location_id))
        query &= Q(location=location)

    all_employe = Employee.objects \
        .filter(query) \
        .with_total_sale() \
        .order_by('-total_sale')

    all_employee_count = all_employe.count()

    page_count = all_employee_count / 10
    if page_count > int(page_count):
        page_count = int(page_count) + 1

    results_per_page = 10000 if no_pagination else 10
    paginator = Paginator(all_employe, results_per_page)
    page_number = request.GET.get("page", None)

    if page_number is not None:
        all_employe = paginator.get_page(page_number)

        serialized = singleEmployeeSerializerOP(all_employe, many=True, context={'request': request})
        data = serialized.data
        return Response(
            {
                'status': 200,
                'status_code': '200',
                'response': {
                    'message': f'Page {page_number} Employee',
                    'count': all_employee_count,
                    'pages': page_count,
                    'per_page_result': results_per_page,
                    'error_message': None,
                    'employees': data
                }
            },
            status=status.HTTP_200_OK
        )
    else:
        serialized = singleEmployeeSerializerOP(all_employe, many=True, context={'request': request})
        data = serialized.data
        return Response(
            {
                'status': 200,
                'status_code': '200',
                'response': {
                    'message': 'All Employee',
                    'count': all_employee_count,
                    'pages': page_count,
                    'per_page_result': 20,
                    'error_message': None,
                    'employees': data
                }
            },
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_Employees(request):
    no_pagination = request.GET.get('no_pagination', None)
    search_text = request.GET.get('search_text', None)
    location_id = request.GET.get('location_id', None)
    employee_id = request.GET.get('employee_id', None)
    designation = request.GET.get('designation', None)
    income_type = request.GET.get('income_type', None)

    query = Q(is_deleted=False)
    query &= Q(is_blocked=False)

    if search_text:
        query &= Q(full_name__icontains=search_text) | Q(mobile_number__icontains=search_text)

    if employee_id:
        query &= Q(id=str(employee_id))

    if designation:
        query &= Q(employee_professional_details__designation=designation)

    if income_type:
        query &= Q(employee_professional_details__income_type=income_type)

    if location_id:
        location = BusinessAddress.objects.get(id=str(location_id))
        query &= Q(location=location)

    all_employe = Employee.objects \
        .filter(query) \
        .select_related('user', 'business', 'country', 'state', 'city', 'employee_permissions') \
        .prefetch_related('location') \
        .with_total_sale() \
        .order_by('-total_sale')
    all_employee_count = all_employe.count()

    page_count = all_employee_count / 10
    if page_count > int(page_count):
        page_count = int(page_count) + 1

    results_per_page = 10000 if no_pagination else 10
    paginator = Paginator(all_employe, results_per_page)
    page_number = request.GET.get("page", None)

    if page_number is not None:
        all_employe = paginator.get_page(page_number)

        serialized = singleEmployeeSerializer(all_employe, many=True, context={'request': request})
        data = serialized.data
        return Response(
            {
                'status': 200,
                'status_code': '200',
                'response': {
                    'message': f'Page {page_number} Employee',
                    'count': all_employee_count,
                    'pages': page_count,
                    'per_page_result': results_per_page,
                    'error_message': None,
                    'employees': data
                }
            },
            status=status.HTTP_200_OK
        )
    else:
        serialized = singleEmployeeSerializer(all_employe, many=True, context={'request': request})
        data = serialized.data
        return Response(
            {
                'status': 200,
                'status_code': '200',
                'response': {
                    'message': 'All Employee',
                    'count': all_employee_count,
                    'pages': page_count,
                    'per_page_result': 20,
                    'error_message': None,
                    'employees': data
                }
            },
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_Employees_dropdown(request):
    # no_pagination = request.GET.get('no_pagination', None)
    location_id = request.GET.get('location_id', None)
    search_text = request.GET.get('search_text', None)
    page = request.query_params.get('page', None)
    # is_calendar = request.query_params.get('is_calendar', None)

    is_searched = False

    query = Q(is_deleted=False)
    query &= Q(is_blocked=False)
    query &= Q(is_active=True)

    if search_text:
        query &= Q(full_name__icontains=search_text) | \
                 Q(mobile_number__icontains=search_text) | \
                 Q(email__icontains=search_text) | \
                 Q(employee_id__icontains=search_text)
        is_searched = True

    if location_id:
        location = BusinessAddress.objects.get(id=str(location_id))
        query &= Q(location=location)

    all_employe = Employee.objects.filter(query).order_by('-created_at')

    serialized = list(EmployeeDropdownSerializer(all_employe, many=True, context={'request': request}).data)

    paginator = CustomPagination()
    paginator.page_size = 10 if page else 100000
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'employees', invoice_translations=None,
                                                current_page=page, is_searched=is_searched)
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def get_employees_dashboard(request):
    location_id = request.GET.get('location_id', None)

    query = Q(is_deleted=False)
    if location_id:
        query &= Q(location__id=location_id)

    employees = Employee.objects.filter(query) \
                    .with_total_sale() \
                    .order_by('-total_sale')[:10]

    data = OptimizedEmployeeSerializerDashboard(employees, many=True, context={'request': request}).data

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Employees',
                'error_message': None,
                'Employee': data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_single_employee(request):
    employee_id = request.GET.get('employee_id', None)

    if not all([employee_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Employee id are required',
                    'fields': [
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
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'status_code_text': 'INVALID_EMPLOYEE_4025',
                'response': {
                    'message': 'Employee Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

        staff = None
    seralized = EmployeSerializer(employee_id, context={'request': request, })

    data = dict()
    data.update(seralized.data)
    try:
        data.update(data['permissions'])
        del data['permissions']

    except Exception as err:
        print(f'dict {err}')
        None
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Business languages',
                'error_message': None,
                'Employee': data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def single_employee_schedule(request):
    employee_id = request.GET.get('employee_id', None)

    if not all([employee_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Employee id are required',
                    'fields': [
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
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'status_code_text': 'INVALID_EMPLOYEE_4025',
                'response': {
                    'message': 'Employee Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = WorkingScheduleSerializer(employee_id)
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'Single Employee',
                'error_message': None,
                'employee': serializer.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_workingschedule(request):
    s = None
    employee_ids_in_schedule = None
    is_weekend = request.query_params.get('is_weekend', None)
    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)
    location_id = request.query_params.get('location_id', None)
    month = request.query_params.get('month', None)
    year = request.query_params.get('year', None)
    # is_vacation = request.query_params.get('is_vacation',None)
    if is_weekend is None:
        query = {}
        if location_id:
            query['location__id'] = location_id
        # if start_date:
        #     query['employee_employedailyschedule__date__date__gte'] = start_date
        # if end_date:
        #     query['employee_employedailyschedule__date__date__lte'] = end_date

        # all_employee = Employee.objects.filter(is_deleted=False, is_blocked=False, **query).order_by(
        #     '-created_at')
        # all_employee = all_employee.filter(
        #     Q(
        #         is_active=False ,is_active_date_lte=end_date
        #     ) | Q(is_active=True)
        # )
        all_employee = Employee.objects.filter(is_deleted=False, is_blocked=False, **query).order_by('-created_at')
        all_employee = all_employee.filter(
            Q(is_active=False, in_active_date__gte=end_date
            ) | Q(is_active=True)
        )

        # all_employee = all_memebers.annotate(
        #     filtered_in_active_date=Case(
        #         When(in_active_date__isnull=False,
        #              then=Case(When(in_active_date__lte=selected_date, then=F('in_active_date')))),
        #         default=Value(selected_date),
        #         output_field=models.DateField(),
        #     )
        # )
        # all_employee = all_employee.filter(filtered_in_active_date__lte=selected_date)
        # all_employee = Employee.objects.filter(query).order_by('-created_at')
        # all_employee = all_employee.filter(
        #     Q(is_active=False,in_active_date__lte=end_date)| Q(is_active=True)
        #
        # )
        # all_employee = all_employee.annotate(
        #     filtered_in_active_date=Case(
        #         When(in_active_date__isnull=False,
        #              then=Case(When(in_active_date__lte=end_date, then=F('in_active_date')))),
        #         default=Value(end_date),
        #         output_field=models.DateField(),
        #     )
        # )

        serialized = WorkingScheduleSerializer(all_employee, many=True, context={'request': request,
                                                                                 'start_date': start_date,
                                                                                 'end_date': end_date,
                                                                                 'location_id': location_id})
        # result = EmployeDailySchedule.objects.filter(is_holiday=True)
        # s = EmployeDailyScheduleResponse(result, many=True).data
        return Response(
            {
                'start_date': start_date, 'end_date': end_date,
                'status': 200,
                # 's': s,
                'status_code': '200',
                'response': {
                    'message': 'All Employee',
                    'error_message': None,
                    'employees': serialized.data
                }
            },
            status=status.HTTP_200_OK
        )
    else:
        employee_ids_in_schedule = EmployeDailySchedule.objects.filter(is_weekend=True, from_date__year=year,
                                                                       from_date__month=month, location_id=location_id)
        serialized = ScheduleSerializerResponse(employee_ids_in_schedule, many=True, context={'request': request,
                                                                                              'location_id': location_id})

        return Response(
            {
                'employee_ids_in_schedule': str(employee_ids_in_schedule),
                'status': 200,
                'status_code': '200',
                'response': {
                    'message': 'All Employee',
                    'error_message': None,
                    'employees': serialized.data
                }
            },
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def del_all_avaliable(request):
    vacations = Vacation.objects.all()
    sceduales = EmployeDailySchedule.objects.all()
    holiday = Holiday.objects.all()
    vacations.delete()
    sceduales.delete()
    holiday.delete()
    return Response({"msg": "del all"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_id(request):
    tenant_name = request.tenant_name
    tenant_name = tenant_name.split('-')
    tenant_name = [word[0] for word in tenant_name]
    print(tenant_name)
    ''.join(tenant_name)
    count = Employee.objects.all().count()
    count += 1

    # tenant_name ='NS'
    return_loop = True
    while return_loop:
        if 0 < count <= 9:
            count = f'000{count}'
        elif 9 < count <= 99:
            count = f'00{count}'
        elif 99 < count <= 999:
            count = f'0{count}'
        new_id = f'{tenant_name}-EMP-{count}'

        try:
            Employee.objects.get(employee_id=new_id)
            count += 1
        except:
            return_loop = False
            break
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'Generated ID',
                'error_message': None,
                'id': new_id
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def check_email_employees(request):
    email = request.data.get('email', None)
    mobile_number = request.data.get('mobile_number', None)

    previous_email = request.data.get('previous_email', None)
    previous_mobile_number = str(request.data.get('previous_mobile_number', None))
    previous_mobile_number = previous_mobile_number.replace('+', '')

    """
    TENANT SPECIFIC DATA
    """

    if email:
        employees = Employee.objects.filter(email=email)
        if previous_email:
            employees = employees.exclude(email=previous_email)
        if employees:
            return Response(
                {
                    'status': False,
                    'status_code': 200,
                    'status_code_text': '200',
                    'response': {
                        'message': f'User Already exist with this {email}!',
                        'error_message': None,
                        'employee': True,
                    }
                },
                status=status.HTTP_200_OK
            )
        else:
            pass

    if mobile_number:
        employees = Employee.objects.filter(mobile_number=mobile_number)
        employees_count = employees.count()
        if previous_mobile_number:
            employees = employees.exclude(mobile_number__icontains=previous_mobile_number)

        if employees:
            return Response(
                {
                    'status': False,
                    'status_code': 200,
                    'status_code_text': '200',
                    'response': {
                        'message_mobile_number': f'User Already exist with this phone number!',
                        'error_message': None,
                        'employee': True,
                    }
                },
                status=status.HTTP_200_OK
            )
        else:
            pass

    with tenant_context(Tenant.objects.get(schema_name='public')):

        """
        PUBLIC TENANT DATA
        """

        if email:
            user = User.objects.filter(email=email)
            if previous_email:
                user = user.exclude(email=previous_email)

            if user:
                return Response(
                    {
                        'status': False,
                        'status_code': 200,
                        'status_code_text': '200',
                        'response': {
                            'message': f'User Already exist with this {email}!',
                            'error_message': None,
                            'employee': True,
                        }
                    },
                    status=status.HTTP_200_OK
                )
            else:
                pass

        if mobile_number:
            user = User.objects.filter(mobile_number__icontains=mobile_number)

            if previous_mobile_number:
                user = user.exclude(mobile_number__icontains=previous_mobile_number)

            if user:
                return Response(
                    {
                        'status': False,
                        'status_code': 200,
                        'status_code_text': '200',
                        'response': {
                            'message_mobile_number': f'User Already exist with this phone number!',
                            'error_message': None,
                            'employee': True,
                        }
                    },
                    status=status.HTTP_200_OK
                )
            else:
                pass

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'Single Employee',
                'error_message': None,
                'employee': False,
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_employee(request):
    user = request.user

    full_name = request.data.get('full_name', None)
    employee_id = request.data.get('employee_id', None)
    tenant_id = request.data.get('tenant_id', None)
    domain = request.data.get('domain', None)

    email = request.data.get('email', None)
    image = request.data.get('image', None)
    business_id = request.data.get('business', None)
    mobile_number = request.data.get('mobile_number', None)
    dob = request.data.get('dob', None)
    gender = request.data.get('gender', 'Male')

    postal_code = request.data.get('postal_code', None)
    address = request.data.get('address', None)
    joining_date = request.data.get('joining_date', None)
    to_present = request.data.get('to_present', False)
    ending_date = request.data.get('ending_date', None)
    is_active = request.data.get('is_active', None)

    # UserInformation
    designation = request.data.get('designation', None)
    income_type = request.data.get('income_type', 'Hourly_Rate')
    salary = request.data.get('salary', None)

    # end_time= request.data.get('end_time',None)
    # start_time = request.data.get('start_time', None)
    working_days = request.data.get('working_days', None)
    staff_id = request.data.get('staff_group', None)
    # level = request.data.get('level',None)

    # start_time = request.data.get('start_time',None)
    # end_time = request.data.get('end_time',None)
    maximum_discount = request.data.get('maximum_discount', None)

    services_id = request.data.get('services', None)

    location = request.data.get('location', None)
    country_unique_id = request.data.get('country', None)
    state_unique_id = request.data.get('state', None)
    city_name = request.data.get('city', None)
    # Either employee can refund the order or not
    can_refund = request.data.get('can_refund', False)
    leave_data = request.data.get('leave_data', [])
    leave_management = None

    if not all([
        business_id, full_name, employee_id, country_unique_id, gender, address, designation, income_type,
        salary]):  # or ( not to_present and ending_date is None):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                        'employee_id',
                        'full_name',
                        'email',
                        'gender',
                        'country',
                        'address',
                        'designation',
                        'income_type',
                        'salary',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(salary) > 7:
        return Response(
            {
                'status': True,
                'status_code': StatusCodes.INVALID_LENGTH_4030,
                'status_code_text': 'INVALID_LENGTH_4030',
                'response': {
                    'message': 'Length not Valid!',
                    'error_message': 'Salary length to be 6 Integer',
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    employees_error = []
    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': True,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business not found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    public_country = get_country_from_public(country_unique_id)
    public_state = get_state_from_public(state_unique_id)

    try:
        country, created = Country.objects.get_or_create(
            name=public_country.name,
            unique_id=public_country.unique_id
        )
    except Exception as err:
        return Response(
            {
                'status': True,
                'status_code': StatusCodes.INVALID_COUNTRY_STATE_CITY_4021,
                'status_code_text': 'INVALID_COUNTRY_STATE_CITY_4021',
                'response': {
                    'message': 'Invalid Country, State, City not found!!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        state, created = State.objects.get_or_create(
            name=public_state.name,
            unique_id=public_state.unique_id
        )
    except:
        state = None
    try:
        city, created = City.objects.get_or_create(name=city_name,
                                                   country=country,
                                                   state=state,
                                                   country_unique_id=country_unique_id,
                                                   state_unique_id=state_unique_id)
    except:
        city = None
    try:
        staff = StaffGroup.objects.get(id=staff_id)
    except Exception as err:
        staff = None

    employee = Employee.objects.create(
        user=user,
        business=business,
        full_name=full_name,
        image=image,
        employee_id=employee_id,
        mobile_number=mobile_number,
        dob=dob,
        gender=gender,
        country=country,
        state=state,
        city=city,
        postal_code=postal_code,
        address=address,
        joining_date=joining_date,
        ending_date=ending_date,
        can_refunds=can_refund
    )
    if not to_present:
        pass
    else:
        employee.to_present = True
    if is_active is not None:
        employee.is_active = True
    else:
        employee.is_active = False
        employee.in_active_date = timezone.now().date()

    if email is not None:
        employee.email = email
    employee.save()
    data = {}

    errors = []

    if staff is not None:
        try:
            staff.employees.add(employee)
            # data.update(staff)
        except:
            pass
    if len(leave_data) > 0:
        leave_data = json.loads(leave_data)
        leave_management = LeaveManagements.objects.create(
            employee_id=employee.id,
            operational_casual_leave=leave_data.get('operational_casual_leave', 0),
            operational_annual_leave=leave_data.get('operational_annual_leave', 0),
            operational_medical_leave=leave_data.get('operational_medical_leave', 0),
            casual_leave=leave_data.get('operational_casual_leave', 0),
            annual_leave=leave_data.get('operational_annual_leave', 0),
            medical_leave=leave_data.get('operational_medical_leave', 0),
            number_of_months=leave_data.get('number_of_months', 0)
        )
        leave_data = LeaveManagementSerializer(leave_management, many=False)

    employee_p_info = EmployeeProfessionalInfo.objects.create(
        employee=employee,
        # start_time = start_time , end_time = end_time,
        maximum_discount=maximum_discount,
        salary=salary,
        designation=designation,
        income_type=income_type,
    )

    employee_p_info.monday = True if 'monday' in request.data else False
    employee_p_info.tuesday = True if 'tuesday' in request.data else False
    employee_p_info.wednesday = True if 'wednesday' in request.data else False
    employee_p_info.thursday = True if 'thursday' in request.data else False
    employee_p_info.friday = True if 'friday' in request.data else False
    employee_p_info.saturday = True if 'saturday' in request.data else False
    employee_p_info.sunday = True if 'sunday' in request.data else False

    if type(services_id) == str:
        services_id = json.loads(services_id)
    else:
        pass
    if services_id is not None:
        for services in services_id:
            try:
                if services['service'] is not None:
                    ser = Service.objects.get(id=services['service'])

                    EmployeeSelectedService.objects.get_or_create(
                        employee=employee,
                        service=ser,
                        level=services['level']
                    )
            except Exception as error:
                print(error)
                None

    employee_p_info.save()

    serialized = EmployeInformationsSerializer(employee_p_info, data=request.data)
    if serialized.is_valid():
        serialized.save()
        data.update(serialized.data)

    empl_permission = EmployePermission.objects.create(employee=employee)
    for permit in ALL_PERMISSIONS:

        value = request.data.get(permit, None)
        employees_error.append(value)
        if value is not None:
            if type(value) == str:
                value = json.loads(value)
            for opt in value:
                try:
                    option = GlobalPermissionChoices.objects.get(text=opt)
                    PERMISSIONS_MODEL_FIELDS[permit](empl_permission).add(option)
                except Exception as err:
                    employees_error.append(str(value))
    empl_permission.save()

    try:
        location_id = BusinessAddress.objects.get(id=str(location))
        employee.location.add(location_id)
    except Exception as err:
        employees_error.append(str(err))

    employee_serialized = EmployeSerializer(employee, context={'request': request, })
    data.update(employee_serialized.data)

    template = 'Employee'
    if email is not None:
        try:
            try:
                username = email.split('@')[0]
                try:
                    user_check = User.objects.get(username=username)
                except Exception as err:
                    # data.append(f'username user is client errors {str(err)}')
                    pass
                else:
                    username = f'{username} {len(User.objects.all())}'

            except Exception as err:
                pass

            user = User.objects.create(
                first_name=full_name,
                username=username,
                email=email,
                is_email_verified=True,
                is_active=True,
                mobile_number=mobile_number,
            )
            account_type = AccountType.objects.create(
                user=user,
                account_type='Employee'
            )
        except Exception as err:
            pass
            # stop_thread = False
    try:
        thrd = Thread(target=add_employee,
                      args=[full_name, email, mobile_number, template, business.business_name, tenant_id, domain, user])
        thrd.start()
        # stop_thread = True
        # if thrd.is_alive():
        #     thrd._stop()
    except Exception as err:
        employees_error.append(str(err))

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Employee Added Successfully!',
                'error_message': None,
                'employee_error': employees_error,
                'employees': data,
                'leave_data': leave_data.data
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_employee(request):
    employee_id = request.data.get('employee', None)

    if employee_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'employee'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        employee = Employee.objects.get(id=employee_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Employee ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        staff_group = StaffGroup.objects.get(employees=employee)
        # print(staff_group)
        staff_group.employees.remove(employee)
        # print(staff_group.employees.remove(employee))
        staff_group.save()
    except:
        pass

    employee.is_deleted = True
    employee.save()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Employee deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_employee(request):
    # sourcery skip: avoid-builtin-shadow
    id = request.data.get('id', None)
    is_active = request.data.get('is_active', None)
    services_id = request.data.get('services', None)
    staff_id = request.data.get('staff_group', None)
    location = request.data.get('location', None)

    country_unique_id = request.data.get('country', None)
    state_unique_id = request.data.get('state', None)
    city_name = request.data.get('city', None)
    email_changed = False
    old_email = None
    emp_email = request.data.get('email')
    can_refund = request.data.get('can_refund', False)

    leave_data = request.data.get('leave_data', [])
    lev_id = 0

    # emp = Employee.objects.get(id=id)

    working_days = []

    Errors = []

    if id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'User id is required',
                    'fields': [
                        'id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        employee = Employee.objects.get(id=id)
        if employee.email != emp_email:
            old_email = employee.email
            email_changed = True

    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
                'status_code_text': 'INVALID_NOT_FOUND_EMPLOYEE_ID_4022',
                'response': {
                    'message': 'Employee Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    if leave_data:
        leave_data = json.loads(leave_data)
        leave_management = LeaveManagements.objects.filter(employee_id=id)
        if leave_management:
            leave_management.update(
                operational_casual_leave=leave_data.get('operational_casual_leave', 0),
                operational_annual_leave=leave_data.get('operational_annual_leave', 0),
                operational_medical_leave=leave_data.get('operational_medical_leave', 0),
                number_of_months=leave_data.get('number_of_months', 0),
            )
    try:
        leave_object = LeaveManagements.objects.get(employee_id=id)
    except:
        leave_object = LeaveManagements.objects.create(employee_id=id)
    casual_leave = leave_object.operational_casual_leave - leave_object.used_casual
    medical_leave = leave_object.operational_medical_leave - leave_object.used_medical
    annual_leave = leave_object.operational_annual_leave - leave_object.used_annual
    if 0 > casual_leave or 0 > medical_leave or 0 > annual_leave:
        pass
    else:
        leave_object.casual_leave = leave_object.operational_casual_leave - leave_object.used_casual
        leave_object.medical_leave = leave_object.operational_medical_leave - leave_object.used_medical
        leave_object.annual_leave = leave_object.operational_annual_leave - leave_object.used_annual
        leave_object.save()

    try:
        staff = StaffGroup.objects.get(employees=id)
        staff.employees.remove(employee)
        staff.save()
    except Exception as err:
        staff = None
        print(err)

    try:
        staff_add = StaffGroup.objects.get(id=staff_id)

    except Exception as err:
        print(err)
        staff_add = None

    if staff_add is not None:
        try:
            staff_add.employees.add(employee)
            staff_add.save()

        except:
            pass

    data = {}
    image = request.data.get('image', None)
    phone_number = request.data.get('mobile_number', None)

    if phone_number is not None:
        existing_employees = Employee.objects.filter(mobile_number=phone_number).exclude(id=id)
        if existing_employees:
            return Response(
                {
                    'status': False,
                    'status_code': 404,
                    'status_code_text': '404',
                    'response': {
                        'message': f'Employee already exist with this phone number.',
                        'error_message': None,
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            employee.mobile_number = phone_number
    else:
        employee.mobile_number = None
    if image is not None:
        employee.image = image

    if is_active is not None:
        current_date = timezone.now().date()
        check_exists = EmployeDailySchedule.objects.filter(
            employee_id=employee.id,
            from_date__gte=current_date

        ).exclude(is_holiday=True)
        if check_exists:
            return Response(
                {
                    'status': True,
                    'status_code': 402,
                    'response': {
                        'message': 'Active schedule1. Adjust or ensure coverage before InActive.',
                        'error_message': 'Active schedule1. Adjust or ensure coverage before InActive.',
                    },
                    'data': Allscedulae(check_exists, many=True).data
                },
                status=402
            )
        else:
            pass
        current_date = timezone.now().date()
        qs = AppointmentService.objects.filter(member_id=employee, created_at__date__gte=current_date)
        if qs:
            return Response(
                {
                    'status': True,
                    'status_code': 402,
                    'response': {
                        'message': ' Employee cannot be marked as inactive until all bookings are completed or canceled.',
                        'error_message': 'Employee cannot be marked as inactive until all bookings are completed or canceled.',
                    }
                },
                status=402
            )

        else:
            pass
        employee.is_active = True
        employee.in_active_date = None
    else:
        current_date = timezone.now().date()
        check_exists = EmployeDailySchedule.objects.filter(
            employee_id=employee.id,
            from_date__gte=current_date
        ).exclude(is_holiday=True)
        if check_exists:

            return Response(
                {
                    'status': True,
                    'status_code': 402,
                    'response': {
                        'message': 'Active schedule2. Adjust or ensure coverage before InActive.',
                        'error_message': 'Active schedule3. Adjust or ensure coverage before InActive.',
                    }
                    ,
                    'data':Allscedulae(check_exists,many=True).data
                },
                status=402
            )
        else:
            pass
        current_date = timezone.now().date()
        qs = AppointmentService.objects.filter(member_id=employee, created_at__date__gte=current_date)
        if qs:
            return Response(
                {
                    'status': True,
                    'status_code': 402,
                    'response': {
                        'message': ' Employee cannot be marked as inactive until all bookings are completed or canceled.',
                        'error_message': 'Employee cannot be marked as inactive until all bookings are completed or canceled.',
                    }
                },
                status=402
            )
        else:
            pass
        employee.is_active = False
        employee.in_active_date = timezone.now().date()

    employee.can_refunds = can_refund
    employee.save()

    if country_unique_id is not None:
        public_country = get_country_from_public(country_unique_id)
        country, created = Country.objects.get_or_create(
            name=public_country.name,
            unique_id=public_country.unique_id
        )
        employee.country = country

    if state_unique_id is not None:
        public_state = get_state_from_public(state_unique_id)
        state, created = State.objects.get_or_create(
            name=public_state.name,
            unique_id=public_state.unique_id
        )
        employee.state = state

    if city_name is not None:
        city, created = City.objects.get_or_create(name=city_name,
                                                   country=country,
                                                   state=state,
                                                   country_unique_id=country_unique_id,
                                                   state_unique_id=state_unique_id)
        employee.city = city

    employee.save()

    Employe_Informations = EmployeeProfessionalInfo.objects.get(employee=employee)

    Employe_Informations.monday = True if 'monday' in request.data else False
    Employe_Informations.tuesday = True if 'tuesday' in request.data else False
    Employe_Informations.wednesday = True if 'wednesday' in request.data else False
    Employe_Informations.thursday = True if 'thursday' in request.data else False
    Employe_Informations.friday = True if 'friday' in request.data else False
    Employe_Informations.saturday = True if 'saturday' in request.data else False
    Employe_Informations.sunday = True if 'sunday' in request.data else False

    if services_id is not None:
        if type(services_id) == str:
            services_id = services_id.replace("'", '"')
            services_id = json.loads(services_id)
        else:
            pass
        for services in services_id:
            # get('id', None)
            s_service_id = services.get('id', None)
            if s_service_id is not None:
                try:
                    emp_service = EmployeeSelectedService.objects.get(id=services['id'])
                    is_deleted = services.get('is_deleted', None)
                    if is_deleted is not None:
                        emp_service.delete()
                        continue

                    ser = Service.objects.get(id=services['service'])
                    emp_service.service = ser
                    emp_service.level = services['level']
                    emp_service.save()
                except Exception as error:
                    print(f'EmployeeSelectedService item {error}')

            else:
                ser = Service.objects.get(id=services['service'])

                emp_service = EmployeeSelectedService.objects.create(
                    employee=employee,
                    service=ser,
                    level=services['level']
                )

    Employe_Informations.save()
    serializer_info = EmployeInformationsSerializer(Employe_Informations, data=request.data, partial=True)
    if serializer_info.is_valid():
        serializer_info.save()
        data.update(serializer_info.data)

    else:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_INFORMATION_4026,
                'response': {
                    'message': 'Invalid Data',
                    'error_message': str(serializer_info.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        empl_permission, created = EmployePermission.objects.get_or_create(employee=employee)

        for permit in ALL_PERMISSIONS:
            value = request.data.get(permit, None)

            if value is not None:
                PERMISSIONS_MODEL_FIELDS[permit](empl_permission).clear()
                try:
                    value = json.loads(value)
                except (TypeError, json.JSONDecodeError, AttributeError) as e:
                    print(f"Error parsing value '{value}' for permit '{permit}': {e}")
                else:
                    for opt in value:
                        try:
                            option = GlobalPermissionChoices.objects.filter(text=opt).first()
                            PERMISSIONS_MODEL_FIELDS[permit](empl_permission).add(option)
                        except GlobalPermissionChoices.DoesNotExist:
                            pass


    except (TypeError, json.JSONDecodeError, AttributeError) as err:  # Exception as err:
        Errors.append(err)

    if location is not None:
        try:
            employee.location.clear()
            address = BusinessAddress.objects.get(id=str(location))
            employee.location.add(address)
        except Exception as err:
            Errors.append(err)
            print(err)

    serializer = EmployeSerializer(employee, data=request.data, partial=True, context={'request': request, })
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(
            {
                'status': True,
                'status_code': 200,
                'response': {
                    'message': ' Employee updated successfully',
                    'error_message': 'Error in saving Employee',
                    'Employee': data,
                    'lev_id': lev_id
                }
            },
            status=status.HTTP_200_OK
        )

    data.update(serializer.data)
    if email_changed:
        user = User.objects.filter(email=old_email).first()
        if user:
            user.email = emp_email
            user.save()

        # also changing email from public schema
        # pub_tenant = Tenant.objects.get(schema_name='public')
        # with tenant_context(pub_tenant):
        connection.set_schema_to_public()
        public_user = User.objects.filter(email=old_email).first()
        if public_user:
            public_user.email = emp_email
            public_user.save()

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': ' Employee updated successfully',
                'error_message': Errors,
                'Employee': data,
                'old_email': old_email,
                'new_email': emp_email
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_employee_device(request):
    # sourcery skip: avoid-builtin-shadow
    id = request.data.get('id', None)
    full_name = request.data.get('full_name', None)

    country_unique_id = request.data.get('country', None)
    state_unique_id = request.data.get('state', None)
    city_name = request.data.get('city', None)
    phone_number = request.data.get('mobile_number', None)
    image = request.data.get('image', None)
    postal_code = request.data.get('postal_code', None)
    address = request.data.get('address', None)

    city_state = None
    city_country = None

    Errors = []

    if id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'User id is required',
                    'fields': [
                        'id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        employee = Employee.objects.get(id=id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
                'status_code_text': 'INVALID_NOT_FOUND_EMPLOYEE_ID_4022',
                'response': {
                    'message': 'Employee Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    is_mobile_exist_already = Employee.objects.filter(mobile_number=phone_number).exclude(id=employee.id)
    if is_mobile_exist_already:
        if phone_number == is_mobile_exist_already[0].mobile_number:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
                    'status_code_text': 'INVALID_NOT_FOUND_EMPLOYEE_ID_4022',
                    'response': {
                        'message': 'Mobile no already exist.',
                    }
                },
                status=status.HTTP_200_OK
            )

    employee.full_name = full_name
    employee.mobile_number = phone_number
    employee.postal_code = postal_code
    employee.address = address

    if image is not None:
        employee.image = image

    if country_unique_id is not None:
        public_country = get_country_from_public(country_unique_id)
        if public_country:
            country, created = Country.objects.get_or_create(
                name=public_country.name,
                unique_id=public_country.unique_id
            )
            employee.country = country
            city_country = country
        else:
            employee.country = None

    if state_unique_id is not None:
        public_state = get_state_from_public(state_unique_id)
        if public_state:
            state, created = State.objects.get_or_create(
                name=public_state.name,
                unique_id=public_state.unique_id
            )
            employee.state = state
            city_state = state
        else:
            employee.state = None

    if city_name is not None:
        city, created = City.objects.get_or_create(name=city_name,
                                                   country=city_country,
                                                   state=city_state,
                                                   country_unique_id=country_unique_id if country_unique_id else None,
                                                   state_unique_id=state_unique_id if state_unique_id else None
                                                   )
        employee.city = city

    employee.save()

    employee.save()
    serializer = EmployeSerializer(employee, context={'request': request, })
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': ' Employee updated successfully',
                'error_message': Errors,
                'Employee': serializer.data
            }
        },
        status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def delete_all_employees(request):
    all_employees = Employee.objects.all()

    for empl in all_employees:
        empl.delete()
    return Response({'deleted': True})


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_staff_group(request):
    user = request.user
    staff_csv = request.data.get('file', None)
    business_id = request.data.get('business', None)

    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            }
        )

    file = NstyleFile.objects.create(
        file=staff_csv
    )
    with open(file.file.path, 'r', encoding='utf-8') as imp_file:
        for index, row in enumerate(imp_file):
            if index == 0:
                continue
            row = row.split(',')
            row = row

            if len(row) < 2:
                continue
            name = row[0].strip('"')
            active = row[1].replace('\n', '').strip('"')

            if active == 'Active':
                active = True
            else:
                active = False

            staff_group = StaffGroup.objects.create(
                user=user,
                business=business,
                name=name,
                is_active=active,
            )

    file.delete()
    return Response({'Status': 'Success'})


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_staff_group(request):
    user = request.user
    business_id = request.data.get('business', None)

    name = request.data.get('name', None)
    employees = request.data.get('employees', None)

    is_active = request.data.get('is_active', None)

    access_reports = request.data.get('access_reports', True)
    access_sales = request.data.get('access_sales', False)
    access_inventory = request.data.get('access_inventory', False)
    access_expenses = request.data.get('access_expenses', True)
    access_products = request.data.get('access_products', False)

    if not all([business_id, name, employees]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                        'name',
                        'employees',
                        'access_reports',
                        'access_sales',
                        'access_inventory',
                        'access_expenses',
                        'access_products'

                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            }
        )
    if is_active is not None:
        #     is_active= json.loads(is_active)
        is_active = True
    else:
        is_active = False

    staff_group = StaffGroup.objects.create(
        user=user,
        business=business,
        name=name,
        is_active=is_active,

    )

    # StaffGroupModulePermission
    # staff_module_permission= StaffGroupModulePermission.objects.create(
    #     staff_group=staff_group,
    #     access_reports=access_reports,
    #     access_sales=access_sales,
    #     access_inventory=access_inventory,
    #     access_expenses=access_expenses,
    #     access_products=access_products,
    # )
    # staff_permission_serializers =  StaffpermisionSerializers(staff_module_permission)
    employees_error = []

    if type(employees) == str:
        employees = json.loads(employees)

    elif type(employees) == list:
        pass

    for usr in employees:
        try:
            employe = Employee.objects.get(id=usr)
            print(employe)
            staff_group.employees.add(employe)
        except Exception as err:
            employees_error.append(str(err))

    staff_permission = EmployePermission.objects.create(staffgroup=staff_group)
    for permit in ALL_PERMISSIONS:
        value = request.data.get(permit, None)
        if value is not None:
            if type(value) == str:
                value = json.loads(value)
            for opt in value:
                try:
                    option = GlobalPermissionChoices.objects.get(text=opt)
                except:
                    pass
                else:
                    PERMISSIONS_MODEL_FIELDS[permit](staff_permission).add(option)

                    for empl in staff_group.employees.all():
                        try:
                            staff_group_employee_prmit = EmployePermission.objects.get(employee=empl.id)
                        except:
                            continue
                        else:
                            PERMISSIONS_MODEL_FIELDS[permit](staff_group_employee_prmit).add(option)
                            staff_group_employee_prmit.save()

    staff_permission.save()

    staff_group.save()
    serialized = StaffGroupSerializers(staff_group, context={'request': request})

    data = dict()
    data.update(serialized.data)
    try:
        data.update(data['staff_permission'])
        del data['staff_permission']
    except Exception as err:
        print(err)
    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Staff Group Create!',
                'error_message': None,
                'StaffGroup': data,
                'staff_errors': employees_error,
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_staff_group(request):
    search_text = request.GET.get('search_text', None)
    no_pagination = request.GET.get('no_pagination', None)

    query = Q(employees__is_deleted=False)

    if search_text:
        query &= Q(name__icontains=search_text)
    all_staff_group = StaffGroup.objects \
        .filter(query) \
        .prefetch_related('employees') \
        .order_by('-created_at').distinct()
    all_staff_group_count = all_staff_group.count()

    page_count = all_staff_group_count / 10
    if page_count > int(page_count):
        page_count = int(page_count) + 1

    per_page_results = 10000 if no_pagination else 10
    paginator = Paginator(all_staff_group, per_page_results)
    page_number = request.GET.get("page")
    all_staff_group = paginator.get_page(page_number)

    serialized = StaffGroupSerializers(all_staff_group, many=True, context={'request': request})

    data = serialized.data

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Staff Group',
                'count': all_staff_group_count,
                'pages': page_count,
                'per_page_result': per_page_results,
                'error_message': None,
                'staff_group': data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_staff_group(request):
    staff_id = request.data.get('staff_id', None)
    if staff_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'fields are required.',
                    'fields': [
                        'staff_id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        employee = StaffGroup.objects.get(id=staff_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Employee ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    employee.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Staff Group deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_staff_group(request):
    staff_id = request.data.get('staff_id', None)
    employees_error = []
    if staff_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Staff ID are required.',
                    'fields': [
                        'staff_id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        staff_group = StaffGroup.objects.get(id=staff_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_STAFF_GROUP_4028,
                'status_code_text': 'INVALID_STAFF_GROUP_4028',
                'response': {
                    'message': 'Staff Group Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    data = {}

    employees = request.data.get('employees', None)
    if employees is not None:
        if type(employees) == str:
            employees = json.loads(employees)
        elif type(employees) == list:
            pass
        staff_group.employees.clear()
        for usr in employees:
            try:
                employe = Employee.objects.get(id=usr)
                print(employe)
                staff_group.employees.add(employe)
            except Exception as err:
                employees_error.append(str(err))
        staff_group.save()

    staff_permission = EmployePermission.objects.get(staffgroup=staff_group)
    for permit in ALL_PERMISSIONS:
        value = request.data.get(permit, None)
        PERMISSIONS_MODEL_FIELDS[permit](staff_permission).clear()
        if value is not None:
            if type(value) == str:
                value = json.loads(value)
            for opt in value:
                try:
                    option = GlobalPermissionChoices.objects.get(text=opt)
                except:
                    pass
                else:
                    PERMISSIONS_MODEL_FIELDS[permit](staff_permission).add(option)

                    for empl in staff_group.employees.all():
                        try:
                            staff_group_employee_prmit = EmployePermission.objects.get(employee=empl.id)
                        except:
                            continue
                        else:
                            PERMISSIONS_MODEL_FIELDS[permit](staff_group_employee_prmit).add(option)
                            staff_group_employee_prmit.save()

    staff_permission.save()

    # permission_serializer =StaffpermisionSerializers(staff_gp_permissions, data=request.data, partial=True, context={'request' : request})
    # if permission_serializer.is_valid():
    #     permission_serializer.save()
    #     data.update(permission_serializer.data)
    # else:
    #      return Response(
    #         {
    #             'status' : False,
    #             'status_code' : StatusCodes.INVALID_EMPLOYEE_INFORMATION_4026,
    #             'response' : {
    #                 'message' : 'Invalid Data',
    #                 'error_message' : str(permission_serializer.errors),
    #             }
    #         },
    #         status=status.HTTP_404_NOT_FOUND
    #  )
    serializer = StaffGroupSerializers(staff_group, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        # data.update(serializer.data)
    else:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.SERIALIZER_INVALID_4024,
                'response': {
                    'message': 'Staff Group Serializer Invalid',
                    'error_message': str(serializer.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Update Staff Group Successfully',
                'error_message': None,
                'StaffGroupUpdate': serializer.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_attendence(request):
    location_id = request.GET.get('location', None)
    search_text = request.GET.get('search_text', None)
    no_pagination = request.GET.get('no_pagination', None)
    employee_id = request.GET.get('employee_id', None)

    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    leo_day = request.GET.get('leo_day', None)

    query = Q(is_deleted=False)
    query &= Q(is_blocked=False)
    query &= Q(location__id=location_id)

    if employee_id:
        query &= Q(id=str(employee_id))

    if search_text:
        query &= Q(full_name__icontains=search_text)

    all_employe = Employee.objects.filter(query) \
        .with_total_commission() \
        .with_total_tips() \
        .order_by('-created_at')
    all_employe_count = all_employe.count()

    page_count = all_employe_count / 10
    if page_count > int(page_count):
        page_count = int(page_count) + 1

    per_page_results = 10000 if no_pagination else 10
    paginator = Paginator(all_employe, per_page_results)
    page_number = request.GET.get("page")
    all_employe = paginator.get_page(page_number)

    serialized = Payroll_WorkingScheduleSerializer(all_employe, many=True,
                                                   context={'request': request, 'start_date': start_date,
                                                            'leo_day': leo_day,
                                                            'end_date': end_date})

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Attendance',
                'count': all_employe_count,
                'pages': page_count,
                'per_page_result': per_page_results,
                'error_message': None,
                'attendance': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_attendence_device(request):
    employee_id = request.GET.get('employee_id', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    if not all([employee_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Employee id are required',
                    'fields': [
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
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'status_code_text': 'INVALID_EMPLOYEE_4025',
                'response': {
                    'message': 'Employee Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    all_employe = Employee.objects.get(id=employee_id.id, is_deleted=False,
                                       is_blocked=False)  # .order_by('-created_at')
    serialized = Payroll_Working_device_attendence_ScheduleSerializer(all_employe, context={
        'request': request,
        'range_start': start_date,
        'range_end': end_date,
    })
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Attendance',
                'error_message': None,
                'attendance': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_attendence(request):
    user = request.user
    business = request.data.get('business', None)
    employees = request.data.get('employees', None)
    is_active = request.data.get('is_active', False)
    in_time = request.data.get('in_time', None)
    out_time = request.data.get('out_time', None)

    if not all([business, employees, in_time]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                        'employees',
                        'in_time',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business_id = Business.objects.get(id=business)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        employee_id = Employee.objects.get(id=employees)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'response': {
                    'message': 'Employee not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    attendence_employe = Attendance.objects.create(
        user=user,
        business=business_id,
        employee=employee_id,
        in_time=in_time,
        out_time=out_time,
        is_active=is_active,
    )

    attendece_serializers = AttendanceSerializers(attendence_employe, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Attendence Created Successfully!',
                'error_message': None,
                'attendence': attendece_serializers.data,
            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_attendence(request):
    attendence_id = request.data.get('attendence_id', None)
    if attendence_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Attendence ID are required.',
                    'fields': [
                        'attendence_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        attendence = Attendance.objects.get(id=attendence_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_ATTENDENCE_ID_OR_NOT_FOUND_4029,
                'status_code_text': 'INVALID_ATTENDENCE_ID_OR_NOT_FOUND_4029',
                'response': {
                    'message': 'Attendence Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = AttendanceSerializers(attendence, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.SERIALIZER_INVALID_4024,
                'response': {
                    'message': 'Attendence Serializer Invalid',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    serializer.save()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Update Attendence Successfully',
                'error_message': None,
                'StaffGroupUpdate': serializer.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_attendence(request):
    attendence_id = request.data.get('attendence_id', None)
    if attendence_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'fields are required!',
                    'fields': [
                        'attendence_id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        attendence = Attendance.objects.get(id=attendence_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Attendance ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    attendence.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Attendance deleted successful',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_payrolls(request):
    all_payroll = Payroll.objects.all()
    serialized = PayrollSerializers(all_payroll, many=True)
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Payroll',
                'error_message': None,
                'payroll': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_payroll(request):
    payroll_id = request.data.get('payroll_id', None)
    if payroll_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'fields are required!',
                    'fields': [
                        'payroll_id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        payroll = Payroll.objects.get(id=payroll_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Payroll ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    payroll.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Payroll deleted successful',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_sallaryslip(request):
    user = request.user

    business = request.data.get('business', None)
    employees = request.data.get('employees', None)
    month = request.data.get('month', None)
    year = request.data.get('year', None)

    if not all([business, employees, month]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                        'employees',
                        'name',
                        'Total_hours'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business_id = Business.objects.get(id=business)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        employee_id = Employee.objects.get(id=employees)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'response': {
                    'message': 'Employee not found',
                    'error_message': str(err),
                }
            }
        )
    received_data = f'{month} {year}'

    month = datetime.datetime.strptime(received_data, "%B %Y").month
    year = datetime.datetime.strptime(received_data, "%B %Y").year
    date_obj = datetime.date(year=year, month=month, day=1)

    payroll = SallarySlipPayrol.objects.create(
        user=user,
        business=business_id,
        employee=employee_id,
        month=date_obj
    )
    payroll_serializers = SallarySlipPayrolSerializers(payroll)

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Sallary Slip Created Successfully!',
                'error_message': None,
                'StaffGroup': payroll_serializers.data,
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_payrol_working(request):
    location_id = request.GET.get('location', None)
    employee_id = request.GET.get('employee_id', None)
    start_date = request.GET.get('start_date', None)  # '2023-07-01'
    end_date = request.GET.get('end_date', None)
    no_pagination = request.GET.get('no_pagination', None)

    query = Q(is_deleted=False, is_blocked=False)

    if location_id:
        query &= Q(location=location_id)

    if employee_id:
        query &= Q(id__in=[employee_id])

    all_employe = Employee.objects.filter(query) \
        .with_total_commission() \
        .with_total_tips()
    # .order_by('employee_employedailyschedule__date')
    all_employe_count = all_employe.count()

    results_per_page = 10000 if no_pagination else 10
    page_count = all_employe_count / 10
    if page_count > int(page_count):
        page_count = int(page_count) + 1

    paginator = Paginator(all_employe, results_per_page)
    page_number = request.GET.get("page")
    all_employe = paginator.get_page(page_number)

    serialized = Payroll_WorkingScheduleSerializerOP(all_employe, many=True,
                                                     context={'request': request, 'start_date': start_date,
                                                              'end_date': end_date})

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Employee',
                'count': all_employe_count,
                'pages': page_count,
                'per_page_result': results_per_page,
                'error_message': None,
                'employees': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_payrol_working_device(request):
    employee_id = request.GET.get('employee_id', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    if not all([employee_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Employee id are required',
                    'fields': [
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
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'status_code_text': 'INVALID_EMPLOYEE_4025',
                'response': {
                    'message': 'Employee Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    all_employe = Employee.objects.get(id=employee_id.id, is_deleted=False,
                                       is_blocked=False)  # .order_by('-created_at')
    serialized = Payroll_Working_deviceScheduleSerializer(all_employe, context={
        'request': request,
        'range_start': start_date,
        'range_end': end_date,
    })

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Employee',
                'error_message': None,
                'employees': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_payroll(request):
    payroll_id = request.data.get('payroll_id', None)
    if payroll_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'fields are required!',
                    'fields': [
                        'payroll_id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        payroll = Payroll.objects.get(id=payroll_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Payroll ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    payroll.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Payroll deleted successful',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_commission(request):
    user = request.user
    business_id = request.data.get('business', None)

    employee = request.data.get('employee', None)
    commission_cycle = request.data.get('commission_cycle', None)

    service_comission = request.data.get('service_comission', None)
    product_comission = request.data.get('product_comission', None)
    voucher_comission = request.data.get('voucher_comission', None)

    if not all([business_id, employee]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                        'employee'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        employee_id = Employee.objects.get(id=employee)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'response': {
                    'message': 'Employee not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    commission_setting = CommissionSchemeSetting.objects.create(
        user=user,
        business=business,
        employee=employee_id,
        commission_cycle=commission_cycle,
    )

    if service_comission is not None:
        if type(service_comission) == str:
            # service_comission = service_comission.replace("'" , '"')
            service_comission = json.loads(service_comission)

        elif type(service_comission) == list:
            pass

        for ser in service_comission:
            try:
                from_value = ser.get('from_value', None)
                to_value = ser.get('to_value', None)
                commission_per = ser.get('commission', None)
                symbol = ser.get('symbol', None)

                # from_value = service_comission['from_value'] #ser.get('from_value', None)
                # to_value = service_comission['to_value'] #ser.get('to_value', None)
                # commission_per = service_comission['commission_percentage'] #ser.get('commission', None)

                CategoryCommission.objects.create(
                    commission=commission_setting,
                    from_value=from_value,
                    to_value=to_value,
                    commission_percentage=commission_per,
                    symbol=symbol,
                    category_comission='Service',
                    comission_choice='percentage' if '%' in symbol else 'currency'
                )
            except Exception as err:
                ExceptionRecord.objects.create(
                    text=f'Service data {str(err)}'
                )

    if product_comission is not None:
        if type(product_comission) == str:
            # product_comission = product_comission.replace("'" , '"')
            product_comission = json.loads(product_comission)

        elif type(product_comission) == list:
            pass

        for pro in product_comission:
            try:
                from_value = pro.get('from_value', None)
                to_value = pro.get('to_value', None)
                commission_per = pro.get('commission', None)
                symbol = pro.get('symbol', None)

                # from_value = product_comission['from_value'] #ser.get('from_value', None)
                # to_value = product_comission['to_value'] #ser.get('to_value', None)
                # commission_per = product_comission['commission_percentage'] #ser.get('commission', None)

                CategoryCommission.objects.create(
                    commission=commission_setting,
                    from_value=from_value,
                    to_value=to_value,
                    commission_percentage=commission_per,
                    symbol=symbol,
                    category_comission='Retail',
                    comission_choice='percentage' if '%' in symbol else 'currency'
                )
            except Exception as err:
                ExceptionRecord.objects.create(
                    text=f'Retail data {str(err)}'
                )

    if voucher_comission is not None:

        if type(voucher_comission) == str:
            # voucher_comission = voucher_comission.replace("'" , '"')
            voucher_comission = json.loads(voucher_comission)

        elif type(voucher_comission) == list:
            pass

        for vou in voucher_comission:
            try:
                from_value = vou.get('from_value', None)
                to_value = vou.get('to_value', None)
                commission_per = vou.get('commission', None)
                symbol = vou.get('symbol', None)

                # from_value = voucher_comission['from_value'] #ser.get('from_value', None)
                # to_value = voucher_comission['to_value'] #ser.get('to_value', None)
                # commission_per = voucher_comission['commission_percentage'] #ser.get('commission', None)

                CategoryCommission.objects.create(
                    commission=commission_setting,
                    from_value=from_value,
                    to_value=to_value,
                    commission_percentage=commission_per,
                    symbol=symbol,
                    category_comission='Voucher',
                    comission_choice='percentage' if '%' in symbol else 'currency'
                )
            except Exception as err:
                ExceptionRecord.objects.create(
                    text=f'Both data {str(err)}'
                )

    # Send Notification to Employee
    user = User.objects.filter(email__icontains=employee_id.email).first()
    title = 'Commission'
    body = 'Admin Assigns New Commission'
    NotificationProcessor.send_notifications_to_users(user, title, body, request_user=request.user)

    serializers = CommissionSerializer(commission_setting, context={'request': request})
    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Commission Created Successfully!',
                'error_message': None,
                'commission': serializers.data,
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_commission(request):
    no_pagination = request.GET.get('no_pagination')
    search_text = request.GET.get('search_text')
    location_id = request.GET.get('location_id', None)

    query = Q()

    if location_id:
        query &= Q(employee__location__id=location_id)

    if search_text:
        query &= Q(employee__full_name__icontains=search_text)

    commission = CommissionSchemeSetting.objects.filter(
        query
    ).order_by('-created_at')
    commission_count = commission.count()

    page_count = commission_count / 10
    if page_count > int(page_count):
        page_count = int(page_count) + 1

    per_page_results = 10000 if no_pagination else 10
    paginator = Paginator(commission, per_page_results)
    page_number = request.GET.get("page", None)

    if page_number is not None:
        commission = paginator.get_page(page_number)

        serializer = CommissionSerializer(commission, many=True, context={'request': request})

        return Response(
            {
                'status': 200,
                'status_code': '200',
                'response': {
                    'message': f'Page {page_number} Commission',
                    'count': commission_count,
                    'pages': page_count,
                    'per_page_result': per_page_results,
                    'error_message': None,
                    'commission': serializer.data
                }
            },
            status=status.HTTP_200_OK
        )
    else:
        serializer = CommissionSerializer(commission, many=True, context={'request': request})

        return Response(
            {
                'status': 200,
                'status_code': '200',
                'response': {
                    'message': 'All Commission',
                    'count': commission_count,
                    'error_message': None,
                    'commission': serializer.data
                }
            },
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_employee_commission(request):
    employe_id = request.GET.get('id', None)

    if not all([employe_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        employe = Employee.objects.get(id=str(employe_id))
    except Exception as err:
        pass
    try:
        commission = CommissionSchemeSetting.objects.get(employee=employe)
        serializer = CommissionSerializer(commission, context={'request': request})
    except Exception as err:
        return Response(
            {
                'status': False,
                'response': {
                    'message': 'Commission Scheme Setting',
                    'error_message': f'error {str(err)} employee id {employe}',
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All  Employee Commission',
                'error_message': None,
                'commission': serializer.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_commission(request):
    commission_id = request.data.get('id', None)
    if commission_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'fields are required!',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        commission = CommissionSchemeSetting.objects.get(id=commission_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Commission ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    commission.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Commission deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_commision(request):
    commission_id = request.data.get('id', None)

    employee = request.data.get('employee', None)

    service_comission = request.data.get('service_comission', None)
    product_comission = request.data.get('product_comission', None)
    voucher_comission = request.data.get('voucher_comission', None)

    if commission_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'commission_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        commission = CommissionSchemeSetting.objects.get(id=commission_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_COMMISSION_ID_4034,
                'status_code_text': 'INVALID_COMMISSION_ID_4034',
                'response': {
                    'message': 'Attendence Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if service_comission is not None:
        if type(service_comission) == str:
            service_comission = json.loads(service_comission)

        elif type(service_comission) == list:
            pass

        for pro in service_comission:

            from_value = pro.get('from_value', None)
            to_value = pro.get('to_value', None)
            commission_per = pro.get('commission', None)
            isDeleted = pro.get('isDeleted', None)
            symbol = pro.get('symbol', None)
            id = pro.get('id', None)
            if id is not None:
                try:
                    commision_ser = CategoryCommission.objects.get(id=id)
                    if bool(isDeleted) == True:
                        commision_ser.delete()
                        pass

                    commision_ser.from_value = from_value
                    commision_ser.to_value = to_value
                    commision_ser.commission_percentage = commission_per
                    commision_ser.symbol = symbol
                    commision_ser.comission_choice = 'percentage' if '%' in symbol else 'currency'
                    commision_ser.save()

                except Exception as err:
                    pass
            else:
                CategoryCommission.objects.create(
                    commission=commission,
                    from_value=from_value,
                    to_value=to_value,
                    commission_percentage=commission_per,
                    symbol=symbol,
                    category_comission='Service',
                    comission_choice='percentage' if '%' in symbol else 'currency'
                )

    if product_comission is not None:
        if type(product_comission) == str:
            product_comission = json.loads(product_comission)

        elif type(product_comission) == list:
            pass

        for pro in product_comission:

            from_value = pro.get('from_value', None)
            to_value = pro.get('to_value', None)
            commission_per = pro.get('commission', None)
            isDeleted = pro.get('isDeleted', None)
            symbol = pro.get('symbol', None)
            id = pro.get('id', None)
            if id is not None:
                try:
                    commision_ser = CategoryCommission.objects.get(id=id)
                    if bool(isDeleted) == True:
                        commision_ser.delete()
                        pass

                    commision_ser.from_value = from_value
                    commision_ser.to_value = to_value
                    commision_ser.commission_percentage = commission_per
                    commision_ser.symbol = symbol
                    commision_ser.comission_choice = 'percentage' if '%' in symbol else 'currency'
                    commision_ser.save()

                except Exception as err:
                    pass
            else:
                CategoryCommission.objects.create(
                    commission=commission,
                    from_value=from_value,
                    to_value=to_value,
                    commission_percentage=commission_per,
                    symbol=symbol,
                    category_comission='Retail',
                    comission_choice='percentage' if '%' in symbol else 'currency'
                )

    if voucher_comission is not None:
        if type(voucher_comission) == str:
            voucher_comission = voucher_comission.replace("'", '"')
            voucher_comission = json.loads(voucher_comission)

        elif type(voucher_comission) == list:
            pass

        for pro in voucher_comission:
            from_value = pro.get('from_value', None)
            to_value = pro.get('to_value', None)
            commission_per = pro.get('commission', None)
            isDeleted = pro.get('isDeleted', None)
            symbol = pro.get('symbol', None)
            id = pro.get('id', None)
            if id is not None:
                try:
                    commision_ser = CategoryCommission.objects.get(id=id)
                    if bool(isDeleted) == True:
                        commision_ser.delete()
                        pass

                    commision_ser.from_value = from_value
                    commision_ser.to_value = to_value
                    commision_ser.commission_percentage = commission_per
                    commision_ser.symbol = symbol
                    commision_ser.comission_choice = (
                        'percentage' if '%' in symbol else 'currency') if symbol else 'currency'
                    commision_ser.save()

                except Exception as err:
                    print(str(err))
            else:
                CategoryCommission.objects.create(
                    commission=commission,
                    from_value=from_value,
                    to_value=to_value,
                    commission_percentage=commission_per,
                    symbol=symbol,
                    category_comission='Voucher',
                    comission_choice='percentage' if '%' in symbol else 'currency'
                )
    try:
        employee_id = Employee.objects.get(id=employee)
        commission.employee = employee_id
        commission.save()
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'response': {
                    'message': 'Employee not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        request.data._mutable = True
    except:
        pass

    del request.data['commission_cycle']

    serializer = CommissionSerializer(commission, data=request.data, partial=True, context={'request': request})
    if not serializer.is_valid():
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.SERIALIZER_INVALID_4024,
                'response': {
                    'message': 'Commission Serializer Invalid',
                    'error_message': serializer.error_messages,
                    'errors': serializer.errors,
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    serializer.save()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Update Commission Successfully',
                'error_message': None,
                'commission': serializer.data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_asset(request):
    user = request.user
    business_id = request.data.get('business', None)

    name = request.data.get('name', None)
    employee_id = request.data.get('employee', None)
    given_date = request.data.get('given_date', None)
    return_date = request.data.get('return_date', None)

    is_active = request.data.get('is_active', None)
    document = request.FILES.getlist('document', None)

    if not all([business_id, name, employee_id, given_date, document]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                        'name',
                        'employee',
                        'given_date',
                        'document',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            }
        )
    if is_active is not None:
        is_active = True
    else:
        is_active = False

    try:
        employee = Employee.objects.get(id=employee_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
                'status_code_text': 'INVALID_NOT_FOUND_EMPLOYEE_ID_4022',
                'response': {
                    'message': 'Employee Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    asset = Asset.objects.create(
        user=user,
        business=business,
        employee=employee,
        name=name,
        given_date=given_date,
        return_date=return_date,
        is_active=is_active
    )
    if document is not None:
        for doc in document:
            doc = AssetDocument.objects.create(
                asset=asset,
                document=doc
            )
    serializers = AssetSerializer(asset, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Asset Created Successfully!',
                'error_message': None,
                'asset': serializers.data,
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_asset(request):
    all_asset = Asset.objects.all().order_by('created_at')
    serialized = AssetSerializer(all_asset, many=True, context={'request': request})
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Assets',
                'error_message': None,
                'asset': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_asset(request):
    asset_id = request.data.get('id', None)
    if asset_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'fields are required!',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        asset = Asset.objects.get(id=asset_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Asset ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    asset.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Asset deleted successful',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_asset(request):
    asset_id = request.data.get('id', None)
    staff_id = request.data.get('staff_id', None)
    document = request.data.get('document', None)
    is_active = request.data.get('is_active', None)

    if asset_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'fields are required!',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        asset = Asset.objects.get(id=asset_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Asset ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if staff_id is not None:
        try:
            emp = Employee.objects.get(id=staff_id)
            asset.employee = emp
        except Exception as err:
            pass
    if is_active is not None:
        asset.is_active = True
    else:
        asset.is_active = False

    if document is not None:
        try:
            docs = AssetDocument.objects.filter(asset=asset)
            for d in docs:
                d.delete()
        except:
            pass
        # for doc in document:
        doc = AssetDocument.objects.create(
            asset=asset,
            document=document
        )
    serializer = AssetSerializer(asset, data=request.data, partial=True, context={'request': request})
    if not serializer.is_valid():
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.SERIALIZER_INVALID_4024,
                'response': {
                    'message': 'Asset Serializer Invalid',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    serializer.save()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Update Asset Successfully',
                'error_message': None,
                'asset': serializer.data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_vacation(request):
    user = request.user
    business_id = request.data.get('business', None)

    employee = request.data.get('employee', None)
    from_date = request.data.get('from_date', None)
    to_date = request.data.get('to_date', None)
    note = request.data.get('note', None)

    if not all([business_id, employee]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                        'employee'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        employee_id = Employee.objects.get(id=employee)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'response': {
                    'message': 'Employee not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    vacation = Vacation.objects.create(
        user=user,
        business=business,
        employee=employee_id,

        from_date=from_date,
        to_date=to_date,
        note=note,
    )

    serializers = VacationSerializer(vacation, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Vacation Created Successfully!',
                'error_message': None,
                'vacation': serializers.data,
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_vacation(request):
    vacation_id = request.data.get('id', None)
    if vacation_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'fields are required!',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        vacation = Vacation.objects.get(id=vacation_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Vacation ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    vacation.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Vacation deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_vacation(request):
    vacation_id = request.data.get('vacation_id', None)
    employee = request.data.get('employee', None)
    note = request.data.get('note', None)

    if vacation_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'vacation_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        vacation = Vacation.objects.get(id=vacation_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code_text': 'INVALID_VACATION_ID',
                'response': {
                    'message': 'Vacation Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if employee is not None:
        try:
            emp = Employee.objects.get(id=employee)
            vacation.employee = emp
        except Exception as err:
            pass
    if note is not None:
        vacation.note = note

    vacation.save()
    serializer = VacationSerializer(vacation, data=request.data, partial=True, context={'request': request})
    if not serializer.is_valid():
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.SERIALIZER_INVALID_4024,
                'response': {
                    'message': 'Vacation Serializer Invalid',
                    'error_message': serializer.errors,
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    serializer.save()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Vacation Update Successfully',
                'error_message': None,
                'vacation': serializer.data
            }
        },
        status=status.HTTP_200_OK
    )


# @transaction.atomic
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def create_vacation_emp(request):
#     user = request.user
#     business_id = request.data.get('business', None)
#     employee = request.data.get('employee', None)
#     day = request.data.get('day', None)
#     start_time = request.data.get('start_time', None)
#     end_time = request.data.get('end_time', None)
#     start_time_shift = request.data.get('start_time_shift', None)
#     end_time_shift = request.data.get('end_time_shift', None)
#     from_date = request.data.get('from_date', None)
#     to_date = request.data.get('to_date', from_date)
#     note = request.data.get('note', None)
#     is_vacation = request.data.get('is_vacation', None)
#     is_leave = request.data.get('is_leave', None)
#     is_off = request.data.get('is_off', None)
#     vacation_type = request.data.get('vacation_type', None)
#     is_working_schedule = request.data.get('is_working_schedule', None)
#     value = 0
#     difference_days = 0
#     working_sch = None
# 
#     check_leo_day = EmployeDailySchedule.objects.filter(
#         employee=employee,
#         date=from_date,
#         is_leo_day=True
#     )
#     check_weekend = EmployeDailySchedule.objects.filter(
#         employee=employee,
#         date=from_date,
#         is_weekend=True
#     )
#     if check_weekend:
#         return Response(
#             {
#                 'status': 400,
#                 'status_code': 400,
#                 'status_code_text': '400',
#                 'response': {
#                     'message': f'Cannot create vacation on weekend.',
#                     'error_message': None,
#                 }
#             },
# 
#             status=200
#         )
#     if check_leo_day:
#         return Response(
#             {
#                 'status': 400,
#                 'status_code': 400,
#                 'status_code_text': '400',
#                 'response': {
#                     'message': f'Cannot create vacation on leo day.',
#                     'error_message': None,
#                 }
#             },
# 
#             status=200
#         )
#     employee_leave_management_obj = LeaveManagements.objects.get(employee_id=employee)
#     employee_id = Employee.objects.get(id=employee, is_deleted=False)
#     if vacation_type == 'medical':
#         value = employee_leave_management_obj.medical_leave
#     if vacation_type == 'annual':
#         value = employee_leave_management_obj.annual_leave
#         now = datetime.now()
#         created_at = employee_id.created_at
#         required_months = employee_leave_management_obj.number_of_months
#         required_months = int(required_months)
#         months_difference = (now.year - created_at.year) * 12 + now.month - created_at.month
#         months_difference = int(months_difference)
#         if required_months > months_difference:
#             return Response(
#                 {
#                     'status': 400,
#                     'status_code': '400',
#                     'response': {
#                         'message': 'Annual leave requests available after {required_months} months'.format(
#                             required_months=required_months),
#                         'error_message': None,
#                     }
#                 },
#                 status=status.HTTP_200_OK
#             )
#     if vacation_type == 'casual':
#         value = employee_leave_management_obj.casual_leave
#     if vacation_type == 'leo_day':
#         value = employee_leave_management_obj.leo_leave
#     from_date = datetime.strptime(from_date, "%Y-%m-%d")
#     try:
#         to_date = datetime.strptime(to_date, "%Y-%m-%d")
#         diff = to_date - from_date
#         days = int(diff.days)
#     except:
#         days = 0
#     available_value = int(value)
#     if days > available_value:
#         return Response(
#             {
#                 'status': 400,
#                 'status_code': '400',
#                 'response': {
#                     'message': 'Exceeded {vacation_type} quota. Please adjust and retry.'.format(
#                         vacation_type=vacation_type),
#                     'error_message': None,
#                 }
#             },
#             status=status.HTTP_200_OK
#         )
#     # annual_vacation_check(vacation_type=vacation_type, employee=employee_id)
#     if not to_date:
#         to_date = from_date
#     is_vacation_exist = Vacation.objects.filter(
#         business_id=business_id,
#         employee=employee_id,
#         from_date=from_date,
#     ).first()
#     if is_vacation_exist:
#         return Response(
#             {
#                 'status': 400,
#                 'status_code': '400',
#                 'response': {
#                     'message': 'Employee Vacation Already Exist',
#                     'error_message': None,
#                 }
#             },
#             status=status.HTTP_200_OK
#         )
# 
#     empl_vacation = Vacation.objects.create(
#         business_id=business_id,
#         employee_id=employee,
#         from_date=from_date,
#         to_date=to_date,
#         note=note,
#         vacation_status='pending',
#         vacation_type=vacation_type,
#     )
#     try:
#         def process_schedule(employee_id, from_date, to_date, user, business_id, day, start_time, end_time,
#                              start_time_shift,
#                              end_time_shift, note, is_vacation, is_leave, is_off, empl_vacation):
#             schedule_instances = []
#             for i in range(days + 1):
#                 current_date = from_date + timedelta(days=i)
#                 try:
#                     working_sch = EmployeDailySchedule.objects.get(employee=employee_id, date=current_date)
#                     if working_sch:
#                         working_sch.is_vacation = True
#                         working_sch.vacation = empl_vacation
#                         working_sch.from_date = current_date
#                         working_sch.save()
#                 except:
#                     schedule_instance = EmployeDailySchedule(
#                         user=user,
#                         business=business_id,
#                         employee=employee_id,
#                         day=day,
#                         start_time=start_time,
#                         end_time=end_time,
#                         start_time_shift=start_time_shift,
#                         end_time_shift=end_time_shift,
#                         date=current_date,
#                         from_date=current_date,
#                         to_date=to_date,
#                         note=note,
#                         vacation_status='pending',
#                         is_vacation=True
#                     )
#                     schedule_instances.append(schedule_instance)
# 
#                     # Use bulk_create to insert all instances at once
#                 with transaction.atomic():
#                     EmployeDailySchedule.objects.bulk_create(schedule_instances)
#                     # working_schedule = EmployeDailySchedule.objects.create(
#                     #     user=user,
#                     #     business=business,
#                     #     employee=employee_id,
#                     #     day=day,
#                     #     start_time=start_time,
#                     #     end_time=end_time,
#                     #     start_time_shift=start_time_shift,
#                     #     end_time_shift=end_time_shift,
#                     #     date=current_date,
#                     #     from_date=current_date,
#                     #     to_date=to_date,
#                     #     note=note,
#                     #     vacation_status='pending',
#                     #     is_vacation=True
#                     # )
# 
#                     # if is_vacation is not None:
#                     #     working_schedule.is_vacation = True
#                     #     empl_vacation.save()
#                     #     working_schedule.vacation = empl_vacation
#                     # else:
#                     #     working_schedule.is_vacation = False
#                     #
#                     # working_schedule.is_leave = is_leave if is_leave is not None else False
#                     # working_schedule.is_off = is_off if is_off is not None else False
#                     # working_schedule.save()
# 
#         thread = threading.Thread(target=process_schedule,
#                                   args=(employee_id, from_date, to_date, user, business_id, day,
#                                         start_time, end_time, start_time_shift, end_time_shift,
#                                         note, is_vacation, is_leave, is_off, empl_vacation))
#         thread.start()
#         thread.join()
#     except Exception as err:
#         return Response(
#             {
#                 'status': False,
#                 'status_code': 500,
#                 'response': {
#                     'message': 'Internal Server Error',
#                     'error_message': str(err),
#                 }
#             },
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )
#     all_employe = EmployeDailySchedule.objects.select_related('business').order_by('created_at')
#     serialized = ScheduleSerializer(all_employe, many=True, context={'request': request})
# 
#     return Response(
#         {
#             'status': 200,
#             'status_code': '200',
#             'response': {
#                 'message': 'Vacation added successfully',
#                 'error_message': None,
#                 'schedule': serialized.data,
#             }
#         },
#         status=status.HTTP_200_OK
#     )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_vacation_emp(request):
    user = request.user
    business_id = request.data.get('business', None)
    employee = request.data.get('employee', None)
    day = request.data.get('day', None)
    start_time = request.data.get('start_time', None)
    end_time = request.data.get('end_time', None)
    start_time_shift = request.data.get('start_time_shift', None)
    end_time_shift = request.data.get('end_time_shift', None)
    from_date = request.data.get('from_date', None)
    to_date = request.data.get('to_date', from_date)
    note = request.data.get('note', None)
    is_vacation = request.data.get('is_vacation', None)
    is_leave = request.data.get('is_leave', None)
    is_off = request.data.get('is_off', None)
    vacation_type = request.data.get('vacation_type', None)
    is_working_schedule = request.data.get('is_working_schedule', None)
    value = 0
    difference_days = 0
    working_sch = None

    # check_leo_day = EmployeDailySchedule.objects.filter(
    #     employee=employee,
    #     date=from_date,
    #     is_leo_day=True
    # )
    # check_weekend = EmployeDailySchedule.objects.filter(
    #     employee=employee,
    #     date=from_date,
    #     is_weekend=True
    # )
    # check_holiday = EmployeDailySchedule.objects.filter(
    #     employee=employee,
    #     date=from_date,
    #     is_holiday=True
    # )
    # if check_weekend:
    #     return Response(
    #         {
    #             'status': 400,
    #             'status_code': 400,
    #             'status_code_text': '400',
    #             'response': {
    #                 'message': f'Cannot create vacation on weekend.',
    #                 'error_message': None,
    #             }
    #         },
    #         status=200
    #     )
    # if check_holiday:
    #     return Response(
    #         {
    #             'status': 400,
    #             'status_code': 400,
    #             'status_code_text': '400',
    #             'response': {
    #                 'message': f'Cannot create vacation on holiday.',
    #                 'error_message': None,
    #             }
    #         },
    #         status=200
    #     )
    # if check_leo_day:
    #     return Response(
    #         {
    #             'status': 400,
    #             'status_code': 400,
    #             'status_code_text': '400',
    #             'response': {
    #                 'message': f'Cannot create vacation on leo day.',
    #                 'error_message': None,
    #             }
    #         },
    # 
    #         status=200
    #     )

    if not all([business_id, employee]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                        'employee'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        employee_id = Employee.objects.get(id=employee, is_deleted=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'response': {
                    'message': 'Employee not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    employee_leave_management_obj = LeaveManagements.objects.get(employee_id=employee_id.id)
    if vacation_type == 'medical':
        value = employee_leave_management_obj.medical_leave
    if vacation_type == 'annual':
        value = employee_leave_management_obj.annual_leave
        now = datetime.now()
        employee_id = Employee.objects.get(id=employee, is_deleted=False)
        created_at = employee_id.created_at
        employee_leave_management_obj = LeaveManagements.objects.get(employee_id=employee)
        required_months = employee_leave_management_obj.number_of_months
        required_months = int(required_months)
        months_difference = (now.year - created_at.year) * 12 + now.month - created_at.month
        months_difference = int(months_difference)
        if required_months > months_difference:
            return Response(
                {
                    'status': 400,
                    'status_code': '400',
                    'response': {
                        'message': 'Annual leave requests available after {required_months} months'.format(
                            required_months=required_months),
                        'error_message': None,
                    }
                },
                status=status.HTTP_200_OK
            )
    if vacation_type == 'medical':
        value = employee_leave_management_obj.medical_leave
    if vacation_type == 'casual':
        value = employee_leave_management_obj.casual_leave
    if vacation_type == 'leo_day':
        value = employee_leave_management_obj.leo_leave
    from_date = datetime.strptime(from_date, "%Y-%m-%d")
    try:
        to_date = datetime.strptime(to_date, "%Y-%m-%d")
        diff = to_date - from_date
        days = int(diff.days)
    except:
        days = 0
    available_value = int(value)
    if days > available_value:
        return Response(
            {
                'days': days,
                'status': 400,
                'status_code': '400',
                'response': {
                    'message': 'Exceeded {vacation_type} quota. Please adjust and retry.'.format(
                        vacation_type=vacation_type),
                    'error_message': None,
                }
            },
            status=status.HTTP_200_OK
        )

    # check_available_vacation_type(vacation_type=vacation_type, employee=employee, from_date=from_date, to_date=to_date)
    # annual_vacation_check(vacation_type=vacation_type, employee=employee_id)
    if not to_date:
        to_date = from_date

    # from_date = datetime.strptime(from_date, "%Y-%m-%d")
    # to_date = datetime.strptime(to_date, "%Y-%m-%d")
    # diff = to_date - from_date
    # working_sch = None
    # days = int(diff.days)
    is_vacations = Vacation.objects.filter(
        business=business,
        employee=employee_id,
        # from_date=from_date,
        vacation_status='pending'
    )
    if is_vacations:
        return Response(
            {
                'status': 400,
                'status_code': '400',
                'response': {
                    'message': 'Employee vacation is already on pending state',
                    'error_message': None,
                }
            },
            status=status.HTTP_200_OK
        )
    is_vacation_exist = Vacation.objects.filter(
        business=business,
        employee=employee_id,
        from_date=from_date,
    ).first()
    if is_vacation_exist:
        return Response(
            {
                'status': 400,
                'status_code': '400',
                'response': {
                    'message': 'Employee Vacation Already Exist',
                    'error_message': None,
                }
            },
            status=status.HTTP_200_OK
        )
    empl_vacation = Vacation.objects.create(
        business=business,
        employee=employee_id,
        from_date=from_date,
        to_date=to_date,
        note=note,
        vacation_status='pending',
        vacation_type=vacation_type,
    )
    try:
        for i in range(days + 1):
            if i == 0:
                current_date = from_date
            else:
                current_date = from_date + timedelta(days=i)
            # current_date = from_date + timedelta(days=i)
            working_sch = EmployeDailySchedule.objects.filter(employee=employee_id, date=current_date).first()
            if working_sch:
                working_sch.is_vacation = True
                empl_vacation.save()
                working_sch.vacation = empl_vacation
                working_sch.from_date = current_date
                working_sch.save()
            else:
                working_schedule = EmployeDailySchedule.objects.create(
                    vacation=empl_vacation,
                    user=user,
                    business=business,
                    employee=employee_id,
                    day=day,
                    start_time=start_time,
                    end_time=end_time,
                    start_time_shift=start_time_shift,
                    end_time_shift=end_time_shift,
                    date=current_date,
                    from_date=current_date,
                    to_date=to_date,
                    note=note,
                    vacation_status='pending',
                    vacation_type=vacation_type
                )

                if is_vacation is not None:
                    working_schedule.is_vacation = True
                    empl_vacation.save()
                    working_schedule.vacation = empl_vacation
                else:
                    working_schedule.is_vacation = False
                working_schedule.is_leave = is_leave if is_leave is not None else False
                working_schedule.is_off = is_off if is_off is not None else False
                working_schedule.save()
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 500,
                'response': {
                    'message': 'Internal Server Error',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    all_employe = EmployeDailySchedule.objects.select_related('business').order_by('created_at')
    serialized = ScheduleSerializer(all_employe, many=True, context={'request': request})

    return Response(
        {
            'status': 200,
            'vacation_type': vacation_type,
            'available_value': available_value,
            'days': days,
            'status_code': '200',
            'response': {
                'message': 'Vacation added successfully',
                'error_message': None,
                'schedule': serialized.data,
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PATCH'])
@permission_classes([AllowAny])
def update_vacation_status(request):
    try:
        type_of_sceduale = request.data.get('type', None)
        type_of_vacation = request.data.get('type_of_vacation', None)
        business_id = request.data.get('business', None)
        employee = request.data.get('employee', None)
        vacation_id = request.data.get('vacation_id', None)
        vacation_status = request.data.get('vacation_status', None)
        vacation_type = request.data.get('vacation_type', None)
        total_days_to_detect = request.data.get('total_days_to_detect', None)
        created_from_dashboard = request.data.get('created_from_dashboard', None)
        if total_days_to_detect is not None:
            total_days_to_detect = int(total_days_to_detect)
        if vacation_status == 'accepted':
            leave_managements = LeaveManagements.objects.get(employee_id=employee)
            if vacation_type == 'casual':
                if leave_managements.casual_leave == 0:
                    return Response(
                        {
                            'status': 200,
                            'status_code': '200',
                            'response': {
                                'message': 'Cannot update the casual leaves',
                                'error_message': None,
                                'data': []
                            }
                        },
                        status=status.HTTP_200_OK
                    )
                leave_managements.casual_leave -= total_days_to_detect
                leave_managements.used_casual = leave_managements.used_casual + total_days_to_detect
                leave_managements.save()
            if vacation_type == 'annual':
                if leave_managements.annual_leave == 0:
                    return Response(
                        {
                            'status': 200,
                            'status_code': '200',
                            'response': {
                                'message': 'Cannot update the annual_leaves',
                                'error_message': None,
                                'data': []
                            }
                        },
                        status=status.HTTP_200_OK
                    )
                leave_managements.annual_leave -= total_days_to_detect
                leave_managements.used_annual = leave_managements.used_annual + total_days_to_detect
                leave_managements.save()
            if vacation_type == 'medical':
                if leave_managements.medical_leave == 0:
                    return Response(
                        {
                            'status': 200,
                            'status_code': '200',
                            'response': {
                                'message': 'Cannot update the annual_leaves',
                                'error_message': None,
                                'data': []
                            }
                        },
                        status=status.HTTP_200_OK
                    )
                leave_managements.medical_leave -= total_days_to_detect
                leave_managements.used_medical = leave_managements.used_medical + total_days_to_detect
                leave_managements.save()
            if vacation_type == 'leo_day':
                if leave_managements.leo_leave == 0:
                    return Response(
                        {
                            'status': 200,
                            'status_code': '200',
                            'response': {
                                'message': 'Cannot update the annual_leaves',
                                'error_message': None,
                                'data': []
                            }
                        },
                        status=status.HTTP_200_OK
                    )
                leave_managements.leo_leave -= total_days_to_detect
                leave_managements.save()
            vacations = Vacation.objects.filter(id=vacation_id)
            vacations.update(vacation_status='accepted')
            EmployeDailySchedule.objects.filter(vacation_id=vacation_id).update(is_display=True,
                                                                                vacation_status='accepted')
            return Response(
                {
                    'status': 200,
                    'status_code': '200',
                    'response': {
                        'message': 'Vacation updated successfully',
                        'error_message': None,
                        'data': []
                    }
                },
                status=status.HTTP_200_OK
            )
        if vacation_status == 'declined':
            aval_vacations = Vacation.objects.filter(id=vacation_id)
            vacations = Vacation.objects.filter(id=vacation_id)
            vacations.update(vacation_status=vacation_status)
            return Response(
                {
                    'status': 200,
                    'status_code': '200',
                    'response': {
                        'message': 'Vacation updated successfully',
                        'error_message': None,
                        'data': []
                    }
                },
                status=status.HTTP_200_OK
            )
    except Exception as ex:
        error = str(ex)
        return Response({"msg": error})


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_absence(request):
    user = request.user
    business_id = request.data.get('business', None)

    employee = request.data.get('employee', None)
    day = request.data.get('day', None)

    start_time = request.data.get('start_time', None)
    end_time = request.data.get('end_time', None)

    start_time_shift = request.data.get('start_time_shift', None)
    end_time_shift = request.data.get('end_time_shift', None)

    from_date = request.data.get('from_date', None)
    to_date = request.data.get('to_date', from_date)
    note = request.data.get('note', None)

    is_vacation = request.data.get('is_vacation', None)

    is_leave = request.data.get('is_leave', None)
    is_off = request.data.get('is_off', None)

    if not all([business_id, employee]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                        'employee'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        employee_id = Employee.objects.get(id=employee, is_deleted=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'response': {
                    'message': 'Employee not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # from_date ='2023-01-04'
    # to_date ='2023-01-06'
    if not to_date:
        to_date = from_date

    from_date = datetime.strptime(from_date, "%Y-%m-%d")
    to_date = datetime.strptime(to_date, "%Y-%m-%d")
    diff = to_date - from_date
    # print(diff.days)
    working_sch = None
    days = int(diff.days)
    days = days + 1
    print(days)
    empl_absence = Vacation(
        business=business,
        employee=employee_id,
        from_date=from_date.strftime('%Y-%m-%d'),
        to_date=to_date.strftime('%Y-%m-%d'),
        note=note,
        holiday_type='Absence'
    )
    if days > 0:
        for i, value in enumerate(range(days)):
            if i == 0:
                from_date = from_date + timedelta(days=i)
            else:
                from_date = from_date + timedelta(days=1)
            try:
                working_sch = EmployeDailySchedule.objects.get(
                    employee=employee_id,
                    date=from_date.strftime('%Y-%m-%d')
                )
            except Exception as err:
                pass
            print(i)
            print(from_date)
            empl_absence.save()
            if working_sch is not None:
                # date_obj = datetime.fromisoformat(from_date)

                working_sch.is_leave = True

                working_sch.vacation = empl_absence
                working_sch.from_date = from_date.strftime('%Y-%m-%d')
                working_sch.save()

            else:
                working_schedule = EmployeDailySchedule.objects.create(
                    user=user,
                    business=business,
                    employee=employee_id,
                    day=day,
                    start_time=start_time,
                    end_time=end_time,
                    start_time_shift=start_time_shift,
                    end_time_shift=end_time_shift,
                    vacation=empl_absence,
                    date=from_date,
                    from_date=from_date.strftime('%Y-%m-%d'),
                    to_date=to_date.strftime('%Y-%m-%d'),
                    note=note,
                    is_leave=True
                )

                # all_employe= EmployeDailySchedule.objects.all().order_by('created_at')
    serialized = NewAbsenceSerializer(empl_absence, context={'request': request})
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'Vacation added successfully',
                'error_message': None,
                'schedule': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_workingschedule(request):
    check_working_schedule = None
    user = request.user
    business_id = request.data.get('business', None)
    employee = request.data.get('employee', None)
    day = request.data.get('day', None)
    start_time = request.data.get('start_time', None)
    end_time = request.data.get('end_time', None)
    start_time_shift = request.data.get('start_time_shift', None)
    end_time_shift = request.data.get('end_time_shift', None)
    location_id = request.data.get('location_id', None)
    from_date = request.data.get('from_date', None)
    to_date = request.data.get('to_date', None)
    date = request.data.get('date', None)
    note = request.data.get('note', None)
    max_records = 2
    check_holiday = None
    is_vacation = request.data.get('is_vacation', None)
    type_of_sceduale = request.data.get('type', None)
    type_of_vacation = request.data.get('type_of_vacation', None)
    id_to_maintain = request.data.get('id_to_maintain', None)
    is_weekend = request.data.get('is_weekend', None)
    is_leave = request.data.get('is_leave', None)
    is_off = request.data.get('is_off', None)
    leo_value = request.data.get('is_leo_day', None)
    location_for_weekend = request.data.get('location', None)
    is_working_schedule = request.data.get('is_working_schedule', None)
    week_end_employee = request.data.get('week_end_employee', [])
    if is_weekend is not None and leo_value is None and is_working_schedule is None:
        # check_holiday = EmployeDailySchedule.objects.filter(
        #     employee=employee,
        #     from_date=from_date,
        #     is_holiday=True
        # )
        # if check_holiday:
        #     return Response(
        #         {
        #             'status': 400,
        #             'status_code': 400,
        #             'status_code_text': '400',
        #             'response': {
        #                 'message': f'Cannot create weekend on holiday.',
        #                 'error_message': None,
        #             }
        #         },
        #         status=200
        #     )
        week_end_employee = json.loads(week_end_employee)
        schedule_ids = []
        try:
            business = Business.objects.get(id=business_id)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response': {
                        'message': 'Business not found',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        for employee_id in week_end_employee:
            try:
                employee = Employee.objects.get(id=employee_id)
            except:
                return Response(
                    {
                        'status': False,
                        'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                        'response': {
                            'message': 'Employee not found',
                            'error_message': str(err),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            working_sch = EmployeDailySchedule.objects.filter(employee_id=employee, date=date).first()
            if working_sch:
                working_sch.is_weekend = True
                working_sch.location_id = location_for_weekend
                working_sch.save()

                schedule_ids.append(working_sch.id)

            else:
                workings = EmployeDailySchedule.objects.create(
                    location_id=location_for_weekend,
                    user=user,
                    business=business,
                    employee=employee,
                    date=date,
                    is_weekend=True,
                    is_vacation=False,
                    day=day,
                    start_time=start_time,
                    end_time=end_time,
                    start_time_shift=start_time_shift,
                    end_time_shift=end_time_shift,
                    from_date=from_date,
                    to_date=to_date,
                    note=note,
                )
                schedule_ids.append(workings.id)

        working_schedule = EmployeDailySchedule.objects.filter(
            id__in=schedule_ids
        )
        serializers = ScheduleSerializer(working_schedule, context={'request': request}, many=True)
        return Response(
            {
                'check_holiday': check_holiday,
                'status': True,
                'status_code': 201,
                'response': {
                    'message': 'Weekend created successfully across employees!',
                    'error_message': None,
                    'schedule': serializers.data,
                }
            },
            status=status.HTTP_201_CREATED
        )
    if leo_value is not None and is_weekend is None and is_working_schedule is None:
        if not all([business_id, employee]):
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.MISSING_FIELDS_4001,
                    'status_code_text': 'MISSING_FIELDS_4001',
                    'response': {
                        'message': 'Invalid Daata!',
                        'error_message': 'All fields are required.',
                        'fields': [
                            'business',
                            'employee'
                        ]
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            business = Business.objects.get(id=business_id)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response': {
                        'message': 'Business not found',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            employee_id = Employee.objects.get(id=employee, is_deleted=False)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                    'response': {
                        'message': 'Employee Fnot found',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        check_working_schedule = EmployeDailySchedule.objects.filter(
            user=user,
            business=business,
            employee=employee_id,
            date=date,

        )
        record_count = check_working_schedule.count()
        if record_count > max_records:
            return Response(
                {
                    'status': True,
                    'message': 'more than weekends working not allowed',
                    'status_code': 400,
                    'response': {
                        'message': 'more than weekends working not allowed',
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        working_schedule, created = EmployeDailySchedule.objects.get_or_create(
            user=user,
            business=business,
            employee=employee_id,
            date=date,
        )
        working_schedule.day = day
        working_schedule.start_time = start_time
        working_schedule.end_time = end_time
        working_schedule.start_time_shift = start_time
        working_schedule.end_time_shift = end_time
        working_schedule.from_date = date
        working_schedule.to_date = to_date
        working_schedule.note = note
        working_schedule.is_leo_day = True
        working_schedule.is_vacation = False
        working_schedule.is_weekend = False
        working_schedule.vacation_status = None
        working_schedule.save()
        if type_of_sceduale == 'vacation':
            try:
                leave_object = LeaveManagements.objects.get(employee_id=employee_id.id)
            except:
                leave_object = LeaveManagements.objects.create(employee_id=employee_id.id)
            if type_of_vacation == 'casual':
                leave_object.casual_leave += 1
                leave_object.save()
            if type_of_vacation == 'medical':
                leave_object.medical_leave += 1
                leave_object.save()
            if type_of_vacation == 'annual':
                leave_object.annual_leave += 1
                leave_object.save()
        if type_of_sceduale == 'weekend':
            try:
                leave_object = LeaveManagements.objects.get(employee_id=employee_id.id)
            except:
                leave_object = LeaveManagements.objects.create(employee_id=employee_id.id)
            leave_object.leo_leave += 1
            leave_object.save()

        serializers = ScheduleSerializer(working_schedule, context={'request': request})

        return Response(
            {
                'status': True,
                'status_code': 201,
                'response': {
                    'message': 'Working Schedule Created Successfully!',
                    'error_message': None,
                    'schedule': serializers.data,
                    'leo_value': leo_value
                }
            },
            status=status.HTTP_201_CREATED
        )
    if is_working_schedule is not None:
        if not all([business_id, employee]):
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.MISSING_FIELDS_4001,
                    'status_code_text': 'MISSING_FIELDS_4001',
                    'response': {
                        'message': 'Invalid Daata!',
                        'error_message': 'All fields are required.',
                        'fields': [
                            'business',
                            'employee'
                        ]
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            business = Business.objects.get(id=business_id)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response': {
                        'message': 'Business not found',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            employee_id = Employee.objects.get(id=employee, is_deleted=False)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                    'response': {
                        'message': 'Employee not found',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            current_date = timezone.now().date()
            check_exists = EmployeDailySchedule.objects.filter(
                employee_id=employee_id,
                created_at__date__gte=current_date
            )
            # if check_exists:
            #     return Response(
            #         {
            #             'status': False,
            #             'status_code': 404,
            #             'status_code_text': '404',
            #             'response': {
            #                 'message': f'Error',
            #                 'error_message': None,
            #             }
            #         },
            #         status=status.HTTP_404_NOT_FOUND
            #     )

        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response': {
                        'message': 'Business not found',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        check_working_schedule = EmployeDailySchedule.objects.filter(
            user=user,
            business=business,
            employee=employee_id,
            date=date,

        )
        check_leo_day = EmployeDailySchedule.objects.filter(
            employee=employee_id,
            date=date,
            is_leo_day=True
        )
        if check_leo_day:
            return Response(
                {
                    'status': False,
                    'status_code': 404,
                    'status_code_text': '404',
                    'response': {
                        'message': f'Cannot create vacation on leo day.',
                        'error_message': None,
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

        record_count = check_working_schedule.count()
        if record_count > max_records:
            return Response(
                {
                    'status': True,
                    'message': 'more than weekends working not allowed',
                    'status_code': 400,
                    'response': {
                        'message': 'more than weekends working not allowed',
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        working_schedule, created = EmployeDailySchedule.objects.get_or_create(
            user=user,
            business=business,
            employee=employee_id,
            date=date,
        )
        working_schedule.day = day
        working_schedule.start_time = start_time
        working_schedule.end_time = end_time
        working_schedule.start_time_shift = start_time_shift
        working_schedule.end_time_shift = end_time_shift
        working_schedule.from_date = date
        working_schedule.to_date = to_date
        working_schedule.note = note
        working_schedule.is_vacation = False
        working_schedule.vacation_status = None
        working_schedule.is_working_schedule = True
        working_schedule.is_holiday = False
        working_schedule.is_weekend = False
        working_schedule.save()
        serializers = ScheduleSerializer(working_schedule, context={'request': request})

        return Response(
            {
                'status': True,
                'status_code': 201,
                'response': {
                    'message': 'Working Schedule Created Successfully!',
                    'error_message': None,
                    'schedule': serializers.data,
                }
            },
            status=status.HTTP_201_CREATED
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_vacations(request):
    employee_id = request.GET.get('employee_id', None)
    location = request.GET.get('location_id', None)
    search_text = request.GET.get('search_text', None)
    no_paginnation = request.GET.get('no_paginnation', None)

    if not all([location]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Missing Fields',
                    'fields': [
                        'location',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        location = BusinessAddress.objects.get(id=location)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'location is Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    queries = {}

    if search_text:
        queries['employee__full_name__icontains'] = search_text

    if employee_id:
        queries['employee__id'] = employee_id

    all_vacations = Vacation.objects.filter(
        employee__location=location,
        holiday_type='Vacation',
        is_active=True,
        **queries
    ).order_by('-created_at')
    # EmployeDailySchedule.objects.filter(vacation=obj, is_vacation=True)

    # Query EmployeDailySchedule instances related to the filtered Vacation instances
    all_daily_schedules = EmployeDailySchedule.objects \
        .filter(vacation__in=all_vacations, is_vacation=True)
    # Extract the distinct Vacation instances from the related EmployeDailySchedule instances
    related_vacations = Vacation.objects \
        .filter(vacation_employedailyschedules__in=all_daily_schedules) \
        .distinct().order_by('-created_at')

    all_vacations_count = related_vacations.count()

    page_count = all_vacations_count / 10
    if page_count > int(page_count):
        page_count = int(page_count) + 1

    per_page_results = 10000 if no_paginnation else 10
    paginator = Paginator(related_vacations, per_page_results)
    page_number = request.GET.get("page", None)
    if page_number is not None:
        related_vacations = paginator.get_page(page_number)

        serialized = NewVacationSerializer(related_vacations, many=True, context={'request': request})
        return Response(
            {
                'status': 200,
                'status_code': '200',
                'response': {
                    'message': f'Page {page_number} Schedule',
                    'count': all_vacations_count,
                    'pages': page_count,
                    'per_page_result': per_page_results,
                    'error_message': None,
                    'vacations': serialized.data
                }
            },
            status=status.HTTP_200_OK
        )
    else:
        serialized = NewVacationSerializer(related_vacations, many=True, context={'request': request})
        return Response(
            {
                'status': 200,
                'status_code': '200',
                'response': {
                    'message': f'Page {page_number} Schedule',
                    'count': all_vacations_count,
                    'pages': page_count,
                    'per_page_result': 10,
                    'error_message': None,
                    'vacations': serialized.data
                }
            },
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_absence(request):
    location = request.GET.get('location_id', None)
    employee_id = request.GET.get('employee_id', None)
    search_text = request.GET.get('search_text', None)
    no_pagination = request.GET.get('no_pagination', None)

    if not all([location]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Missing Fields',
                    'fields': [
                        'location',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        location = BusinessAddress.objects.get(id=location)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'location is Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    queries = {}

    if search_text:
        queries['employee__full_name__icontains'] = search_text

    if employee_id:
        queries['employee__id'] = employee_id

    allvacations = Vacation.objects.filter(
        employee__location=location,
        holiday_type='Absence',
        is_active=True,
        **queries
    ).order_by('-created_at')

    all_daily_schedules = EmployeDailySchedule.objects \
        .filter(vacation__in=allvacations, is_vacation=False, is_weekend=False)
    # Extract the distinct Vacation instances from the related EmployeDailySchedule instances
    related_vacations = Vacation.objects \
        .filter(vacation_employedailyschedules__in=all_daily_schedules) \
        .distinct().order_by('-created_at')

    allvacations_count = related_vacations.count()

    page_count = allvacations_count / 10
    if page_count > int(page_count):
        page_count = int(page_count) + 1

    per_page_results = 10000 if no_pagination else 10
    paginator = Paginator(related_vacations, per_page_results)
    page_number = request.GET.get("page", None)
    if page_number is not None:
        related_vacations = paginator.get_page(page_number)

        serialized = NewAbsenceSerializer(related_vacations, many=True, context={'request': request})
        return Response(
            {
                'status': 200,
                'status_code': '200',
                'response': {
                    'message': f'Page {page_number} Schedule',
                    'count': allvacations_count,
                    'pages': page_count,
                    'per_page_result': per_page_results,
                    'error_message': None,
                    'absences': serialized.data
                }
            },
            status=status.HTTP_200_OK
        )
    else:
        serialized = NewAbsenceSerializer(related_vacations, many=True, context={'request': request})
        return Response(
            {
                'status': 200,
                'status_code': '200',
                'response': {
                    'message': 'All absence schedule',
                    'count': allvacations_count,
                    'error_message': None,
                    'absences': serialized.data
                }
            },
            status=status.HTTP_200_OK
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_workingschedule(request):
    schedule_id = request.data.get('id', None)
    is_weekend_true = request.data.get('is_weekend', None)
    ids = request.data.get('ids', [])

    if is_weekend_true is None:
        if schedule_id is None:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.MISSING_FIELDS_4001,
                    'status_code_text': 'MISSING_FIELDS_4001',
                    'response': {
                        'message': 'Invalid Data!',
                        'error_message': 'fields are required!',
                        'fields': [
                            'id'
                        ]
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            schedule = EmployeDailySchedule.objects.get(id=schedule_id)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': 404,
                    'status_code_text': '404',
                    'response': {
                        'message': 'Invalid Schedule ID!',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        schedule.delete()
        if schedule.vacation:
            vacation = schedule.vacation
            remaingin_schedue = EmployeDailySchedule.objects.filter(
                vacation=vacation,
            ).exclude(id=schedule.id)
            if len(remaingin_schedue) == 0:
                vacation.delete()

        return Response(
            {
                'status': True,
                'status_code': 200,
                'status_code_text': '200',
                'response': {
                    'message': 'Schedule deleted successfully',
                    'error_message': None
                }
            },
            status=status.HTTP_200_OK
        )
    else:
        employee_ids = json.loads(ids)
        employee_schedule = EmployeDailySchedule.objects.filter(id__in=employee_ids)
        if employee_schedule:
            employee_schedule.delete()
            return Response(
                {
                    'status': 200,
                    'status_code': '200',
                    'response': {
                        'message': 'Weekend deleted successfully',
                        'error_message': None,
                    }
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    'status': 400,
                    'status_code': '400',
                    'response': {
                        'message': 'Weekend NOTFOUND',
                        'error_message': None,
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_leo_day(request):
    schedule_id = request.query_params.get('id', None)
    if schedule_id is not None:
        schedule = EmployeDailySchedule.objects.get(id=schedule_id)
        schedule.is_leo_day = False
        schedule.is_vacation = True
        schedule.vacation_status = 'accepted'
        schedule.save()
        schedule = EmployeDailySchedule.objects.get(id=schedule_id)
        leave_manage = LeaveManagements.objects.get(employee_id=schedule.employee.id)
        data = LeaveManagementSerializer(leave_manage, many=False).data
        if str(schedule.vacation_type) == "casual":
            leave_manage.casual_leave -= 1
            leave_manage.used_casual = leave_manage.used_casual - 1
            leave_manage.save()
        if str(schedule.vacation_type) == "medical":
            leave_manage.medical_leave -= 1
            leave_manage.used_medical = leave_manage.used_medical - 1
            leave_manage.save()
        if str(schedule.vacation_type) == "annual":
            leave_manage.annual_leave -= 1
            leave_manage.used_annual = leave_manage.used_annual - 1
            leave_manage.save()
        return Response(
            {
                'data': data,
                'schedule': str(schedule.vacation_type),
                'status': 200,
                'status_code': '200',
                'response': {
                    'message': 'Schedule deleted successfully',
                    'error_message': None,
                }
            },
            status=status.HTTP_200_OK
        )


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_all_vacation(request):
    vacation = Vacation.objects.all()
    vacation.delete()
    return Response({"msg": "All vacation data deleted successfully"})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_absence(request):
    schedule_id = request.data.get('id', None)
    if schedule_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'fields are required!',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        schedule = EmployeDailySchedule.objects.get(id=schedule_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Absense Schedule ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    schedule.delete()

    if schedule.vacation:

        absence = schedule.vacation
        remaingin_schedue = EmployeDailySchedule.objects.filter(
            vacation=absence,

        ).exclude(id=schedule.id)
        if len(remaingin_schedue) == 0:
            absence.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Absense Schedule deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_absence(request):
    schedule_id = request.data.get('schedule_id', None)
    employee = request.data.get('employee', None)

    if schedule_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'schedule_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        schedule = EmployeDailySchedule.objects.get(id=schedule_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code_text': 'INVALID_SCHEDULE_ID',
                'response': {
                    'message': 'Absense Schedule Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if employee is not None:
        try:
            emp = Employee.objects.get(id=employee)
            schedule.employee = emp
        except Exception as err:
            pass

    schedule.save()
    serializer = ScheduleSerializer(schedule, data=request.data, partial=True, context={'request': request})
    if not serializer.is_valid():
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.SERIALIZER_INVALID_4024,
                'response': {
                    'message': 'Schedule Serializer Invalid',
                    'error_message': serializer.errors,
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    serializer.save()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Schedule Updated Successfully',
                'error_message': None,
                'schedule': serializer.data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_all__workingschedule(request):
    weekends = EmployeDailySchedule.objects.all()
    vacation = Vacation.objects.all()
    vacation.delete()

    if weekends:
        weekends = weekends.delete()

        return Response({"msg": "Success fully deleted"})
    else:
        return Response({"msg": "all deleted"})


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_workingschedule(request):
    schedule_id = request.data.get('schedule_id', None)
    business_id = request.data.get('business_id', None)
    employee = request.data.get('employee', None)
    week_end_employee = request.data.get('week_end_employee', [])
    schedule_ids = request.data.get('schedule_ids', [])
    date = request.data.get('date', None)
    from_date = request.data.get('from_date', None)
    is_weekend = request.data.get('is_weekend', None)
    leo_value = request.data.get('is_leo_day', None)
    start_time = request.data.get('start_time', None)
    end_time = request.data.get('end_time', None)
    schedule_id = request.data.get('schedule_id', None)
    location_id_weekend = request.data.get('location', None)
    is_vacation = request.data.get('is_vacation', None)
    # is_working_schedule = request.data.get('is_working_schedule', None)
    if leo_value is not None:
        check_working_schedule = EmployeDailySchedule.objects.get(
            id=schedule_id
        )
        check_working_schedule.start_time = start_time
        check_working_schedule.end_time = end_time
        check_working_schedule.end_time_shift = end_time
        check_working_schedule.start_time_shift = start_time
        check_working_schedule.is_weekend = False
        check_working_schedule.save()
        # check_working_schedule.update(start_time=start_time,end_time=end_time , is_weekend=False ,is_vacation=False)
        working_schedule = EmployeDailySchedule.objects.get(
            id=schedule_id
        )
        serializers = ScheduleSerializer(working_schedule, context={'request': request})
        return Response(
            {
                'status': True,
                'status_code': 200,
                'response': {
                    'message': 'Working Schedule updated Successfully2!',
                    'error_message': None,
                    'schedule': serializers.data,
                    'leo_value': leo_value
                }
            },
            status=200
        )
    if is_vacation is not None:
        if schedule_id is None:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.MISSING_FIELDS_4001,
                    'status_code_text': 'MISSING_FIELDS_4001',
                    'response': {
                        'message': 'Invalid Data!',
                        'error_message': 'All fields are required.',
                        'fields': [
                            'schedule_id',
                        ]
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            schedule = EmployeDailySchedule.objects.get(id=schedule_id)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code_text': 'INVALID_SCHEDULE_ID',
                    'response': {
                        'message': 'Schedule Not Found',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if employee is not None:
            try:
                emp = Employee.objects.get(id=employee)
                schedule.employee = emp
                schedule.leo_value = leo_value
            except Exception as err:
                pass
        schedule.save()
        serializer = ScheduleSerializer(schedule, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.SERIALIZER_INVALID_4024,
                    'response': {
                        'message': 'Schedule Serializer Invalid',
                        'error_message': serializer.errors,
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer.save()
        return Response(
            {
                'status': True,
                'status_code': 200,
                'response': {
                    'message': 'Schedule Updated Successfully',
                    'error_message': None,
                    'schedule': serializer.data
                }
            },
            status=status.HTTP_200_OK
        )
    if is_weekend is not None:
        week_end_employee = json.loads(week_end_employee)
        for employee in week_end_employee:
            qs = EmployeDailySchedule.objects.filter(date__date=date, employee_id=employee)
            if qs:
                qs = qs.delete()
                EmployeDailySchedule.objects.create(
                    employee_id=employee,
                    is_weekend=True,
                    date=date,
                    from_date=from_date,
                    location_id=location_id_weekend
                )
            else:
                EmployeDailySchedule.objects.create(
                    employee_id=employee,
                    is_weekend=True,
                    date=date,
                    from_date=from_date,
                    location_id=location_id_weekend
                )
        qs = EmployeDailySchedule.objects.filter(
            is_weekend=True,
        )
        serializers = ScheduleSerializer(qs, context={'request': request}, many=True)
        return Response(
            {
                'status': True,
                'status_code': 200,
                'response': {
                    'message': 'Weekend update successfully across employees!',
                    'error_message': None,
                    'schedule': serializers.data,
                    'date': date
                }
            },
            status=status.HTTP_200_OK
        )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_employe_account(request):
    employee_id = request.data.get('employee_id', None)
    tenant_id = request.data.get('tenant_id', None)
    password = request.data.get('password', None)

    data = []

    if not all([employee_id, tenant_id, password]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'employee_id',
                        'tenant_id',
                        'password',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        employe = Employee.objects.get(id=employee_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 400,
                'status_code_text': 'Invalid Data',
                'response': {
                    'message': 'Invalid employee Id',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        tenant_id = Tenant.objects.get(id=tenant_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 400,
                'status_code_text': 'Invalid Data',
                'response': {
                    'message': 'Invalid Tenat Id',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        username = employe.email.split('@')[0]
        try:
            user_check = User.objects.get(username=username)
        except Exception as err:
            # data.append(f'username user is client errors {str(err)}')
            pass
        else:
            username = f'{username} {len(User.objects.all())}'
            data.append(f'username user is {username}')
    except Exception as err:
        data.append(f'Employee errors {str(err)}')

    user = User.objects.create(
        first_name=str(employe.full_name),
        username=username,
        email=str(employe.email),
        is_email_verified=True,
        is_active=True,
        mobile_number=str(employe.mobile_number),
    )
    account_type = AccountType.objects.create(
        user=user,
        account_type='Employee'
    )
    user.set_password(password)
    user.save()

    with tenant_context(Tenant.objects.get(schema_name='public')):
        try:
            username = employe.email.split('@')[0]
            try:
                user_check = User.objects.get(username=username)
            except Exception as err:
                # data.append(f'username user is client errors {str(err)}')
                pass
            else:
                username = f'{username} {len(User.objects.all())}'
                data.append(f'username user is {username}')
        except Exception as err:
            data.append(f'Employee errors {str(err)}')
        user = User.objects.create(
            first_name=str(employe.full_name),
            username=username,
            email=str(employe.email),
            is_email_verified=True,
            is_active=True,
            mobile_number=str(employe.mobile_number),
        )
        user_client = EmployeeTenantDetail.objects.create(
            user=user,
            tenant=tenant_id,
            is_tenant_staff=True
        )
        account_type = AccountType.objects.create(
            user=user,
            account_type='Employee'
        )
        user.set_password(password)
        user.save()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': 'Saved Data',
            'response': {
                'message': 'Successfully Employee Created',
                'error_message': None,
                'errors': data,
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def employee_login(request):
    email = request.data.get('email', None)
    password = request.data.get('password', None)
    device_token = request.data.get('device_token', None)

    data = []

    if not all([email, password]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'email',
                        'password',
                        'username',
                    ],
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user_id = User.objects.get(
            email=email,
            is_deleted=False,
            user_account_type__account_type='Employee'
        )

    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_CREDENTIALS_4013,
                'status_code_text': 'INVALID_CREDENTIALS_4013',
                'response': {
                    'message': 'User does not exist with this email',
                    'error_message': str(err),
                    'fields': ['email']
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        employee_tenant = EmployeeTenantDetail.objects.get(user__username=user_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 200,
                'response': {
                    'message': 'Authenticated',
                    'data': f'{str(err)} {str(user_id.id)} {str(user_id)} {user_id} {data}'
                }
            },
            status=status.HTTP_200_OK
        )

    with tenant_context(employee_tenant.tenant):
        user_id = User.objects.get(
            email=email,
            is_deleted=False,
            # user_account_type__account_type = 'Employee'
        )
        if not user_id.check_password(password):
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.INVALID_CREDENTIALS_4013,
                    'status_code_text': 'INVALID_CREDENTIALS_4013',
                    'response': {
                        'message': 'Incorrect Password',
                        'fields': 'Password'  # f'password {user_id.username} pass {password}'
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            user = user_id
        try:
            token = Token.objects.get(user=user)
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)

        try:
            employee = Employee.objects.get(
                email__icontains=user.email,
                is_deleted=False
            )

            # registering device token for employee
            # for mobile to send push notifications
            employee_device = CustomFCMDevice.objects.filter(
                user=user_id
            ).first()
            if not employee_device:
                employee_device = CustomFCMDevice.objects.create(
                    user=user_id,
                    registration_id=device_token
                )
            else:
                employee_device.registration_id = device_token
                employee_device.save()
            device_serialized = FCMDeviceSerializer(employee_device)
        except:
            return Response(
                {
                    'status': False,
                    'status_code': 404,
                    'status_code_text': 'EMPLOYEEE_IS_DELETED',
                    'response': {
                        'message': 'User Does not exist',
                        # 'device_token':device_token,
                        # 'device_serializer':device_serialized
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            if not employee.is_active:
                return Response(
                    {
                        'status': False,
                        'status_code': 403,
                        'status_code_text': 'EMPLOYEEE_IS_INACTIVE',
                        'response': {
                            'message': 'Employee is inactive',
                        }
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

        serialized = UserEmployeeSerializer(user, context={'tenant': employee_tenant.tenant, 'token': token.key})

    return Response(
        {
            'status': False,
            'status_code': 200,
            'response': {
                'message': 'Authenticated',
                'data': serialized.data,
                'device_data': device_serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def employee_logout(request):
    email = request.query_params.get('email', None)

    try:
        user = User.objects.filter(
            email__icontains=email,
            is_deleted=False,
        ).first()

    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_CREDENTIALS_4013,
                'status_code_text': 'INVALID_CREDENTIALS_4013',
                'response': {
                    'message': 'User does not exist with this email',
                    'error_message': str(err),
                    'fields': ['email']
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        employee_tenant = EmployeeTenantDetail.objects.get(user__username=user)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 200,
                'response': {
                    'message': 'Authenticated',
                }
            },
            status=status.HTTP_200_OK
        )

    with tenant_context(employee_tenant.tenant):

        user_id = User.objects.get(
            email=email,
            is_deleted=False,
        )
        # deleting device token for employee
        # for mobile to not send push notifications
        # when it is logout
        device = CustomFCMDevice.objects.filter(
            user=user_id
        ).first()

        if device:
            device.delete()

    return Response({
        'status': True,
        'status_code': 200,
        'message': 'Device Unlinked'
    }, status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def resend_password(request):
    email = request.data.get('email', None)
    password = request.data.get('password', None)
    old_password = request.data.get('old_password', None)

    if not email or not password:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'email',
                        'password',
                        'code',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user_id = User.objects.get(
            email=email,
            is_deleted=False,
            # user_account_type__account_type = 'Employee'
        )

    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_CREDENTIALS_4013,
                'status_code_text': 'INVALID_CREDENTIALS_4013',
                'response': {
                    'message': 'User does not exist with this email',
                    'error_message': str(err),
                    'fields': ['email']
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        employee_tenant = EmployeeTenantDetail.objects.get(user__username=user_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 200,
                'response': {
                    'message': 'Authenticated',
                    'data': str(err),
                }
            },
            status=status.HTTP_200_OK
        )

    with tenant_context(employee_tenant.tenant):
        try:
            user = User.objects.get(email=email, is_active=True)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.INVALID_CREDENTIALS_4013,
                    'status_code_text': 'INVALID_CREDENTIALS_4013',
                    'response': {
                        'message': 'User does not exist with this email',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if not len(password) < 8:
            if old_password is not None:
                # if old_password == user.password:
                if user.check_password(old_password):
                    # raise serializers.ValidationError("Old password does't match.")
                    user.set_password(password)
                    user.save()
                    return Response({
                        'success': True,
                        'response': {'message': 'Password reset successfully!'}},
                        status=status.HTTP_200_OK
                    )

                else:
                    return Response({
                        'success': True,
                        'response': {'message': f'Old password not same!'}},
                        status=status.HTTP_404_NOT_FOUND
                    )


            else:
                user.set_password(password)
                user.save()
                return Response({
                    'success': True,
                    'response': {'message': 'Password reset successfully!'}},
                    status=status.HTTP_200_OK
                )
        else:
            return Response({'success': False, 'response': {'message': 'Password should be 8 letters long!'}},
                            status=status.HTTP_400_BAD_REQUEST)


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get('email', None)
    code_for = 'Email'

    try:
        user_id = User.objects.get(
            email=email,
            is_deleted=False,
            # user_account_type__account_type = 'Employee'
        )

    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_CREDENTIALS_4013,
                'status_code_text': 'INVALID_CREDENTIALS_4013',
                'response': {
                    'message': 'User does not exist with this email',
                    'error_message': str(err),
                    'fields': ['email']
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        employee_tenant = EmployeeTenantDetail.objects.get(user__username=user_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 200,
                'response': {
                    'message': 'Authenticated',
                    'data': str(err),
                }
            },
            status=status.HTTP_200_OK
        )

    with tenant_context(employee_tenant.tenant):
        try:
            user = User.objects.get(email=email, is_active=True)
        except Exception as err:
            return Response(
                {'success': False, 'response': {'message': 'User with the given email address does not exist!'}},
                status=status.HTTP_404_NOT_FOUND)

        random_digits_for_code = ''.join(random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
        try:
            get_otp = VerificationOTP.objects.get(
                user=user,
                code_for=code_for
            )
            get_otp.delete()
        except:
            pass

        otp = VerificationOTP(
            user=user,
            code=random_digits_for_code,
            code_for=code_for
        )
        otp.save()

        user_name = f'{user.first_name}'

        if user.last_name:
            user_name += f' {user.last_name}'

        html_file = render_to_string("otp_email.html", {
            'user_name': user.username,
            'otp': otp.code,
            'email': user.email
        })
        text_content = strip_tags(html_file)

        email = EmailMultiAlternatives(
            'Email Verification OTP',
            text_content,
            settings.EMAIL_HOST_USER,
            to=[user.email]
        )

        email.attach_alternative(html_file, "text/html")
        email.send()
    return Response({'success': True,
                     'message': 'Verification code has been sent to your provided Email'},
                    status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    email = request.data.get('email', None)
    code = request.data.get('code', None)

    if not all([code, email]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'code',
                        'email',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user_id = User.objects.get(
            email=email,
            is_deleted=False,
            # user_account_type__account_type = 'Employee'
        )

    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_CREDENTIALS_4013,
                'status_code_text': 'INVALID_CREDENTIALS_4013',
                'response': {
                    'message': 'User does not exist with this email',
                    'error_message': str(err),
                    'fields': ['email']
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        employee_tenant = EmployeeTenantDetail.objects.get(user__username=user_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 200,
                'response': {
                    'message': 'Authenticated',
                    'data': str(err),
                }
            },
            status=status.HTTP_200_OK
        )

    with tenant_context(employee_tenant.tenant):
        try:
            user = User.objects.get(email=email, is_active=True)
        except Exception as err:
            return Response(
                {'success': False, 'response': {'message': 'User with the given email address does not exist!'}},
                status=status.HTTP_404_NOT_FOUND)

        try:
            get_otp = VerificationOTP.objects.get(
                user=user,
                code=code,
            )
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.INVALID_OTP_4006,
                    'status_code_text': 'INVALID_OTP_4006',
                    'response': {
                        'message': 'OTP does not correct',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Email Verify ',
                'error': None
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_employee_device(request):
    employee_id = request.GET.get('id', None)

    if not all([employee_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Employee id are required',
                    'fields': [
                        'id',
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
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'status_code_text': 'INVALID_EMPLOYEE_4025',
                'response': {
                    'message': 'Employee Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    serialized = SingleEmployeeInformationSerializer(employee_id, context={'request': request})
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'Employee',
                'error_message': None,
                'employees': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_single_employee_vacation(request):
    employee_id = request.GET.get('id', None)

    if not all([employee_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Employee id are required',
                    'fields': [
                        'id',
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
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'status_code_text': 'INVALID_EMPLOYEE_4025',
                'response': {
                    'message': 'Employee Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    # all_employe= Employee.objects.get(is_deleted=False, is_blocked=False).order_by('-created_at')
    serialized = WorkingScheduleSerializer(employee_id, context={'request': request, })

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Employee',
                'error_message': None,
                'employees': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def set_password(request):
    user_id = request.data.get('user_id', None)
    password = request.data.get('password', None)

    try:
        user = User.objects.get(id=str(user_id))
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code_text': 'INVALID_USER_ID',
                'response': {
                    'message': 'User Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        token = Token.objects.get(user=user)
    except Token.DoesNotExist:
        token = Token.objects.create(user=user)
    user.set_password(password)
    user.save()
    with tenant_context(Tenant.objects.get(schema_name='public')):
        try:
            user = User.objects.get(email=user.email)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code_text': 'INVALID_USER_EMAIL',
                    'response': {
                        'message': 'User Not Found',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            token = Token.objects.get(user=user)
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)
        user.set_password(password)
        user.save()

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'Password Set Successfully!',
                'error_message': None,
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def check_employee_existance(request):
    email = request.GET.get('email', None)

    employees = User.objects.filter(email=email)
    if len(employees) > 0:
        return Response(
            {
                'status': 200,
                'status_code': '200',
                'response': {
                    'message': 'Employee Exist!',
                    'error_message': None,
                }
            },
            status=status.HTTP_200_OK
        )
    return Response(
        {
            'status': 404,
            'status_code': '404',
            'response': {
                'message': 'Employee does not exists!',
                'error_message': None,
            }
        },
        status=status.HTTP_404_NOT_FOUND
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def create_weekend_management(request):
    try:
        monday = request.data.get('monday', False)
        tuesday = request.data.get('tuesday', False)
        wednesday = request.data.get('wednesday', False)
        thursday = request.data.get('thursday', False)
        friday = request.data.get('friday', False)
        saturday = request.data.get('saturday', False)
        sunday = request.data.get('sunday', False)
        if monday == 'true' or monday == 'True':
            monday = True
        if tuesday == 'true' or tuesday == 'True':
            tuesday = True
        if wednesday == 'true' or wednesday == 'True':
            wednesday = True
        if thursday == 'true' or thursday == 'True':
            thursday = True
        if friday == 'true' or friday == 'True':
            friday = True
        if saturday == 'true' or saturday == 'True':
            saturday = True
        if sunday == 'true' or sunday == 'True':
            sunday = True
        employee = Employee.objects.get(id=request.data.get('employee_id'))
        weekend_management = WeekManagement.objects.create(
            employee=employee,
            monday=monday,
            tuesday=tuesday,
            wednesday=wednesday,
            thursday=thursday,
            friday=friday,
            saturday=saturday,
            sunday=sunday,
        )
        weekend = WeekendManagementSerializer(weekend_management)
        return Response(
            {
                'status': 200,
                'success': True,
                'status_code': '200',
                'response': {
                    'message': 'Week end created across employee!',
                    'error_message': None,
                    'weekend': weekend.data
                }
            },
            status=status.HTTP_200_OK
        )
    except Exception as ex:
        return Response(
            {
                'success': False,
                'status': 404,
                'status_code': '404',
                'response': {
                    'message': 'Employee does not exists!',
                    'error_message': None,
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PATCH'])
@permission_classes([AllowAny])
def update_weekend_management(request):
    try:
        id = request.query_params.get('id', None)
        if not id:
            return Response(
                {
                    'success': False,
                    'status': 400,
                    'status_code': '400',
                    'response': {
                        'message': 'Employee ID is required!',
                        'error_message': None,
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        monday = request.data.get('monday', False)
        tuesday = request.data.get('tuesday', False)
        wednesday = request.data.get('wednesday', False)
        thursday = request.data.get('thursday', False)
        friday = request.data.get('friday', False)
        saturday = request.data.get('saturday', False)
        sunday = request.data.get('sunday', False)
        if monday == 'true':
            monday = True
        if tuesday == 'true':
            tuesday = True
        if wednesday == 'true':
            wednesday = True
        if thursday == 'true':
            thursday = True
        if friday == 'true':
            friday = True
        if saturday == 'true':
            saturday = True
        if sunday == 'true':
            sunday = True
        weekend_instance = WeekManagement.objects.get(id=id)
        # Update fields
        weekend_instance.monday = monday
        weekend_instance.tuesday = tuesday
        weekend_instance.wednesday = wednesday
        weekend_instance.thursday = thursday
        weekend_instance.friday = friday
        weekend_instance.saturday = saturday
        weekend_instance.sunday = sunday

        # Save the updated instance
        weekend_instance.save()

        # Serialize the updated instance if needed
        # weekend_serializer = WeekendManagementSerializer(weekend_instance)

        return Response(
            {
                'success': True,
                'status': 200,
                'status_code': '200',
                'response': {
                    'message': 'Weekend updated for the employee!',
                    'error_message': None,
                    # 'weekend': weekend_serializer.data
                }
            },
            status=status.HTTP_200_OK
        )
    except WeekManagement.DoesNotExist:
        return Response(
            {
                'success': False,
                'status': 404,
                'status_code': '404',
                'response': {
                    'message': 'Employee does not exist!',
                    'error_message': None,
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {
                'status': 400,
                'status_code': '400',
                'response': {
                    'message': 'Internal Server Error',
                    'error_message': str(e),
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_weekend_management(request):
    try:
        id = request.query_params.get('id', False)
        if id:
            weekend = WeekManagement.objects.filter(id=id)
            weekend = WeekendManagementSerializer(weekend, many=True)
            return Response(
                {
                    'success': True,
                    'status': 200,
                    'status_code': '200',
                    'response': {
                        'message': 'Weekend get across employee!',
                        'error_message': None,
                        'weekend': weekend.data
                    }
                },
                status=status.HTTP_200_OK
            )
        else:
            weekend = WeekManagement.objects.all()
            weekend = WeekendManagementSerializer(weekend, many=True)
            return Response(
                {
                    'success': True,
                    'status': 200,
                    'status_code': '200',
                    'response': {
                        'message': 'Weekend get across employee successfully!',
                        'error_message': None,
                        'weekend': weekend.data
                    }
                },
                status=status.HTTP_200_OK
            )
    except:
        return Response(
            {
                'success': False,
                'status': 400,
                'status_code': '400',
                'response': {
                    'message': 'Employee does not exists!',
                    'error_message': None,
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_weekend_management(request):
    try:
        id = request.query_params.get('id', None)
        if id:
            weekend = WeekManagement.objects.filter(id=id)
            if weekend:
                weekend.delete()
                return Response(
                    {
                        'success': True,
                        'status': 200,
                        'status_code': '200',
                        'response': {
                            'message': 'Weekend deleted across employee!',
                            'error_message': None,
                            # 'weekend':weekend
                        }
                    },
                    status=status.HTTP_200_OK
                )
    except:
        return Response(
            {
                'success': False,
                'status': 400,
                'status_code': '400',
                'response': {
                    'message': 'Weekend does not exists!',
                    'error_message': None,
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_weekend(request):
    user = request.user
    business_id = request.data.get('business', None)
    employee = request.data.get('employee', None)
    day = request.data.get('day', None)
    start_time = request.data.get('start_time', None)
    end_time = request.data.get('end_time', None)
    start_time_shift = request.data.get('start_time_shift', None)
    end_time_shift = request.data.get('end_time_shift', None)
    from_date = request.data.get('from_date', None)
    to_date = request.data.get('to_date', None)
    date = request.data.get('date', None)
    note = request.data.get('note', None)
    max_records = 2
    is_vacation = request.data.get('is_vacation', None)
    is_leave = request.data.get('is_leave', None)
    is_off = request.data.get('is_off', None)
    if not all([business_id, employee]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'business',
                        'employee'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business = Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'response': {
                    'message': 'Business not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        employee_id = Employee.objects.get(id=employee, is_deleted=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_EMPLOYEE_4025,
                'response': {
                    'message': 'Employee not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    check_working_schedule = EmployeDailySchedule.objects.filter(
        # user=user,
        business=business,
        employee=employee_id,
        is_weekend=True
        # date=date,

    )
    record_count = check_working_schedule.count()
    if record_count > max_records:
        return Response(
            {
                'status': True,
                'message': 'more than weekends working not allowed',
                'status_code': 400,
                'response': {
                    'message': 'more than weekends working not allowed',
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    working_schedule, created = EmployeDailySchedule.objects.get_or_create(
        user=user,
        business=business,
        employee=employee_id,
        date=date,
    )
    working_schedule.day = day
    working_schedule.start_time = start_time
    working_schedule.end_time = end_time
    working_schedule.start_time_shift = start_time_shift
    working_schedule.end_time_shift = end_time_shift
    working_schedule.from_date = from_date
    working_schedule.to_date = to_date
    working_schedule.note = note

    # if is_vacation == 'false':
    #     working_schedule.is_vacation = False
    #     working_schedule.is_weekend = True

    if is_vacation is not None:
        working_schedule.is_vacation = True
    else:
        working_schedule.is_vacation = False
        working_schedule.is_weekend = True
        working_schedule.is_leo_day = True
        is_leo_day_update = LeaveManagements.objects.get(employee_id=employee_id.id)
        is_leo_day_update.leo_leave += 1
        is_leo_day_update.save()

    if is_leave is not None:
        working_schedule.is_leave = True
    else:
        working_schedule.is_leavrequeste = False
    if is_off is not None:
        working_schedule.is_off = True
    else:
        working_schedule.is_off = False

    # if is_absense is not None:
    #     working_schedule.is_leave = True
    # else:
    #     working_schedule.is_leave = False

    working_schedule.save()
    serializers = ScheduleSerializer(working_schedule, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Working Schedule Created Successfull223y!',
                'error_message': None,
                'schedule': serializers.data,
            }
        },
        status=status.HTTP_201_CREATED
    )


class GiftCardViewSet(viewsets.ModelViewSet):
    queryset = GiftCards.objects.all()
    serializer_class = GiftCardSerializerResponse

    # permission_classes = [AllowAny]
    # authentication_classes = []

    def create(self, request, *args, **kwargs):
        title = request.data.get('title', None)
        validity = request.data.get('valid_till', None)
        code = request.data.get('code', None)
        currency_gift_card_price = request.data.get('currency_gift_card_price', [])
        description = request.data.get('description', None)
        custom_card = request.data.get('custom_card', None)
        discount_to_show = request.data.get('discount_to_show', None)
        price = request.data.get('price', None)
        retail_price = request.data.get('retail_price', None)
        term_condition = request.data.get('term_condition', None)
        code_check = GiftCards.objects.filter(code__contains=code)
        if code_check:
            data = {
                "success": True,
                "status_code": 400,
                "response": {
                    "message": "Code already exists",
                    "error_message": None,
                }
            }
            return Response(data, status=status.HTTP_200_OK)
        if custom_card is None:
            card = GiftCards.objects.create(title=title, valid_till=validity, code=code, description=description,
                                            discount_to_show=discount_to_show,
                                            custom_card=None, term_condition=term_condition)
            # currency_gift_card_price = json.loads(currency_gift_card_price)
            if len(currency_gift_card_price) > 0:
                for data in currency_gift_card_price:
                    GiftDetail.objects.create(currencies_id=data['currencies'], price=data['price'],
                                              retail_price=data['retail_price'], gift_card=card)
            data = {
                "success": True,
                "status_code": 200,
                "response": {
                    "message": "Gift card created Successfully",
                    "error_message": None,
                    # "data": serializer.data
                }
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            card = GiftCards.objects.create(title=title, valid_till=validity, code=code, description=description,
                                            custom_card='avaliable',
                                            price=price, retail_price=retail_price)

            data = {
                "success": True,
                "status_code": 200,
                "response": {
                    "message": "giftcard get successfully",
                    "error_message": None,
                    "data": serializer.data
                }
            }
            return Response(data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        id = request.query_params.get('id', None)
        if id is not None:
            giftcard = GiftCards.objects.filter(id=id)
            if giftcard.exists():
                giftcard.delete()
                data = {
                    "success": True,
                    "status_code": 200,
                    "response": {
                        "message": "GiftCard deleted successfully",
                        "error_message": None,
                        # "data": serializer.data
                    }
                }
                return Response(data, status=status.HTTP_200_OK)
                # return Response({"msg": f"Gift card with id {id} deleted successfully"}, status=status.HTTP_200_OK)
            else:
                data = {
                    "success": True,
                    "status_code": 200,
                    "response": {
                        "message": {"msg": f"Gift card with id {id} not found"},
                        "error_message": None,
                        # "data": serializer.data
                    }
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        else:
            # return Response({"msg": "Unable to delete the card. Please provide a valid ID"},
            #                 status=status.HTTP_400_BAD_REQUEST)
            data = {
                "success": True,
                "status_code": 400,
                "response": {
                    "message": "Unable to delete the card. Please provide a valid ID",
                    "error_message": None,
                }
            }
            return Response(data, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
@permission_classes([AllowAny])
def update_gift_card(request):
    code = request.data.get('code', None)
    # code_check = GiftCards.objects.filter(code=code)
    # if code_check:
    #     data = {
    #         "success": True,
    #         "status_code": 400,
    #         "response": {
    #             "message": "Code already exists",
    #             "error_message": None,
    #         }
    #     }
    #     return Response(data, status=status.HTTP_200_OK)
    id = request.data.get('id', None)
    currency_gift_card_price = request.data.get('currency_gift_card_price', [])
    instance = GiftCards.objects.get(id=id)
    instance.title = request.data.get('title', None)
    instance.valid_till = request.data.get('valid_till', None)
    instance.code = request.data.get('code', None)
    instance.currency_gift_card_price = request.data.get('currency_gift_card_price', [])
    instance.description = request.data.get('description', None)
    instance.price = request.data.get('price', None)
    instance.retail_price = request.data.get('retail_price', None)
    instance.term_condition = request.data.get('term_condition', None)
    instance.save()
    if len(currency_gift_card_price) > 0:
        gift_details = GiftDetail.objects.filter(gift_card_id=id)
        gift_details.delete()
        for data in currency_gift_card_price:
            GiftDetail.objects.create(currencies_id=data['currencies'], price=data['price'],
                                      retail_price=data['retail_price'], gift_card_id=id)
    data = {
        "success": True,
        "status_code": 200,
        "response": {
            "message": "gift card updated successfully",
            "error_message": None,
        }
    }
    return Response(data, status=status.HTTP_200_OK)
    # if id is not None:
    #     serializer = GiftCardSerializer(instance=instance, data=request.data, partial=True)
    #     if serializer.is_valid(raise_exception=True):
    #         instance = serializer.save()
    #         data = GiftCardSerializer(instance, many=False).data
    # else:
    #     return Response({"msg": "Id is None"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_gift_card(request):
    selected_location = request.query_params.get('selected_location')
    query_set = GiftCards.objects.all()
    search_text = request.query_params.get('search_text', None)
    if search_text:
        query_set = GiftCards.objects.filter(title_i__contains=search_text)
        
    serializer_context = {'selected_location': selected_location}
    serializer = GiftCardSerializerResponse(query_set, many=True, context=serializer_context).data
    data = {
        "success": True,
        "status_code": 200,
        "response": {
            "message": "gift card get successfully",
            "error_message": None,
            "results": serializer
        }
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_detail_from_code(request):
    code = request.query_params.get('code', None)
    location_id = request.query_params.get('location_id', None)

    if code is not None and location_id is not None:
        try:
            
            # Filter GiftCards based on the provided code and BusinessAddress
            gift_card = GiftCards.objects.get(code=code)
            serializer_gift_card = SingleGiftCardDetails(gift_card,
                                                        context={'location_id':location_id}).data
            
            data = {
                "success": True,
                "status_code": 200,
                "response": {
                    "message": "Gift card details retrieved successfully",
                    "error_message": None,
                    "gift_card": serializer_gift_card,
                }
            }
            # Return the response
            return Response(data, status=status.HTTP_200_OK)

        except GiftCards.DoesNotExist:
            # If no matching gift card is found
            data = {
                "success": False,
                "status_code": 404,
                "response": {
                    "message": "Enter a valid gift card",
                    "error_message": "No gift card with the provided code and location ID",
                    "data": None
                }
            }

            # Return a 404 Not Found response
            return Response(data, status=status.HTTP_200_OK)
    else:
        # If code or location_id is not provided
        data = {
            "success": False,
            "status_code": 400,
            "response": {
                "message": "Bad Request",
                "error_message": "Both 'code' and 'location_id' must be provided",
                "data": None
            }
        }

        # Return a 400 Bad Request response
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
