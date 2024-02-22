from Appointment.Constants.Reschedulen import reschedule_appointment_n
from django.db.models import Sum, Subquery, OuterRef, FloatField, Case, When, Value, CharField, F, DateTimeField, Q
from django.db import models
from Appointment.Constants.Reschedulen import reschedule_appointment_n
from Appointment.Constants.ConvertTime import convert_24_to_12
from django.utils import timezone
from Appointment.Constants.Reschedule import reschedule_appointment
from Appointment.Constants.AddAppointment import Add_appointment
from Appointment.Constants.cancelappointment import cancel_appointment
from Appointment.Constants.comisionCalculate import calculate_commission
from Client.serializers import ClientImagesSerializerResponses
from Promotions.models import ComplimentaryDiscount, PackagesDiscount, ServiceDurationForSpecificTime, Coupon
from Sale.Constants.Custom_pag import CustomPagination

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from rest_framework import status
from Appointment.Constants.durationchoice import DURATION_CHOICES
from Business.models import Business, BusinessAddress, BusinessTax, BusinessTaxSetting
from Business.serializers.v1_serializers import BusinessTaxSerializerNew
from datetime import datetime
from Order.models import MemberShipOrder, ProductOrder, VoucherOrder, ServiceOrder
from Sale.Constants.Custom_pag import AppointmentsPagination
from Sale.serializers import (MemberShipOrderSerializer, POSerializerForClientSale,
                              MOrderSerializerForSale, VOSerializerForClientSale,
                              SOSerializerForClientSale)

# from Service.models import Service
from Service.models import Service, PriceService
from Employee.models import CategoryCommission, CommissionSchemeSetting, EmployeDailySchedule, Employee, \
    EmployeeSelectedService, EmployeeCommission
from Authentication.models import User
from NStyle.Constants import StatusCodes
import json
from django.db.models import Q, F

from Client.models import Client, ClientPackageValidation, ClientPromotions, LoyaltyPoints, ClientLoyaltyPoint, \
    LoyaltyPointLogs, ClientImages
from datetime import date, timedelta
from threading import Thread

from Appointment.models import (Appointment, AppointmentService, AppointmentNotes, AppointmentCheckout,
                                AppointmentLogs, LogDetails, AppointmentEmployeeTip, ClientMissedOpportunity,
                                OpportunityEmployeeService, Reversal, AppointmentGroup)
from Appointment.serializers import (CheckoutSerializer, AppoinmentSerializer, ServiceClientSaleSerializer,
                                     ServiceEmployeeSerializer,
                                     SingleAppointmentSerializer, AllAppoinmentSerializer, SingleNoteSerializer,
                                     TodayAppoinmentSerializer,
                                     EmployeeAppointmentSerializer, AppointmentServiceSerializer,
                                     UpdateAppointmentSerializer,
                                     AppointmenttLogSerializer, AppointmentSerializerDashboard,
                                     AppointmentServiceSerializerBasic,
                                     PaidUnpaidAppointmentSerializer, MissedOpportunityBasicSerializer,
                                     OpportunityEmployeeServiceSerializer, PaidUnpaidAppointmentCheckoutSerializer,
                                     AppointmentSerializerForStatus, SingleNoteResponseSerializer, ReversalSerializer,
                                     ReversalSerializerResponse)
from Tenants.models import ClientTenantAppDetail, Tenant
from django_tenants.utils import tenant_context

from Utility.Campaign import send_reversal_email
from Utility.models import ExceptionRecord
from Invoices.models import SaleInvoice
from Reports.models import DiscountPromotionSalesReport
from Employee.serializers import EmplooyeeAppointmentInsightsSerializer

from Notification.notification_processor import NotificationProcessor
from Analytics.models import EmployeeBookingDailyInsights
from django.db.models import Sum
from django.db import transaction
from django.db import connection
from Utility.json_utilities import format_json_string
from Utility.date_range_utils import get_date_range_tuple
from rest_framework.pagination import PageNumberPagination

from ... import choices
from Service.serializers import BasicServiceSerializer
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from Appointment.models import Comment
from Appointment.serializers import *
from rest_framework.views import APIView
from SaleRecords.models import *

@api_view(['GET'])
@permission_classes([AllowAny])
def get_single_appointments(request):
    appointment_id = request.GET.get('appointment_id', None)

    if not all([appointment_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Appointment id is required',
                    'fields': [
                        'appointment_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        appointment = AppointmentService.objects.get(id=appointment_id, is_blocked=False, is_deleted=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_APPOINMENT_ID_4038,
                'status_code_text': 'INVALID_APPOINMENT_ID_4038',
                'response': {
                    'message': 'Appointment Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    serialized = SingleAppointmentSerializer(appointment)
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Single Appointment',
                'error_message': None,
                'appointment': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def create_reversal(request):
    description = request.data.get('description', None)
    business = request.data.get('business', None)
    service_id = request.data.get('appointment_service', None)
    appointment_id = request.data.get('appointment_id', None)
    appointment_date = request.data.get('appointment_date', None)
    service_name = request.data.get('service_name', None)
    client_name = request.data.get('client_name', None)
    email = request.data.get('email', None)
    client_type = request.data.get('client_type', None)
    client_phone = request.data.get('client_phone', None)
    url = request.data.get('url', None)
    generated_by = request.data.get('generated_by', None)
    location = request.data.get('location_id', None)
    
    Reversal.objects.create(
        location_id=location,
        url=url,
        description=description, appointment_date=appointment_date,
        business_id=business, request_status='pending',
        appointment_services_id=service_id,
        appointment_id=appointment_id,
        email=email, generated_by=generated_by,
        client_type=client_type, phone_number=client_phone, client_name=client_name, service_name=service_name
    )
    send_reversal_email(client_phone=client_phone, client_name=client_name, email=email, appointment_id=appointment_id,
                        service_id=service_id, description=description, appointment_date=appointment_date,
                        service_name=service_name, url=url)

    # Example usage:
    # send_reversal_email_threaded(client_phone=client_phone,client_name=client_name,email=email, appointment_id=appointment_id, service_id=service_id,description=description,appointment_date=appointment_date ,service_name=service_name)

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Reversal created successfully!',
                'error_message': None,
                'errors': []
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_reversal(request):
    search = request.GET.get('search_text', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    location = request.GET.get('location_id', None)
    
    #apply filter
    query = Q(location=location)  
    if start_date and end_date:
        query &= Q(appointment_date__range=(start_date, end_date))  
    
    if search:
        query &= Q(generated_by__icontains=search) | Q(client_name__icontains=search)
        
    all_reversal = Reversal.objects.filter(query).order_by('-created_at')
    paginator = AppointmentsPagination()
    paginator.page_size = 10
    reversal_qs = paginator.paginate_queryset(all_reversal, request)
    serialized = ReversalSerializerResponse(reversal_qs, many=True)
    data = {
        'status': True,
        'status_code': 200,
        'status_code_text': '200',
        "response": {
            "message": "Appointments  get Successfully",
            "error_message": None,
            "data": serialized.data,
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'current_page': paginator.page.number,
            'per_page': paginator.page_size,
            'total_pages': paginator.page.paginator.num_pages,
        }
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_appointments_service(request):
    appointment_id = request.GET.get('appointment_group_id', None)
    
    total_sale = 0
    voucher_total_price = 0
    voucher_membership = []
    
    if not all([appointment_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Appointment id is required',
                    'fields': [
                        'appointment_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        appointment = Appointment.objects.get(id=appointment_id, is_deleted=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_APPOINMENT_ID_4038,
                'status_code_text': 'INVALID_APPOINMENT_ID_4038',
                'response': {
                    'message': 'Appointment Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    serialized = SingleNoteSerializer(appointment)
    
    # Calculate Total Sale of Client---------------------
    client = appointment.client
    
    # Client All Product Order---------------------
    product_order = ProductOrder.objects \
        .filter(checkout__client=client) \
        .select_related('product', 'member') \
        .order_by('-created_at')
    product_total = product_order.aggregate(total_sale=Sum('price'))['total_sale']
    total_sale += product_total if product_total else 0
    
    # Client All Service Orders----------------------
    service_orders = ServiceOrder.objects \
        .filter(checkout__client=client) \
        .select_related('service', 'user', 'member') \
        .order_by('-created_at')
    service_total = service_orders.aggregate(total_sale=Sum('price'))['total_sale']
    total_sale += service_total if service_total else 0
    
    # Client All Voucher & Membership Orders -----------------------
    voucher_order = VoucherOrder.objects \
                        .filter(checkout__client=client) \
                        .select_related('voucher', 'member', 'user') \
                        .order_by('-created_at')[:5]
    
    # Client All Membership Orders -----------------------                    
    membership_order = MemberShipOrder.objects \
                            .filter(checkout__client=client) \
                            .select_related('membership', 'user', 'member') \
                            .order_by('-created_at')[:5]
                            
    voucher_total = voucher_order.aggregate(total_sale=Sum('price'))['total_sale']
    total_sale += voucher_total if voucher_total else 0
    
    voucher = VOSerializerForClientSale(voucher_order, many=True, context={'request': request, })
    membership = MOrderSerializerForSale(membership_order[:5], many=True, context={'request': request, })

    voucher_membership.extend(voucher.data)
    voucher_membership.extend(membership.data)
    
    # Client All Appointment Orders ------------------------------
    appointment_checkout_all = AppointmentService.objects \
        .filter(
        appointment__client=client,
        appointment_status__in=['Done', 'Paid']
        ) \
        .select_related('member', 'user', 'service') \
        .order_by('-created_at')
    
    #Now Calculate Total Sale    
    appointment_total = appointment_checkout_all.aggregate(total_sale=Sum('price'))['total_sale']
    total_sale += appointment_total if appointment_total else 0
    product = POSerializerForClientSale(product_order, many=True, context={'request': request, })
    
    price_values = sum(item.get('price', 0) for item in product.data)
    voucher_total_price = sum(item.get('price', 0) for item in voucher.data)
    total_sale = total_sale + price_values + voucher_total_price
    
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'All Appointments',
                'error_message': None,
                'appointment': serialized.data,
                'total_sales': total_sale,
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_appointments_group_services(request):
    appointment_id = request.GET.get('appointment_group_id', None)
    
    
    total_sale = 0
    voucher_total_price = 0
    voucher_membership = []
    
    if not all([appointment_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Appointment id is required',
                    'fields': [
                        'appointment_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        appointment_group = AppointmentGroup.objects.get(id = appointment_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_APPOINMENT_ID_4038,
                'status_code_text': 'INVALID_APPOINMENT_ID_4038',
                'response': {
                    'message': 'Appointment Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    

    serialized = SingleNoteSerializer(appointment_group.appointment.all(), many=True, context={'request': request})
    
    # Calculate Total Sale of Client---------------------
    clients = list(appointment_group.appointment.all().values_list('client', flat=True))
    
    # Client All Product Order---------------------
    product_order = ProductOrder.objects \
        .filter(checkout__client__id__in=clients) \
        .select_related('product', 'member') \
        .order_by('-created_at')
    product_total = product_order.aggregate(total_sale=Sum('price'))['total_sale']
    total_sale += product_total if product_total else 0
    
    # Client All Service Orders----------------------
    service_orders = ServiceOrder.objects \
        .filter(checkout__client__id__in=clients) \
        .select_related('service', 'user', 'member') \
        .order_by('-created_at')
    service_total = service_orders.aggregate(total_sale=Sum('price'))['total_sale']
    total_sale += service_total if service_total else 0
    
    # Client All Voucher & Membership Orders -----------------------
    voucher_order = VoucherOrder.objects \
                        .filter(checkout__client__id__in=clients) \
                        .select_related('voucher', 'member', 'user') \
                        .order_by('-created_at')[:5]
    
    # Client All Membership Orders -----------------------                    
    membership_order = MemberShipOrder.objects \
                            .filter(checkout__client__id__in=clients) \
                            .select_related('membership', 'user', 'member') \
                            .order_by('-created_at')[:5]
                            
    voucher_total = voucher_order.aggregate(total_sale=Sum('price'))['total_sale']
    total_sale += voucher_total if voucher_total else 0
    
    voucher = VOSerializerForClientSale(voucher_order, many=True, context={'request': request, })
    membership = MOrderSerializerForSale(membership_order[:5], many=True, context={'request': request, })

    voucher_membership.extend(voucher.data)
    voucher_membership.extend(membership.data)
    
    # Client All Appointment Orders ------------------------------
    appointment_checkout_all = AppointmentService.objects \
        .filter(
        appointment__client__id__in=clients,
        appointment_status__in=['Done', 'Paid']
        ) \
        .select_related('member', 'user', 'service') \
        .order_by('-created_at')
    
    #Now Calculate Total Sale    
    appointment_total = appointment_checkout_all.aggregate(total_sale=Sum('price'))['total_sale']
    total_sale += appointment_total if appointment_total else 0
    product = POSerializerForClientSale(product_order, many=True, context={'request': request, })
    
    price_values = sum(item.get('price', 0) for item in product.data)
    voucher_total_price = sum(item.get('price', 0) for item in voucher.data)
    total_sale = total_sale + price_values + voucher_total_price
    
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'All Appointments',
                'error_message': None,
                'appointment': serialized.data,
                'total_sales': total_sale,
                'group_check_in_time': appointment_group.group_check_in_time,
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_appointments_device(request):
    employee_id = request.GET.get('employee_id', None)
    appointment_status = request.GET.get('status', None)

    # Because we have a common serializer (see SingleNoteSerializer)
    # is_mobile is used to differentiate between mobile and web
    is_mobile = request.GET.get('is_mobile', None)
    if is_mobile == 'true':
        is_mobile = True

    query = {}
    if appointment_status == 'Appointment Booked':
        query['appointment_services__appointment_status__in'] = ['Appointment_Booked', 'Appointment Booked', 'Arrived',
                                                                 'In Progress']
    elif appointment_status == 'Done':
        query['appointment_services__appointment_status__in'] = ['Done', 'Paid']
    elif appointment_status == 'Cancel':
        query['appointment_services__appointment_status__in'] = ['Cancel']

    if not all([employee_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Employee id is required',
                    'fields': [
                        'employee_id',
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

    try:
        appointment = Appointment.objects.filter(
            appointment_services__member=employee,
            **query
        ).order_by('-created_at').distinct()
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_APPOINMENT_ID_4038,
                'status_code_text': 'INVALID_APPOINMENT_ID_4038',
                'response': {
                    'message': 'Appointment Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    serialized = SingleNoteSerializer(appointment, many=True, context={'is_mobile': is_mobile})
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'All Appointments',
                'error_message': None,
                'appointment': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_today_appointments(request):
    location_id = request.GET.get('location_id', None)

    today = date.today()
    include_query = Q(is_blocked=False, appointment_date__icontains=today, )
    exclude_query = Q(appointment_status__in=['Cancel', 'Done', 'Paid']) | \
                    Q(appointment__status=choices.AppointmentStatus.CANCELLED)

    if location_id:
        include_query &= Q(business_address__id=location_id)

    today_appointment = AppointmentService.objects \
        .filter(include_query) \
        .exclude(exclude_query) \
        .select_related('member', 'service') \
        .order_by('appointment_time')

    serialize = TodayAppoinmentSerializer(today_appointment, many=True, context={'request': request})
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'Today Appointments',
                'error_message': None,
                'appointments': serialize.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_employee_appointment_insights(request):
    # incoming string date format: 2023-05-25  YEAR-MONTH-DAY
    _start_date = str(request.query_params.get('start_date')).split('-')
    _end_date = str(request.query_params.get('end_date')).split('-')
    employee_ids = request.query_params.get('employees')
    business_address_id = request.query_params.get('business_address_id')

    # date objects
    start_date = date(int(_start_date[0]), int(_start_date[1]), int(_start_date[2]))
    end_date = date(int(_end_date[0]), int(_end_date[1]), int(_end_date[2]))
    delta = timedelta(days=1)

    if type(employee_ids) == str:
        employee_ids = employee_ids.replace("'", '"')
        employee_ids = json.loads(employee_ids)
    elif type(employee_ids) == list:
        pass

    employee_ids = [emp['id'] for emp in employee_ids]
    data = []
    business_address = BusinessAddress.objects.get(id=business_address_id)
    while start_date <= end_date:
        employees = Employee.objects \
            .with_completed_appointments(
            employee_ids=employee_ids,
            date=start_date,
            business_address=business_address
        )
        formatted_date = start_date.strftime("%Y-%m-%d")  # changes over loop
        data.append(
            {
                formatted_date: EmplooyeeAppointmentInsightsSerializer(employees, many=True).data
            }
        )
        start_date += delta

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'Employee Insights',
                'error_message': None,
                'data': data,
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_appointments(request):
    location_id = request.GET.get('location', None)
    appointment_status = request.GET.get('appointment_status', None)
    search_text = request.GET.get('search_text', None)

    upcoming_flags = ['Appointment_Booked', 'Appointment Booked', 'Arrived', 'In Progress']
    completed_flags = ['Done', 'Paid']
    cancelled_flags = ['Cancel']
    paginator = CustomPagination()
    paginator.page_size = 10

    query = Q(is_blocked=False)

    if appointment_status is not None:
        if appointment_status == 'Upcomming':
            query &= Q(appointment_status__in=upcoming_flags)
        elif appointment_status == 'Completed':
            query &= Q(appointment_status__in=completed_flags)
        elif appointment_status == 'Cancelled':
            query &= Q(appointment_status__in=cancelled_flags)

    if search_text:
        or_query = Q(member__full_name__icontains=search_text) | \
                   Q(appointment__client__full_name__icontains=search_text)
        query &= or_query

    if location_id is not None:
        query &= Q(business_address__id=location_id)

    test = AppointmentService.objects.filter(query).order_by('-created_at')

    paginated_checkout_order = paginator.paginate_queryset(test, request)
    serialize = AllAppoinmentSerializer(paginated_checkout_order, many=True)

    return paginator.get_paginated_response(serialize.data, 'appointments')


@api_view(['GET'])
@permission_classes([AllowAny])
def get_recent_ten_appointments(request):
    location_id = request.GET.get('location_id', None)

    completed_flags = ['Done', 'Paid']
    query = Q(is_blocked=False)
    query &= Q(appointment_status__in=completed_flags)
    query &= Q(business_address__id=location_id)

    recent_ten_appointments = AppointmentService.objects \
                                  .filter(query) \
                                  .select_related('member', 'service', 'appointment__client') \
                                  .order_by('-created_at')[:10]

    serialized = AppointmentSerializerDashboard(recent_ten_appointments, many=True, context={'request': request})

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'Recent 10 Appointments',
                'error_message': None,
                'appointments': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_appointments_no_pagination(request):
    location_id = request.GET.get('location', None)
    appointment_status = request.GET.get('appointment_status', None)
    search_text = request.GET.get('search_text', None)

    upcoming_flags = ['Appointment_Booked', 'Appointment Booked', 'Arrived', 'In Progress']
    completed_flags = ['Done', 'Paid']
    cancelled_flags = ['Cancel']

    paginator = CustomPagination()
    paginator.page_size = 1000000

    query = Q(is_blocked=False)

    if appointment_status is not None:
        if appointment_status == 'Upcomming':
            query &= Q(appointment_status__in=upcoming_flags)
        elif appointment_status == 'Completed':
            query &= Q(appointment_status__in=completed_flags)
        elif appointment_status == 'Cancelled':
            query &= Q(appointment_status__in=cancelled_flags)

    if location_id is not None:
        Q(business_address__id=location_id)

    if search_text:
        or_query = Q(member__full_name__icontains=search_text) | \
                   Q(appointment__client__full_name__icontains=search_text)
        query &= or_query

    test = AppointmentService.objects.filter(query).order_by('-created_at')
    paginated_checkout_order = paginator.paginate_queryset(test, request)
    serialize = AllAppoinmentSerializer(paginated_checkout_order, many=True)

    return paginator.get_paginated_response(serialize.data, 'appointments')


# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_calendar_appointment(request):
#     selected_date = request.GET.get('selected_date', None)
#     location_id = request.GET.get('location_id', None)
#     employee_ids = request.GET.get('employee', None)
#
#     # query = Q(is_deleted=False, is_active=True)
#     query = Q(is_deleted=False)
#     if employee_ids != 'All':
#         if type(employee_ids) == str:
#             employee_ids = employee_ids.replace("'", '"')
#             employee_ids = json.loads(employee_ids)
#         elif type(employee_ids) == list:
#             pass
#
#         employee_ids = [emp['id'] for emp in employee_ids]
#         query &= Q(id__in=employee_ids)
#     if location_id:
#         location = BusinessAddress.objects.get(id=location_id)
#         query &= Q(location=location)
#
#     all_memebers = Employee.objects.filter(query).order_by('-created_at')
#     # all_memebers = all_memebers.filter(is_deleted=False, is_blocked=False, **query).order_by('-created_at')
#     # all_memebers = all_memebers.filter(
#     #     Q(is_active=False, in_active_date__gte=selected_date
#     #       ) | Q(is_active=True)
#     # )
#     # all_memebers = Employee.objects.filter(is_deleted=False, is_blocked=False, **query).order_by('-created_at')
#     # all_memebers = all_memebers.filter(
#     #     Q(is_active=False, in_active_date_isnull=False,in_active_date__gte=selected_date
#     #       ) | Q(is_active=True)
#     # )
#     # all_memebers = all_memebers.filter(
#     #     Q(is_active=False, in_active_date__isnull=False, in_active_date__gte=selected_date) |
#     #     Q(is_active=True)
#     # )
#
#     # all_memebers = all_memebers.annotate(
#     #     filtered_in_active_date=Case(
#     #         When(in_active_date__isnull=False,
#     #              then=Case(When(in_active_date__lte=selected_date, then=F('in_active_date')))),
#     #         default=Value(selected_date),
#     #         output_field=models.DateField(),
#     #     )
#     # )
#     # all_memebers = all_memebers.filter(filtered_in_active_date__lte=selected_date)
#     serialized = EmployeeAppointmentSerializer(all_memebers, many=True,
#                                                context={'request': request, 'selected_date': selected_date})
#
#     return Response(
#         {
#             'status': 200,
#             'status_code': '200',
#             'response': {
#                 'message': 'Calender Appointment',
#                 'error_message': None,
#                 'appointments': serialized.data
#             }
#         },
#         status=status.HTTP_200_OK
#     )
@api_view(['GET'])
@permission_classes([AllowAny])
def get_calendar_appointment(request):
    #master code
    selected_date = request.GET.get('selected_date', None)
    location_id = request.GET.get('location_id', None)
    employee_ids = request.GET.get('employee', None)

    query = Q(is_deleted=False, is_active=True)

    if employee_ids != 'All':
        if type(employee_ids) == str:
            employee_ids = employee_ids.replace("'", '"')
            employee_ids = json.loads(employee_ids)
        elif type(employee_ids) == list:
            pass

        employee_ids = [emp['id'] for emp in employee_ids]
        query &= Q(id__in=employee_ids)

    if location_id:
        location = BusinessAddress.objects.get(id=location_id)
        query &= Q(location=location)

    all_memebers = Employee.objects.filter(query).order_by('-created_at')
    serialized = EmployeeAppointmentSerializer(all_memebers, many=True,
                                               context={'request': request, 'selected_date': selected_date})

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'Calender Appointment',
                'error_message': None,
                'appointments': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )

@transaction.atomic
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
    extra_price = request.data.get('extra_price', None)
    free_services_quantity = request.data.get('free_services_quantity', None)
    client = request.data.get('client', None)
    client_type = request.data.get('client_type', None)
    payment_method = request.data.get('payment_method', None)
    discount_type = request.data.get('discount_type', None)

    selected_promotion_type = request.data.get('selected_promotion_type', None)
    selected_promotion_id = request.data.get('selected_promotion_id', None)
    is_promotion_availed = request.data.get('is_promotion_availed', False)
    all_data = request.data.get('all_data', [])
    all_appointments = []

    Errors = []
    total_price_app = 0
    # if all_data:
    #     for data in all_data:
    #         business_id = data.get('business', None)
    #         appointments = data.get('appointments', None)
    #         appointment_date = data.get('appointment_date', None)
    #         text = data.get('appointment_notes', None)
    #         business_address_id = data.get('business_address', None)
    #         member = data.get('member', None)
    #         extra_price = data.get('extra_price', None)
    #         free_services_quantity = data.get('free_services_quantity', None)
    #         client = data.get('client', None)
    #         client_type = data.get('client_type', None)
    #         payment_method = data.get('payment_method', None)
    #         discount_type = data.get('discount_type', None)
    #
    #         selected_promotion_type = data.get('selected_promotion_type', None)
    #         selected_promotion_id = data.get('selected_promotion_id', None)
    #         is_promotion_availed = data.get('is_promotion_availed', False)
    #         try:
    #             business = Business.objects.get(id=business_id)
    #         except Exception as err:
    #             return Response(
    #                 {
    #                     'status': False,
    #                     'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
    #                     'response': {
    #                         'message': 'Business not found',
    #                         'error_message': str(err),
    #                     }
    #                 }
    #
    #             )
    #         if business_address_id is not None:
    #             try:
    #                 business_address = BusinessAddress.objects.get(id=business_address_id)
    #             except Exception as err:
    #                 return Response(
    #                     {
    #                         'status': False,
    #                         'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
    #                         'response': {
    #                             'message': 'Business Address not found',
    #                         }
    #                     }
    #                 )
    #         try:
    #             client = Client.objects.get(id=client)
    #         except Exception as err:
    #             client = None
    #
    #         appointment = Appointment.objects.create(
    #             user=user,
    #             business=business,
    #             client=client,
    #             client_type=client_type,
    #             payment_method=payment_method,
    #             discount_type=discount_type,
    #             status=choices.AppointmentStatus.BOOKED
    #         )
    #
    #         if is_promotion_availed:
    #             appointment.is_promotion = True
    #             appointment.selected_promotion_id = data.get('selected_promotion_id', '')
    #             appointment.selected_promotion_type = data.get('selected_promotion_type', '')
    #             appointment.save()
    #
    #         if business_address_id is not None:
    #             appointment.business_address = business_address
    #             appointment.save()
    #
    #         if type(appointments) == str:
    #             appointments = appointments.replace("'", '"')
    #             appointments = json.loads(appointments)
    #
    #         elif type(appointments) == list:
    #             pass
    #
    #         if text:
    #             if type(text) == str:
    #                 try:
    #                     text = text.replace("'", '"')
    #                     text = json.loads(text)
    #                 except:
    #                     AppointmentNotes.objects.create(
    #                         appointment=appointment,
    #                         text=text
    #                     )
    #             elif type(text) == list:
    #                 pass
    #                 for note in text:
    #                     AppointmentNotes.objects.create(
    #                         appointment=appointment,
    #                         text=note
    #                     )
    #         active_user_staff = None
    #         try:
    #             active_user_staff = Employee.objects.filter(
    #                 email=request.user.email,
    #                 is_deleted=False,
    #                 is_active=True,
    #                 is_blocked=False
    #             ).first()
    #         except:
    #             pass
    #
    #         appointment_logs = AppointmentLogs.objects.create(
    #             user=request.user,
    #             location=business_address,
    #             appointment=appointment,
    #             log_type='Create',
    #             member=active_user_staff
    #         )
    #
    #         all_members = []
    #         employee_users = []
    #         service_appointments = []
    #         for appoinmnt in appointments:
    #             member = appoinmnt['member']
    #             service = appoinmnt['service']
    #             app_duration = appoinmnt['duration']
    #             price = appoinmnt.get('price', 0)
    #             date_time = appoinmnt['date_time']
    #             fav = appoinmnt.get('is_favourite', None)
    #             client_can_book = appoinmnt.get('client_can_book', None)
    #             slot_availible_for_online = appoinmnt.get('slot_availible_for_online', None)
    #             discount_price = appoinmnt.get('discount_price', None)
    #             app_date_time = f'2000-01-01 {date_time}'
    #
    #             duration = DURATION_CHOICES[app_duration]
    #             app_date_time = datetime.fromisoformat(app_date_time)
    #             datetime_duration = app_date_time + timedelta(minutes=duration)
    #             datetime_duration = datetime_duration.strftime('%H:%M:%S')
    #             end_time = datetime_duration
    #
    #             try:
    #                 member = Employee.objects.get(id=member)
    #                 all_members.append(str(member.id))
    #                 temp_user = User.objects.filter(email__icontains=member.email).first()
    #                 employee_users.append(temp_user)
    #             except Exception as err:
    #                 return Response(
    #                     {
    #                         'status': False,
    #                         'status_code': StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
    #                         'response': {
    #                             'message': 'Employee not found',
    #                             'error_message': str(err),
    #                         }
    #                     }
    #                 )
    #
    #             try:
    #                 service = Service.objects.get(id=service)
    #             except Exception as err:
    #                 return Response(
    #                     {
    #                         'status': False,
    #                         'status_code': StatusCodes.SERVICE_NOT_FOUND_4035,
    #                         'response': {
    #                             'message': 'Service not found',
    #                             'error_message': str(err),
    #                         }
    #                     }
    #                 )
    #
    #             if selected_promotion_type == 'Complimentary_Discount':
    #
    #                 try:
    #                     complimentary = ComplimentaryDiscount.objects.get(id=selected_promotion_id)
    #                     ClientPromotions.objects.create(
    #                         user=user,
    #                         business=business,
    #                         client=client,
    #                         complimentary=complimentary,
    #                         service=service,
    #                         visits=1
    #                     )
    #                 except Exception as err:
    #                     Errors.append(str(err))
    #
    #             if selected_promotion_type == 'Packages_Discount':
    #                 testduration = False
    #                 try:
    #                     service_duration = ServiceDurationForSpecificTime.objects.get(id=selected_promotion_id)
    #                 except:
    #                     pass
    #
    #                 try:
    #                     package_dis = PackagesDiscount.objects.get(id=service_duration.package.id)
    #                 except:
    #                     pass
    #
    #                 try:
    #                     clientpackage = ClientPackageValidation.objects.get(
    #                         serviceduration__id=selected_promotion_id,
    #                         client=client,
    #                         package=package_dis,
    #                     )
    #                     testduration = True
    #                     clientpackage.service.add(service)
    #                     clientpackage.save()
    #
    #                 except Exception as err:
    #                     Errors.append(str(err))
    #
    #                 if testduration == False:
    #                     packages = ClientPackageValidation.objects.create(
    #                         user=user,
    #                         business=business,
    #                         client=client,
    #                         serviceduration=service_duration,
    #                         package=package_dis
    #                     )
    #                     current_date = date.today()
    #                     duration_rectricte = int(service_duration.package_duration)
    #
    #                     next_3_months = current_date + timedelta(days=duration_rectricte * 30)
    #
    #                     packages.service.add(service)
    #                     packages.due_date = next_3_months
    #                     packages.save()
    #
    #             total_price_app += int(price)
    #             service_commission = 0
    #             service_commission_type = ''
    #             toValue = 0
    #
    #             appointment_service = AppointmentService.objects.create(
    #                 user=user,
    #                 business=business,
    #                 business_address=business_address,
    #                 appointment=appointment,
    #                 duration=app_duration,
    #                 appointment_time=date_time,
    #                 appointment_date=appointment_date,
    #                 end_time=end_time,
    #                 service=service,
    #                 member=member,
    #                 discount_price=discount_price,
    #                 total_price=price,
    #                 slot_availible_for_online=slot_availible_for_online,
    #                 client_can_book=client_can_book,
    #                 status=choices.AppointmentServiceStatus.BOOKED,
    #             )
    #             if appointment.client:
    #                 appointment_service.client_tag = appointment.client.client_tag
    #                 appointment_service.client_type = appointment.client.client_type
    #                 appointment_service.save()
    #             else:
    #                 appointment_service.client_tag = 'No Client'
    #                 appointment_service.client_type = 'No Client'
    #                 appointment_service.save()
    #
    #             price_com = 0
    #             try:
    #                 if extra_price is not None and price == 0:
    #                     price = int(extra_price) / int(free_services_quantity)
    #
    #                 if discount_price is not None:
    #                     price_com = discount_price
    #                     appointment_service.price = discount_price
    #
    #                 else:
    #                     price_com = price
    #                     appointment_service.price = price
    #
    #                 appointment_service.save()
    #
    #                 comm, comm_type = calculate_commission(member, price_com)  # int(price))
    #                 service_commission += comm
    #                 service_commission_type += comm_type
    #                 appointment_service.service_commission = service_commission
    #                 appointment_service.service_commission_type = service_commission_type
    #                 appointment_service.save()
    #
    #             except Exception as err:
    #                 Errors.append(str(err))
    #
    #             if fav and fav is not None:
    #                 appointment_service.is_favourite = True
    #                 appointment_service.save()
    #
    #             if business_address_id is not None:
    #                 appointment_service.business_address = business_address
    #                 appointment_service.save()
    #                 service_appointments.append(appointment_service.id)
    #
    #             LogDetails.objects.create(
    #                 log=appointment_logs,
    #                 appointment_service=appointment_service,
    #                 start_time=appointment_service.appointment_time,
    #                 duration=appointment_service.duration,
    #                 member=appointment_service.member
    #             )
    #
    #             # Creating Employee Anatylics Here
    #             employee_insight_obj = EmployeeBookingDailyInsights.objects.create(
    #                 user=user,
    #                 employee=member,
    #                 business=business,
    #                 service=service,
    #                 appointment=appointment,
    #                 business_address=business_address,
    #                 appointment_service=appointment_service,
    #                 booking_time=date_time,
    #             )
    #             if employee_insight_obj:
    #                 employee_insight_obj.set_employee_time(date_time)
    #
    #         service_commission = 0
    #         service_commission_type = ''
    #         toValue = 0
    #         try:
    #             commission = CommissionSchemeSetting.objects.get(employee=str(member))
    #             category = CategoryCommission.objects.filter(commission=commission.id)
    #             for cat in category:
    #                 try:
    #                     toValue = int(cat.to_value)
    #                 except:
    #                     sign = cat.to_value
    #                 if cat.category_comission == 'Service':
    #                     if (int(cat.from_value) <= total_price_app and total_price_app < toValue) or (
    #                             int(cat.from_value) <= total_price_app and sign):
    #                         if cat.symbol == '%':
    #                             service_commission = price * int(cat.commission_percentage) / 100
    #                             service_commission_type = str(service_commission_type) + cat.symbol
    #                         else:
    #                             service_commission = int(cat.commission_percentage)
    #                             service_commission_type = str(service_commission) + cat.symbol
    #
    #         except Exception as err:
    #             Errors.append(str(err))
    #
    #         appointment.extra_price = total_price_app
    #         appointment.service_commission = int(service_commission)
    #         appointment.service_commission_type = service_commission_type
    #         appointment.save()
    #         serialized = AppoinmentSerializer(appointment)
    #         try:
    #             thrd = Thread(target=Add_appointment, args=[],
    #                           kwargs={'appointment': appointment, 'tenant': request.tenant,
    #                                   'user': request.user})
    #             thrd.start()
    #         except Exception as err:
    #             pass
    #
    #         all_memebers = Employee.objects.filter(
    #             is_deleted=False,
    #             is_active=True,
    #             is_blocked=False,
    #         ).order_by('-created_at')
    #
    #         # Send Notification to one or multiple Employee
    #         user = employee_users
    #         title = "Appointment"
    #         body = "New Booking Assigned"
    #
    #         NotificationProcessor.send_notifications_to_users(user, title, body, request_user=request.user)
    #
    #         serialized = EmployeeAppointmentSerializer(all_memebers, many=True, context={'request': request})
    #         return Response(
    #             {
    #                 'status': True,
    #                 'status_code': 201,
    #                 'response': {
    #                     'message': 'Appointment Create!',
    #                     'error_message': None,
    #                     'error': Errors,
    #                     'appointment_id': appointment.id,
    #                     'appointment_service_id': service_appointments[0],
    #                     'appointments': serialized.data,
    #                 }
    #             },
    #             status=status.HTTP_201_CREATED
    #         )
    # else:
    if not all([client_type, appointment_date, business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
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

    if business_address_id is not None:
        try:
            business_address = BusinessAddress.objects.get(id=business_address_id)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response': {
                        'message': 'Business Address not found',
                    }
                }
            )
    try:
        client = Client.objects.get(id=client)
    except Exception as err:
        client = None

    appointment = Appointment.objects.create(
        user=user,
        business=business,
        client=client,
        client_type=client_type,
        payment_method=payment_method,
        discount_type=discount_type,
        status=choices.AppointmentStatus.BOOKED
    )
    all_appointments.append(appointment)

    if is_promotion_availed:
        appointment.is_promotion = True
        appointment.selected_promotion_id = request.data.get('selected_promotion_id', '')
        appointment.selected_promotion_type = request.data.get('selected_promotion_type', '')
        appointment.save()

    if business_address_id is not None:
        appointment.business_address = business_address
        appointment.save()

    if type(appointments) == str:
        appointments = appointments.replace("'", '"')
        appointments = json.loads(appointments)

    elif type(appointments) == list:
        pass

    if text:
        if type(text) == str:
            try:
                text = text.replace("'", '"')
                text = json.loads(text)
            except:
                AppointmentNotes.objects.create(
                    appointment=appointment,
                    text=text
                )
        elif type(text) == list:
            pass
            for note in text:
                AppointmentNotes.objects.create(
                    appointment=appointment,
                    text=note
                )
    active_user_staff = None
    try:
        active_user_staff = Employee.objects.filter(
            email=request.user.email,
            is_deleted=False,
            is_active=True,
            is_blocked=False
        ).first()
    except:
        pass

    appointment_logs = AppointmentLogs.objects.create(
        user=request.user,
        location=business_address,
        appointment=appointment,
        log_type='Create',
        member=active_user_staff
    )

    all_members = []
    employee_users = []
    service_appointments = []
    for appoinmnt in appointments:
        member = appoinmnt['member']
        service = appoinmnt['service']
        app_duration = appoinmnt['duration']
        price = appoinmnt.get('price', 0)
        date_time = appoinmnt['date_time']
        fav = appoinmnt.get('is_favourite', None)
        client_can_book = appoinmnt.get('client_can_book', None)
        slot_availible_for_online = appoinmnt.get('slot_availible_for_online', None)
        discount_price = appoinmnt.get('discount_price', None)
        app_date_time = f'2000-01-01 {date_time}'

        duration = DURATION_CHOICES[app_duration]
        app_date_time = datetime.fromisoformat(app_date_time)
        datetime_duration = app_date_time + timedelta(minutes=duration)
        datetime_duration = datetime_duration.strftime('%H:%M:%S')
        end_time = datetime_duration

        try:
            member = Employee.objects.get(id=member)
            all_members.append(str(member.id))
            temp_user = User.objects.filter(email__icontains=member.email).first()
            employee_users.append(temp_user)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
                    'response': {
                        'message': 'Employee not found',
                        'error_message': str(err),
                    }
                }
            )

        try:
            service = Service.objects.get(id=service)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.SERVICE_NOT_FOUND_4035,
                    'response': {
                        'message': 'Service not found',
                        'error_message': str(err),
                    }
                }
            )

        if selected_promotion_type == 'Complimentary_Discount':

            try:
                complimentary = ComplimentaryDiscount.objects.get(id=selected_promotion_id)
                ClientPromotions.objects.create(
                    user=user,
                    business=business,
                    client=client,
                    complimentary=complimentary,
                    service=service,
                    visits=1
                )
            except Exception as err:
                Errors.append(str(err))

        if selected_promotion_type == 'Packages_Discount':
            testduration = False
            try:
                service_duration = ServiceDurationForSpecificTime.objects.get(id=selected_promotion_id)
            except:
                pass

            try:
                package_dis = PackagesDiscount.objects.get(id=service_duration.package.id)
            except:
                pass

            try:
                clientpackage = ClientPackageValidation.objects.get(
                    serviceduration__id=selected_promotion_id,
                    client=client,
                    package=package_dis,
                )
                testduration = True
                clientpackage.service.add(service)
                clientpackage.save()

            except Exception as err:
                Errors.append(str(err))

            if testduration == False:
                packages = ClientPackageValidation.objects.create(
                    user=user,
                    business=business,
                    client=client,
                    serviceduration=service_duration,
                    package=package_dis
                )
                current_date = date.today()
                duration_rectricte = int(service_duration.package_duration)

                next_3_months = current_date + timedelta(days=duration_rectricte * 30)

                packages.service.add(service)
                packages.due_date = next_3_months
                packages.save()

        total_price_app += int(price)
        service_commission = 0
        service_commission_type = ''
        toValue = 0

        appointment_service = AppointmentService.objects.create(
            user=user,
            business=business,
            business_address=business_address,
            appointment=appointment,
            duration=app_duration,
            appointment_time=date_time,
            appointment_date=appointment_date,
            end_time=end_time,
            service=service,
            member=member,
            discount_price=discount_price,
            total_price=price,
            slot_availible_for_online=slot_availible_for_online,
            client_can_book=client_can_book,
            status=choices.AppointmentServiceStatus.BOOKED,
        )
        if appointment.client:
            appointment_service.client_tag = appointment.client.client_tag
            appointment_service.client_type = appointment.client.client_type
            appointment_service.save()
        else:
            appointment_service.client_tag = 'No Client'
            appointment_service.client_type = 'No Client'
            appointment_service.save()

        price_com = 0
        try:
            if extra_price is not None and price == 0:
                price = int(extra_price) / int(free_services_quantity)

            if discount_price is not None:
                price_com = discount_price
                appointment_service.price = discount_price

            else:
                price_com = price
                appointment_service.price = price

            appointment_service.save()

            comm, comm_type = calculate_commission(member, price_com)  # int(price))
            service_commission += comm
            service_commission_type += comm_type
            appointment_service.service_commission = service_commission
            appointment_service.service_commission_type = service_commission_type
            appointment_service.save()

        except Exception as err:
            Errors.append(str(err))

        if fav and fav is not None:
            appointment_service.is_favourite = True
            appointment_service.save()

        if business_address_id is not None:
            appointment_service.business_address = business_address
            appointment_service.save()
            service_appointments.append(appointment_service.id)

        LogDetails.objects.create(
            log=appointment_logs,
            appointment_service=appointment_service,
            start_time=appointment_service.appointment_time,
            duration=appointment_service.duration,
            member=appointment_service.member
        )

        # Creating Employee Anatylics Here
        employee_insight_obj = EmployeeBookingDailyInsights.objects.create(
            user=user,
            employee=member,
            business=business,
            service=service,
            appointment=appointment,
            business_address=business_address,
            appointment_service=appointment_service,
            booking_time=date_time,
        )
        if employee_insight_obj:
            employee_insight_obj.set_employee_time(date_time)

    service_commission = 0
    service_commission_type = ''
    toValue = 0
    try:
        commission = CommissionSchemeSetting.objects.get(employee=str(member))
        category = CategoryCommission.objects.filter(commission=commission.id)
        for cat in category:
            try:
                toValue = int(cat.to_value)
            except:
                sign = cat.to_value
            if cat.category_comission == 'Service':
                if (int(cat.from_value) <= total_price_app and total_price_app < toValue) or (
                        int(cat.from_value) <= total_price_app and sign):
                    if cat.symbol == '%':
                        service_commission = price * int(cat.commission_percentage) / 100
                        service_commission_type = str(service_commission_type) + cat.symbol
                    else:
                        service_commission = int(cat.commission_percentage)
                        service_commission_type = str(service_commission) + cat.symbol

    except Exception as err:
        Errors.append(str(err))

    appointment.extra_price = total_price_app
    appointment.service_commission = int(service_commission)
    appointment.service_commission_type = service_commission_type
    appointment.save()
    # serialized = AppoinmentSerializer(appointment)
    try:
        thrd = Thread(target=Add_appointment, args=[], kwargs={'appointment': appointment, 'tenant': request.tenant,
                                                               'user': request.user})
        thrd.start()
    except Exception as err:
        pass

    all_memebers = Employee.objects.filter(
        is_deleted=False,
        is_active=True,
        is_blocked=False,
    ).order_by('-created_at')

    # Send Notification to one or multiple Employee
    user = employee_users
    title = "Appointment"
    body = "New Booking Assigned"

    NotificationProcessor.send_notifications_to_users(user, title, body, request_user=request.user)

    serialized = EmployeeAppointmentSerializer(all_memebers, many=True, context={'request': request})
    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Appointment Create!',
                'error_message': None,
                'error': Errors,
                'appointment_id': appointment.id,
                'appointment_service_id': service_appointments[0],
                'appointments': serialized.data,
            }
        },
        status=status.HTTP_201_CREATED
    )
@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group_appointment(request):
    user = request.user

    group_appointments = request.data.get('group_appointments', [])
    business_id = request.data.get('business', None)
    business_address_id = request.data.get('business_address', None)


    if not all([group_appointments, business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'group_appointments',
                        'business',
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
    
    if business_address_id is not None:
        try:
            business_address = BusinessAddress.objects.get(id=business_address_id)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response': {
                        'message': 'Business Address not found',
                    }
                }
            )
    else:
        business_address = None

    group_instance = AppointmentGroup.objects.create(group_name='appointment_group')
    all_appointments = []

    for g_app in group_appointments:
        appointments = g_app.get('appointments', None)
        appointment_date = g_app.get('appointment_date', None)
        text = g_app.get('appointment_notes', None)
        extra_price = g_app.get('extra_price', None)
        free_services_quantity = g_app.get('free_services_quantity', None)
        client = g_app.get('client', None)
        client_type = g_app.get('client_type', None)
        payment_method = g_app.get('payment_method', None)
        discount_type = g_app.get('discount_type', None)

        selected_promotion_type = g_app.get('selected_promotion_type', None)
        selected_promotion_id = g_app.get('selected_promotion_id', None)
        is_promotion_availed = g_app.get('is_promotion_availed', False)
        all_data = g_app.get('all_data', [])

        Errors = []
        total_price_app = 0
        

        try:
            client = Client.objects.get(id=client)
        except Exception as err:
            client = None

        appointment = Appointment.objects.create(
            user=request.user,
            business=business,
            client=client,
            client_type=client_type,
            payment_method=payment_method,
            discount_type=discount_type,
            status=choices.AppointmentStatus.BOOKED
        )
        group_instance.appointment.add(appointment)
        group_instance.save()


        all_appointments.append(appointment)

        if is_promotion_availed:
            appointment.is_promotion = True
            appointment.selected_promotion_id = g_app.get('selected_promotion_id', '')
            appointment.selected_promotion_type = g_app.get('selected_promotion_type', '')
            appointment.save()

        if business_address_id is not None:
            appointment.business_address = business_address
            appointment.save()

        if type(appointments) == str:
            appointments = appointments.replace("'", '"')
            appointments = json.loads(appointments)

        elif type(appointments) == list:
            pass

        if text:
            if type(text) == str:
                try:
                    text = text.replace("'", '"')
                    text = json.loads(text)
                except:
                    AppointmentNotes.objects.create(
                        appointment=appointment,
                        text=text
                    )
            elif type(text) == list:
                pass
                for note in text:
                    AppointmentNotes.objects.create(
                        appointment=appointment,
                        text=note
                    )
        active_user_staff = None
        try:
            active_user_staff = Employee.objects.filter(
                email=request.user.email,
                is_deleted=False,
                is_active=True,
                is_blocked=False
            ).first()
        except:
            pass

        appointment_logs = AppointmentLogs.objects.create(
            user=request.user,
            location=business_address,
            appointment=appointment,
            log_type='Create',
            member=active_user_staff
        )

        all_members = []
        employee_users = []
        service_appointments = []
        for appoinmnt in appointments:
            member = appoinmnt['member']
            service = appoinmnt['service']
            app_duration = appoinmnt['duration']
            price = appoinmnt.get('price', 0)
            date_time = appoinmnt['date_time']
            fav = appoinmnt.get('is_favourite', None)
            client_can_book = appoinmnt.get('client_can_book', None)
            slot_availible_for_online = appoinmnt.get('slot_availible_for_online', None)
            discount_price = appoinmnt.get('discount_price', None)
            app_date_time = f'2000-01-01 {date_time}'

            duration = DURATION_CHOICES[app_duration]
            app_date_time = datetime.fromisoformat(app_date_time)
            datetime_duration = app_date_time + timedelta(minutes=duration)
            datetime_duration = datetime_duration.strftime('%H:%M:%S')
            end_time = datetime_duration

            try:
                member = Employee.objects.get(id=member)
                all_members.append(str(member.id))
                temp_user = User.objects.filter(email__icontains=member.email).first()
                employee_users.append(temp_user)
            except Exception as err:
                return Response(
                    {
                        'status': False,
                        'status_code': StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
                        'response': {
                            'message': 'Employee not found',
                            'error_message': str(err),
                        }
                    }
                )

            try:
                service = Service.objects.get(id=service)
            except Exception as err:
                return Response(
                    {
                        'status': False,
                        'status_code': StatusCodes.SERVICE_NOT_FOUND_4035,
                        'response': {
                            'message': 'Service not found',
                            'error_message': str(err),
                        }
                    }
                )

            if selected_promotion_type == 'Complimentary_Discount':

                try:
                    complimentary = ComplimentaryDiscount.objects.get(id=selected_promotion_id)
                    ClientPromotions.objects.create(
                        user=request.user,
                        business=business,
                        client=client,
                        complimentary=complimentary,
                        service=service,
                        visits=1
                    )
                except Exception as err:
                    Errors.append(str(err))

            if selected_promotion_type == 'Packages_Discount':
                testduration = False
                try:
                    service_duration = ServiceDurationForSpecificTime.objects.get(id=selected_promotion_id)
                except:
                    pass

                try:
                    package_dis = PackagesDiscount.objects.get(id=service_duration.package.id)
                except:
                    pass

                try:
                    clientpackage = ClientPackageValidation.objects.get(
                        serviceduration__id=selected_promotion_id,
                        client=client,
                        package=package_dis,
                    )
                    testduration = True
                    clientpackage.service.add(service)
                    clientpackage.save()

                except Exception as err:
                    Errors.append(str(err))

                if testduration == False:
                    packages = ClientPackageValidation.objects.create(
                        user=request.user,
                        business=business,
                        client=client,
                        serviceduration=service_duration,
                        package=package_dis
                    )
                    current_date = date.today()
                    duration_rectricte = int(service_duration.package_duration)

                    next_3_months = current_date + timedelta(days=duration_rectricte * 30)

                    packages.service.add(service)
                    packages.due_date = next_3_months
                    packages.save()

            total_price_app += int(price)
            service_commission = 0
            service_commission_type = ''
            toValue = 0

            appointment_service = AppointmentService.objects.create(
                user=request.user,
                business=business,
                business_address=business_address,
                appointment=appointment,
                duration=app_duration,
                appointment_time=date_time,
                appointment_date=appointment_date,
                end_time=end_time,
                service=service,
                member=member,
                discount_price=discount_price,
                total_price=price,
                slot_availible_for_online=slot_availible_for_online,
                client_can_book=client_can_book,
                status=choices.AppointmentServiceStatus.BOOKED,
            )
            if appointment.client:
                appointment_service.client_tag = appointment.client.client_tag
                appointment_service.client_type = appointment.client.client_type
                appointment_service.save()
            else:
                appointment_service.client_tag = 'No Client'
                appointment_service.client_type = 'No Client'
                appointment_service.save()

            price_com = 0
            try:
                if extra_price is not None and price == 0:
                    price = int(extra_price) / int(free_services_quantity)

                if discount_price is not None:
                    price_com = discount_price
                    appointment_service.price = discount_price

                else:
                    price_com = price
                    appointment_service.price = price

                appointment_service.save()

                comm, comm_type = calculate_commission(member, price_com)  # int(price))
                service_commission += comm
                service_commission_type += comm_type
                appointment_service.service_commission = service_commission
                appointment_service.service_commission_type = service_commission_type
                appointment_service.save()

            except Exception as err:
                Errors.append(str(err))

            if fav and fav is not None:
                appointment_service.is_favourite = True
                appointment_service.save()

            if business_address_id is not None:
                appointment_service.business_address = business_address
                appointment_service.save()
                service_appointments.append(appointment_service.id)

            LogDetails.objects.create(
                log=appointment_logs,
                appointment_service=appointment_service,
                start_time=appointment_service.appointment_time,
                duration=appointment_service.duration,
                member=appointment_service.member
            )

            # Creating Employee Anatylics Here
            employee_insight_obj = EmployeeBookingDailyInsights.objects.create(
                user=request.user,
                employee=member,
                business=business,
                service=service,
                appointment=appointment,
                business_address=business_address,
                appointment_service=appointment_service,
                booking_time=date_time,
            )
            if employee_insight_obj:
                employee_insight_obj.set_employee_time(date_time)

        service_commission = 0
        service_commission_type = ''
        toValue = 0
        try:
            commission = CommissionSchemeSetting.objects.get(employee=str(member))
            category = CategoryCommission.objects.filter(commission=commission.id)
            for cat in category:
                try:
                    toValue = int(cat.to_value)
                except:
                    sign = cat.to_value
                if cat.category_comission == 'Service':
                    if (int(cat.from_value) <= total_price_app and total_price_app < toValue) or (
                            int(cat.from_value) <= total_price_app and sign):
                        if cat.symbol == '%':
                            service_commission = price * int(cat.commission_percentage) / 100
                            service_commission_type = str(service_commission_type) + cat.symbol
                        else:
                            service_commission = int(cat.commission_percentage)
                            service_commission_type = str(service_commission) + cat.symbol

        except Exception as err:
            Errors.append(str(err))

        appointment.extra_price = total_price_app
        appointment.service_commission = int(service_commission)
        appointment.service_commission_type = service_commission_type
        appointment.save()
        # serialized = AppoinmentSerializer(appointment)
        try:
            thrd = Thread(target=Add_appointment, args=[], kwargs={'appointment': appointment, 'tenant': request.tenant,
                                                                'user': request.user})
            thrd.start()
        except Exception as err:
            pass

        all_memebers = Employee.objects.filter(
            is_deleted=False,
            is_active=True,
            is_blocked=False,
        ).order_by('-created_at')

        # Send Notification to one or multiple Employee
        user = employee_users
        title = "Appointment"
        body = "New Booking Assigned"

        NotificationProcessor.send_notifications_to_users(user, title, body, request_user=request.user)

        # serialized = EmployeeAppointmentSerializer(all_memebers, many=True, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Appointment Create!',
                'error_message': None,
                'error': Errors,
                'appointment_group' : {
                    'id' : str(group_instance.id),
                },
                'appointment_id': group_instance.appointment.all()[0].id,
                # 'appointment_service_id': service_appointments[0],
                # 'appointments': serialized.data,
            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_appointment(request):
    appointment_service_id = request.data.get('id', None)
    start_time = request.data.get('start_time', None)
    employee_id = request.data.get('employee_id', None)
    appointment_status = request.data.get('appointment_status', None)

    is_cancelled = False

    if appointment_service_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'fields are required.',
                    'fields': [
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
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Appointment ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if employee_id:
        try:
            employee = Employee.objects.get(id=employee_id, is_deleted=False)
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

        service_appointment.member = employee
        service_appointment.appointment_time = start_time

        duration = DURATION_CHOICES[service_appointment.duration]
        app_date_time = datetime.fromisoformat(f'{service_appointment.appointment_date} {start_time}')
        datetime_duration = app_date_time + timedelta(minutes=duration)
        datetime_duration = datetime_duration.strftime('%H:%M:%S')

        service_appointment.end_time = datetime_duration
        service_appointment.save()

        # updating employee booking insight data
        # on changing appointment service.
        employee_insight_obj = EmployeeBookingDailyInsights.objects.filter(
            appointment_service=service_appointment,
        ).first()
        employee_insight_obj.employee = employee
        employee_insight_obj.set_employee_time(start_time)
        employee_insight_obj.save()

    serializer = UpdateAppointmentSerializer(service_appointment, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.SERIALIZER_INVALID_4024,
                'response': {
                    'message': 'Appointment Serializer Invalid',
                    'error_message': str(serializer.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    serializer.save()
    try:
        active_user_staff = Employee.objects.get(
            email=request.user.email,
            is_deleted=False,
            is_active=True,
            is_blocked=False
        )
    except:
        active_user_staff = None
    appointment_logs = AppointmentLogs.objects.create(
        user=request.user,
        location=service_appointment.business_address,
        appointment=service_appointment.appointment,
        log_type='Reschedule',
        member=active_user_staff
    )
    if appointment_status == 'Cancel':
        appointment_logs.log_type = 'Cancel'
        appointment_logs.save()
        cancel_service_appointment = AppointmentService.objects.filter(appointment=service_appointment.appointment)
        for appointment_service in cancel_service_appointment:
            appointment_service.appointment_status = 'Cancel'
            appointment_service.save()

            LogDetails.objects.create(
                log=appointment_logs,
                appointment_service=appointment_service,
                start_time=appointment_service.appointment_time,
                duration=appointment_service.duration,
                member=active_user_staff
            )
        pass
        try:
            thrd = Thread(target=cancel_appointment, args=[],
                          kwargs={'appointment': service_appointment, 'tenant': request.tenant})
            thrd.start()
        except Exception as err:
            print(err)
            pass
        is_cancelled = True
    else:
        res_service_appointment = AppointmentService.objects.filter(appointment=service_appointment.appointment)
        for appointment_service in res_service_appointment:
            LogDetails.objects.create(
                log=appointment_logs,
                appointment_service=appointment_service,
                start_time=appointment_service.appointment_time,
                duration=appointment_service.duration,
                member=appointment_service.member
            )

        try:
            thrd = Thread(target=reschedule_appointment_n, args=[],
                          kwargs={'appointment': service_appointment, 'tenant': request.tenant})
            thrd.start()
        except Exception as err:
            print(err)
            pass

    if is_cancelled:
        #  deleted the appointment
        user = User.objects.filter(email__icontains=service_appointment.member.email).first()
        title = 'Appointment'
        body = 'Appointment Cancelled'
        NotificationProcessor.send_notifications_to_users(user, title, body, request_user=request.user)
    else:
        # changed the employee of the existing appointment
        user = User.objects.filter(email__icontains=service_appointment.member.email).first()
        title = 'Appointment'
        body = 'New Booking Assigned'
        NotificationProcessor.send_notifications_to_users(user, title, body, request_user=request.user)

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Update Appointment Successfully',
                'error_message': None,
                'Appointment': serializer.data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_appointment_device(request):
    appointment_id = request.data.get('id', None)
    appointment_status = request.data.get('appointment_status', None)
    if appointment_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'fields are required.',
                    'fields': [
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
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Appointment ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        appointment_service = AppointmentService.objects.filter(appointment=str(appointment.id))
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Appointment Service ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    for ser in appointment_service:
        ser.appointment_status = 'In Progress'
        ser.save()

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Update Appointment Successfully',
                'error_message': None,
                # 'Appointment' : serializer.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def update_appointment_service(request):
    appointment_id = request.data.get('id', None)
    appointments = request.data.get('appointments', None)
    client_type = request.data.get('client_type', None)
    appointment_notes = request.data.get('appointment_notes', None)
    appointment_date_g = request.data.get('appointment_date', None)
    client = request.data.get('client', None)
    action_type = request.data.get('action_type', None)

    errors = []
    if appointment_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'fields are required.',
                    'fields': [
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
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Appointment ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # with transaction.atomic():
    if client:
        try:
            client = Client.objects.get(id=client)
            appointment.client = client
            customer_type = client.full_name
            appointment.save()
        except Exception as err:
            client = None
            customer_type = 'WALKIN'

    if client_type:
        appointment.client_type = client_type
        appointment.save()

    if appointment_notes:
        try:
            notes = AppointmentNotes.objects.filter(appointment=appointment)
            for no in notes:
                no.delete()
            notes = AppointmentNotes.objects.create(
                appointment=appointment,
                text=appointment_notes
            )

        except Exception as err:
            errors.append(str(err))

    active_user_staff = None
    try:
        active_user_staff = Employee.objects.get(
            email=request.user.email,
            is_deleted=False,
            is_active=True,
            is_blocked=False
        )
    except:
        pass

    appointment_logs = AppointmentLogs.objects.create(
        user=request.user,
        location=appointment.business_address,
        appointment=appointment,
        log_type='Edit' if action_type == 'edit' else 'Reschedule',
        member=active_user_staff
    )

    if appointments is not None:
        if type(appointments) == str:
            appointments = json.loads(appointments)

        elif type(appointments) == list:
            pass

        for app in appointments:
            appointment_date = appointment_date_g or app.get('appointment_date', None)
            date_time = app.get('date_time', None)
            service = app.get('service', None)
            client_can_book = app.get('client_can_book', None)
            slot_availible_for_online = app.get('slot_availible_for_online', None)
            duration = app.get('duration', None)
            price = app.get('price', None)
            member = app.get('member', None)
            is_deleted = app.get('is_deleted', None)
            is_favourite = app.get('is_favourite', False)
            id = app.get('id', None)
            try:
                service_id = Service.objects.get(id=service)
            except Exception as err:
                errors.append(str(err))
            try:
                member_id = Employee.objects.get(id=member)
            except Exception as err:
                errors.append(str(err))

            try:
                # below is just a workaround
                if id:
                    service_appointment = AppointmentService.objects.get(id=str(id))
                    if is_deleted == True:
                        service_appointment.delete()
                        continue
                else:
                    service_appointment = AppointmentService()
                    service_appointment.appointment = appointment
                    service_appointment.user = request.user
                    service_appointment.business = appointment.business
                    service_appointment.business_address = appointment.business_address
                    service_appointment.status = choices.AppointmentServiceStatus.BOOKED

                service_appointment.appointment_date = appointment_date
                service_appointment.appointment_time = date_time
                service_appointment.service = service_id
                service_appointment.client_can_book = client_can_book
                service_appointment.slot_availible_for_online = slot_availible_for_online
                service_appointment.duration = duration
                service_appointment.price = price
                service_appointment.member = member_id
                service_appointment.is_favourite = is_favourite
                service_appointment.save()

                # If a new service is added change the status of 
                # appointment to started
                appointment.status = choices.AppointmentStatus.BOOKED
                appointment.save()

                appointment_checkout, created = AppointmentCheckout.objects.get_or_create(
                    appointment=appointment,
                    business_address=appointment.business_address
                )

                # save method is being called in apply_texes method.
                appointment_checkout.apply_taxes()
            except Exception as err:
                errors.append(str(err))
            else:
                LogDetails.objects.create(
                    log=appointment_logs,
                    appointment_service=service_appointment,
                    start_time=service_appointment.appointment_time,
                    duration=service_appointment.duration,
                    member=service_appointment.member
                )

            # updating employee booking insight data
            # on changing appointment service.
            # taking client from appointment object
            employee_insight_obj = EmployeeBookingDailyInsights.objects.filter(appointment=appointment).first()

            if employee_insight_obj:
                employee_insight_obj.appointment_service = service_appointment
                employee_insight_obj.service = service_id
                employee_insight_obj.employee = member_id
                employee_insight_obj.set_employee_time(date_time)
                employee_insight_obj.save()

    try:
        ExceptionRecord.objects.create(
            text=f'reschedule_appointment Entry phase'
        )
        thrd = Thread(target=reschedule_appointment, args=[],
                      kwargs={'appointment': appointment, 'tenant': request.tenant, 'client': client})
        thrd.start()
    except Exception as err:
        ExceptionRecord.objects.create(
            text=f'reschedule_appointment {str(err)}'
        )
        pass

    # Send Notification to Employee
    user = User.objects.filter(email__icontains=service_appointment.member.email).first()
    title = 'Appointment'
    body = 'Booking Updated'
    NotificationProcessor.send_notifications_to_users(user, title, body, request_user=request.user)

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Update Appointment Successfully',
                'error_message': None,
                'errors': errors,
                # 'Appointment' : serializer.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_appointment(request):
    appointment_id = request.data.get('id', None)

    if appointment_id is None:
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
        appointment = Appointment.objects.get(id=appointment_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Appointment Service Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    appointment_services = AppointmentService.objects.filter(appointment=appointment)

    appointment.delete()
    appointment_services.delete()

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Appointment Service deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_blockTime(request):
    user = request.user
    business_id = request.data.get('business', None)

    date = request.data.get('date', None)
    start_time = request.data.get('start_time', None)
    duration = request.data.get('duration', None)

    member = request.data.get('member', None)
    details = request.data.get('details', None)

    if not all([business_id, date, start_time, duration, member]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
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
    try:
        member = Employee.objects.get(id=member)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
                'response': {
                    'message': 'Employee not found',
                    'error_message': str(err),
                }
            }
        )

    try:
        app_date_time = f'2000-01-01 {start_time}'

        duration_end = DURATION_CHOICES[duration]
        app_date_time = datetime.fromisoformat(app_date_time)
        datetime_duration = app_date_time + timedelta(minutes=duration_end)
        datetime_duration = datetime_duration.strftime('%H:%M:%S')
        tested = datetime.strptime(datetime_duration, '%H:%M:%S').time()
        end_time = datetime_duration
    except Exception as err:
        ExceptionRecord.objects.create(text=f'Errors happer in end linr 1180 {str(err)}')

    block_time_start = start_time
    block_time_end = tested
    current_appointments = AppointmentService.objects.filter(
        Q(appointment_time__range=(block_time_start, block_time_end)) |
        Q(end_time__range=(block_time_start, block_time_end)),
        business=business,
        member=member,
        appointment_date=date,
        is_deleted=False
    ).exclude(
        appointment_status__in=['Done', 'Paid', 'Cancel']
    )

    if len(current_appointments) > 0:
        return Response(
            {
                'status': False,
                'status_code': 400,
                'response': {
                    'message': 'You already have block time on this time.',
                    'error_message': None,
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    block_time = AppointmentService.objects.create(
        user=user,
        business=business,
        appointment_time=start_time,
        duration=duration,
        appointment_date=date,
        member=member,
        details=details,
        is_blocked=True,
        end_time=tested,
        status=choices.AppointmentServiceStatus.BOOKED
    )

    all_members = Employee.objects.filter(is_deleted=False, is_active=True).order_by('-created_at')

    serialized = EmployeeAppointmentSerializer(all_members, many=True, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'BlockTime Create!',
                'error_message': None,
                'appointments': serialized.data,
            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_blocktime(request):
    block_id = request.data.get('id', None)
    end_time = request.data.get('end_time', None)
    start_time = request.data.get('start_time', None)
    duration = request.data.get('duration', None)
    date = request.data.get('date', None)

    if block_id is None:
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
        block = AppointmentService.objects.get(id=block_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid BlockTime ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if start_time is not None:
        app_date_time = f'2000-01-01 {start_time}'

        duration_end = DURATION_CHOICES[duration]
        app_date_time = datetime.fromisoformat(app_date_time)
        datetime_duration = app_date_time + timedelta(minutes=duration_end)
        datetime_duration = datetime_duration.strftime('%H:%M:%S')
        tested = datetime.strptime(datetime_duration, '%H:%M:%S').time()
        end_time = datetime_duration

        block.appointment_time = start_time
        block.end_time = tested

    if date:
        block.appointment_date = date

    block.save()

    serializer = UpdateAppointmentSerializer(block, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.SERIALIZER_INVALID_4024,
                'response': {
                    'message': 'Block Serializer Invalid',
                    'error_message': str(serializer.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    serializer.save()
    all_members = Employee.objects.filter(is_deleted=False, is_active=True).order_by('-created_at')

    serialized = EmployeeAppointmentSerializer(all_members, many=True, context={'request': request})
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Update BlockTime Successfully',
                'error_message': None,
                'asset': serialized.data
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
        block = AppointmentService.objects.get(id=block_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid BlockTime ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    block.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Delete BlockTime Successfully',
                'error_message': None,
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_appointment_employee_tip(request):
    tips_id = request.data.get('tips_id', None)
    if tips_id is None:
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
        tip = AppointmentEmployeeTip.objects.get(id=tips_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Tips ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    tip.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Deleted Tip Successfully',
                'error_message': None,
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout(request):
    appointment = request.data.get('appointment', None)
    appointment_service_obj = request.data.get('appointment_service_obj', None)
    appointment_service = request.data.get('appointment_service', None)
    coupon_discounted_price = 0
    payment_method = request.data.get('payment_method', None)
    service = request.data.get('service', None)
    member = request.data.get('member', None)
    business_address = request.data.get('business_address', None)

    tax_name = request.data.get('tax_name', '')
    tax_name1 = request.data.get('tax_name1', '')
    gst = request.data.get('gst', 0)
    gst1 = request.data.get('gst1', 0)
    gst_price = request.data.get('gst_price', 0)
    gst_price1 = request.data.get('gst_price1', 0)
    service_price = request.data.get('service_price', None)
    total_price = request.data.get('total_price', 0)
    tip = request.data.get('tip', [])

    is_promotion_availed = request.data.get('is_promotion_availed', False)

    is_redeemed = request.data.get('is_redeemed', None)
    redeemed_id = request.data.get('redeemed_id', None)
    redeemed_points = request.data.get('redeemed_points', None)

    is_membership_redeemed = request.data.get('is_membership_redeemed', False)
    is_voucher_redeemed = request.data.get('is_voucher_redeemed', False)

    redeemed_membership_id = request.data.get('redeemed_membership_id', None)
    redeemed_voucher_id = request.data.get('redeemed_voucher_id', None)

    service_commission = 0
    service_commission_type = ''
    toValue = 0

    Errors = []
    total_price_app = 0
    notify_users = []
    # Extract client name from appointtment_service_obj
    client_name = None
    client_invoice = None

    try:
        member = Employee.objects.get(id=member)
    except Exception as err:
        member = None

    try:
        service = Service.objects.get(id=service)
    except Exception as err:
        service = None

    try:
        service_appointment = AppointmentService.objects.get(id=appointment_service)
    except Exception as err:
        service_appointment = None

    try:
        appointment = Appointment.objects.get(id=appointment)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Appointment ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        business_address = BusinessAddress.objects.get(id=str(business_address))
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Business Address id is required',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    if type(tip) == str:
        tip = json.loads(tip)
    if type(tip) == list:

        for t in tip:
            employee_id = t.get('employee', None)
            checkout_tip = t.get('tip', None)
            try:
                employee_tips_id = Employee.objects.get(id=employee_id)

                if employee_tips_id is not None:
                    AppointmentEmployeeTip.objects.create(
                        appointment=appointment,
                        member=employee_tips_id,
                        tip=checkout_tip,
                        business_address=business_address,
                    )
                else:
                    print(f"Error: Employee with ID {employee_id} does not exist")
            except Exception as err:
                Errors.append(f'Appointment Tip Error :: {str(err)}')
                pass

    if type(appointment_service_obj) == str:
        appointment_service_obj = json.loads(appointment_service_obj)

    elif type(appointment_service_obj) == list:
        pass

    empl_commissions_instances = []
    for app in appointment_service_obj:
        client_name = app.get('client', None)
        active_user_staff = None
        try:
            active_user_staff = Employee.objects.get(
                email=request.user.email,
                is_deleted=False,
                is_active=True,
                is_blocked=False
            )
        except:
            pass
        id = app.get('id', None)
        redeemed_price = app.get('redeemed_price', 0.00)

        try:
            service_appointment = AppointmentService.objects.get(id=id)
            service_appointment.appointment_status = 'Done'

            # if membership is redeemed then set redeemed price and redeemed
            # membership id to redeemed_instance_id
            if is_membership_redeemed:
                service_appointment.redeemed_price = redeemed_price
                service_appointment.redeemed_instance_id = redeemed_membership_id
                service_appointment.is_redeemed = True
                service_appointment.redeemed_type = AppointmentService.REDEEMED_TYPES[1][0]
            elif is_voucher_redeemed:
                # incrementing voucher max sale 
                if is_voucher_redeemed:
                    client_voucher = VoucherOrder.objects.get(id=redeemed_voucher_id)
                    client_voucher.max_sales += 1
                    client_voucher.save()
                service_appointment.redeemed_price = redeemed_price
                service_appointment.redeemed_instance_id = redeemed_voucher_id
                service_appointment.is_redeemed = True
                service_appointment.redeemed_type = AppointmentService.REDEEMED_TYPES[0][0]
            else:
                pass

            service_appointment.save()
            appointment_logs = AppointmentLogs.objects.create(
                user=request.user,
                location=service_appointment.business_address,
                appointment=service_appointment.appointment,
                log_type='Done',
                member=active_user_staff
            )
        except Exception as err:
            pass
        else:
            service_total_price = (service_appointment.total_price or service_appointment.price) * 1

            sale_commissions = CategoryCommission.objects.filter(
                commission__employee=service_appointment.member,
                from_value__lte=service_total_price,
                category_comission__iexact='Service'
            ).order_by('-from_value')

            if len(sale_commissions) > 0:
                commission = sale_commissions[0]

                calculated_commission = commission.calculated_commission(
                    service_appointment.total_price or service_appointment.price)
                employee_commission = EmployeeCommission.objects.create(
                    user=request.user,
                    business=business_address.business,
                    location=business_address,
                    employee=service_appointment.member,
                    commission=commission.commission,
                    category_commission=commission,
                    commission_category='Service',
                    commission_type=commission.comission_choice,
                    sale_value=service_appointment.discount_price if service_appointment.discount_price else (
                            service_appointment.total_price or service_appointment.price),
                    commission_rate=commission.commission_percentage,
                    commission_amount=calculated_commission,
                    symbol=commission.symbol,
                    item_name=service_appointment.service.name,
                    item_id=f'{service_appointment.service.id}',
                    quantity=1,
                    tip=0
                )
                empl_commissions_instances.append(employee_commission)
                notify_users.append(User.objects.filter(
                    email__icontains=service_appointment.member.email
                ).first())

    total_price_app = float(gst) + float(total_price)
    try:
        commission = CommissionSchemeSetting.objects.get(employee=str(member))
        category = CategoryCommission.objects.filter(commission=commission.id)
        for cat in category:
            try:
                toValue = int(cat.to_value)
            except:
                sign = cat.to_value
            if cat.category_comission == 'Service':
                if (int(cat.from_value) <= total_price_app and total_price_app < toValue) or (
                        int(cat.from_value) <= total_price_app and sign):
                    if cat.symbol == '%':
                        service_commission = total_price_app * float(cat.commission_percentage) / 100
                        service_commission_type = str(service_commission_type) + cat.symbol
                    else:
                        service_commission = float(cat.commission_percentage)
                        service_commission_type = str(service_commission) + cat.symbol

    except Exception as err:
        Errors.append(str(err))

    """
    Updating the unpaid checkout created in the appointment_service_status_update/
    api and feeding all the other data here.
    """
    coupon_discounted_price = request.data.get('coupon_discounted_price', None)
    redeemed_coupon_id = request.data.get('redeemed_coupon_id', None)
    is_coupon_redeemed = request.data.get('is_coupon_redeemed', None)
    if redeemed_coupon_id:
        coupon = Coupon.objects.get(id=redeemed_coupon_id)
        coupon.usage_limit -= 1
        coupon.user_limit -= 1
        coupon.save()
    checkout = AppointmentCheckout.objects.get(appointment=appointment)
    checkout.appointment_service = service_appointment
    checkout.payment_method = payment_method
    checkout.service = service
    checkout.member = member
    checkout.business_address = business_address
    checkout.gst = gst
    checkout.gst1 = gst1
    checkout.gst_price = gst_price
    checkout.gst_price1 = gst_price1
    checkout.tax_name = tax_name
    checkout.tax_name1 = tax_name1
    checkout.service_price = service_price
    checkout.total_price = total_price
    checkout.service_commission = float(service_commission)
    checkout.service_commission_type = service_commission_type
    checkout.coupon_discounted_price = coupon_discounted_price
    checkout.coupon_id = redeemed_coupon_id
    checkout.is_coupon_redeemed = is_coupon_redeemed
    checkout.save()

    # change the status of appointment after checkout
    appointment.status = choices.AppointmentStatus.DONE
    appointment.save()

    for i_employee_commission in empl_commissions_instances:
        i_employee_commission.sale_id = checkout.id
        i_employee_commission.save()

    if client_name is not None:
        client_invoice = Client.objects.filter(full_name=client_name).first()

    invoice = SaleInvoice.objects.create(
        client=client_invoice if client_invoice else None,
        appointment=appointment,
        appointment_service=f'{service_appointment.id}',
        payment_type=payment_method,

        # Added new fields

        invoice_type='order',
        checkout_type='appointment',

        service=f'{service.id}' if service else '',
        member=f'{member.id}' if member else '',
        business_address=f'{business_address.id}',
        location=business_address,
        gst=gst,
        gst_price=gst_price,
        service_price=service_price,
        total_price=total_price,
        service_commission=float(service_commission),
        service_commission_type=service_commission_type,
        checkout=f'{checkout.id}',
    )
    invoice.save()

    try:
        if checkout.appointment.is_promotion:
            checkout.is_promotion = True
            checkout.selected_promotion_id = checkout.appointment.selected_promotion_id
            checkout.selected_promotion_type = checkout.appointment.selected_promotion_type
            checkout.save()
            invoice.is_promotion = True
            invoice.selected_promotion_id = checkout.appointment.selected_promotion_id
            invoice.selected_promotion_type = checkout.appointment.selected_promotion_type
            invoice.save()
    except Exception as err:
        Errors.append(str(err))
        pass

    if checkout.appointment.is_promotion:
        disc_sale = DiscountPromotionSalesReport(
            checkout_id=checkout.id,
            checkout_type='Appointment',
            invoice=invoice,
            promotion_id=checkout.appointment.selected_promotion_id,
            promotion_type=checkout.appointment.selected_promotion_type,
            user=checkout.appointment.user,
            client=checkout.appointment.client,
            location=checkout.business_address,
        )
        disc_sale.save()

    if appointment.client:
        logs_points_redeemed = 0
        logs_total_redeened_value = 0
        if all([is_redeemed, redeemed_id, redeemed_points]):
            try:
                client_points = ClientLoyaltyPoint.objects.get(id=redeemed_id)
            except Exception as err:
                ExceptionRecord.objects.create(text=f'LOYALTY : {err}')
                pass
            else:
                client_points.points_redeemed = client_points.points_redeemed + float(redeemed_points)
                client_points.save()

                # for_every_points
                # customer_will_get_amount

                single_point_value = client_points.customer_will_get_amount / client_points.for_every_points
                total_redeened_value = float(single_point_value) * float(redeemed_points)

                # points_redeemed = redeemed_points,
                logs_points_redeemed = redeemed_points
                # actual_sale_value_redeemed = total_redeened_value
                logs_total_redeened_value = total_redeened_value

        allowed_points = LoyaltyPoints.objects.filter(
            Q(loyaltytype='Service') |
            Q(loyaltytype='Both'),
            location=business_address,
            is_active=True,
            is_deleted=False
        )

        if len(allowed_points) > 0:
            point = allowed_points[0]

            client_points, created = ClientLoyaltyPoint.objects.get_or_create(
                location=business_address,
                client=appointment.client,
                loyalty_points=point,
            )

            loyalty_spend_amount = point.amount_spend
            loyalty_earned_points = point.number_points  # total earned points if user spend amount point.amount_spend

            # gained points based on customer's total Checkout Bill

            earned_points = (float(checkout.total_price) / float(loyalty_spend_amount)) * float(loyalty_earned_points)
            earned_amount = (earned_points / point.earn_points) * float(point.total_earn_from_points)

            if created:
                client_points.for_every_points = point.earn_points
                client_points.customer_will_get_amount = point.total_earn_from_points
                client_points.total_earn = earned_points
                client_points.total_amount = earned_amount

            else:
                client_points.total_earn = float(client_points.total_earn) + earned_points
                client_points.total_amount = client_points.total_amount + float(earned_amount)

            client_points.save()

            LoyaltyPointLogs.objects.create(
                location=business_address,
                client=client_points.client,
                client_points=client_points,
                loyalty=point,
                points_earned=float(earned_points),
                points_redeemed=logs_points_redeemed,
                balance=(float(client_points.total_earn) - float(logs_points_redeemed)),
                actual_sale_value_redeemed=logs_total_redeened_value,
                invoice=invoice,
                checkout=checkout
            )

    LogDetails.objects.create(
        log=appointment_logs,
        appointment_service=service_appointment,
        start_time=service_appointment.appointment_time,
        duration=service_appointment.duration,
        member=service_appointment.member
    )

    invoice.save()  # Do not remove this
    serialized = CheckoutSerializer(checkout)

    # Send Notification to Employee
    user = notify_users
    title = 'Appointment'
    body = 'Appointment completed'
    NotificationProcessor.send_notifications_to_users(user, title, body, request_user=request.user)
    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Appointment Checkout Created!',
                'error_message': None,
                'checkout': serialized.data,
                'errors': Errors
            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_device(request):
    appointment = request.data.get('appointment', None)

    payment_method = request.data.get('payment_method', None)
    service = request.data.get('service', None)
    member = request.data.get('member', None)
    business_address = request.data.get('business_address', None)

    tip = request.data.get('tip', None)
    gst = request.data.get('gst', None)
    service_price = request.data.get('service_price', None)
    total_price = request.data.get('total_price', None)

    try:
        members = Employee.objects.get(id=member)
    except Exception as err:
        members = None

    try:
        services = Service.objects.get(id=service)
    except Exception as err:
        services = None

    try:
        appointments = Appointment.objects.get(id=appointment)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Appointment ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        business_address = BusinessAddress.objects.get(id=str(business_address))
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Business address Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        service_appointment = AppointmentService.objects.filter(appointment=str(appointments))
        for ser in service_appointment:
            ser.appointment_status = 'Done'
            ser.save()

            service_total_price = (ser.total_price or ser.price) * 1

            sale_commissions = CategoryCommission.objects.filter(
                commission__employee=members,
                from_value__lte=service_total_price,
                category_comission__iexact='Service'
            ).order_by('-from_value')

            if len(sale_commissions) > 0:
                commission = sale_commissions[0]

                calculated_commission = commission.calculated_commission(ser.total_price or ser.price)
                employee_commission = EmployeeCommission.objects.create(
                    user=request.user,
                    business=business_address.business,
                    location=business_address,
                    employee=ser.member,
                    commission=commission.commission,
                    category_commission=commission,
                    commission_category='Service',
                    commission_type=commission.comission_choice,
                    sale_value=ser.discount_price if ser.discount_price else (ser.total_price or ser.price),
                    commission_rate=commission.commission_percentage,
                    commission_amount=calculated_commission,
                    symbol=commission.symbol,
                    item_name=ser.service.name,
                    item_id=f'{ser.service.id}',
                    quantity=1,
                    tip=0
                )

    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Service Appointment ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    AppointmentEmployeeTip.objects.create(
        appointment=appointments,
        member=members,
        tip=tip,
        business_address=business_address,
    )

    checkout = AppointmentCheckout.objects.create(
        appointment=appointments,
        appointment_service=service_appointment[0],
        payment_method=payment_method,
        service=services,
        member=members,
        business_address=business_address,
        gst=gst,
        service_price=service_price,
        total_price=total_price,

    )
    invoice = SaleInvoice.objects.create(
        appointment=appointments,
        appointment_service=f'{service_appointment[0].id}',
        payment_type=payment_method,
        service=f'{services.id}' if services else '',
        member=f'{members.id}' if members else '',
        location=business_address,
        business_address=f'{business_address.id}',
        gst=gst,
        service_price=service_price,
        total_price=total_price,
        checkout=f'{checkout.id}',
    )

    invoice.save()  # Do not remove this
    # change the status of appointment after checkout
    appointments.status = choices.AppointmentStatus.DONE
    appointments.save()
    serialized = CheckoutSerializer(checkout)
    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Appointment Checkout Created!',
                'error_message': None,
                'checkout': serialized.data,
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def service_appointment_count(request):
    location_id = request.GET.get('address', None)
    duration = request.GET.get('duration', None)

    query = Q(is_deleted=False)

    try:
        location = BusinessAddress.objects.get(id=location_id)
        query &= Q(location__id=location_id)
    except Exception as err:
        location = None
        print(err)

    currency = BusinessAddress.objects.get(id=location_id).currency
    if currency:
        # filter out those services which has the currency price for the current location currency.
        service_ids = list(PriceService.objects.filter(currency=currency).values_list('service__id', flat=True))
        query &= Q(id__in=service_ids)

    services = Service.objects \
        .filter(query) \
        .with_total_sale_count(location=location, duration=duration) \
        .order_by('-total_count')

    serializer = BasicServiceSerializer(services, many=True)

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Appointment Checkout Create!',
                'error_message': None,
                'serializer_data': serializer.data

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
    if address is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'address id is required',
                    'fields': [
                        'address',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    Employee = EmployeeSelectedService.objects.filter(service=address)
    serializer = ServiceEmployeeSerializer(Employee, many=True)
    data = serializer.data
    for i in data:
        employee_ids.append(i['employee'])

    # test = data['employee']
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Appointment Checkout Create!',
                'error_message': None,
                'data': employee_ids,

            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_employees_for_selected_service(request):
    service = request.GET.get('service', None)
    if service is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'service id is required',
                    'fields': [
                        'service',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    Employee = EmployeeSelectedService.objects.filter(service=service)
    serializer = ServiceEmployeeSerializer(Employee, many=True)

    # test = data['employee']
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Employee Selected Service!',
                'error_message': None,
                'data': serializer.data,

            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_client_sale(request):
    total_sale = 0
    client = request.GET.get('client', None)
    voucher_membership = []
    if client is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'client id is required',
                    'fields': [
                        'client',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    images = ClientImages.objects.filter(client_id=client)
    c_images = ClientImagesSerializerResponses(images, many=True,
                                               context={'request': request}).data

    # Product Order---------------------
    product_order = SaleRecordsProducts.objects \
        .filter(sale_record__client__id=client) \
        .select_related('sale_record', 'employee', 'product') \
        .order_by('-created_at')
        
    product_total = product_order.aggregate(total_sale=Sum('price'))['total_sale']
    total_sale += product_total if product_total else 0
    if product_order.count() > 5:
        product_order = product_order[:5]
    product = POSerializerForClientSale(product_order, many=True, context={'request': request, })

    # Service Orders----------------------
    service_orders = SaleRecordServices.objects \
        .filter(sale_record__client__id=client) \
        .select_related('sale_record', 'employee', 'service') \
        .order_by('-created_at')
    service_total = service_orders.aggregate(total_sale=Sum('price'))['total_sale']
    total_sale += service_total if service_total else 0
    if service_orders.count() > 5:
        service_orders = service_orders[:5]
    services_data = SOSerializerForClientSale(service_orders, many=True, context={'request': request, })

    # Voucher & Membership Orders -----------------------
    voucher_order = SaleRecordVouchers.objects \
                        .filter(sale_record__client__id=client) \
                        .select_related('sale_record', 'employee', 'voucher') \
                        .order_by('-created_at')[:5]
    membership_order = SaleRecordMembership.objects \
                        .filter(sale_record__client__id=client) \
                        .select_related('sale_record') \
                        .order_by('-created_at')[:5]
    voucher_total = voucher_order.aggregate(total_sale=Sum('price'))['total_sale']
    total_sale += voucher_total if voucher_total else 0
    if voucher_order.count() > 5:
        voucher_order = voucher_order[:5]

    membership_total = membership_order.aggregate(total_sale=Sum('price'))['total_sale']
    total_sale += membership_total if membership_total else 0
    if membership_order.count() > 5:
        membership_order = membership_order[:5]

    voucher = VOSerializerForClientSale(voucher_order, many=True, context={'request': request, })
    membership = MOrderSerializerForSale(membership_order[:5], many=True, context={'request': request, })

    voucher_membership.extend(voucher.data)
    voucher_membership.extend(membership.data)

    # Appointment Orders ------------------------------
    appointment_checkout_all = SaleRecordsAppointmentServices.objects \
        .filter(
        client_id=client,
        appointment__status__in=['Done', 'Paid']
        ).select_related('sale_record', 'membership', 'client', 'appointment', 'service', 'employee' ) \
        .order_by('-created_at')
    appointment_checkout_5 = appointment_checkout_all
    appointment_total = appointment_checkout_all.aggregate(total_sale=Sum('price'))['total_sale']
    total_sale += appointment_total if appointment_total else 0
    if appointment_checkout_all.count() > 5:
        appointment_checkout_5 = appointment_checkout_all[:5]

    appointment = ServiceClientSaleSerializer(appointment_checkout_5[:5], many=True)
    quick_sale_count = len(product.data) + len(services_data.data)
    # for item in product:
    #     print("i am printing item",item)
    price_values = sum(item.get('price', 0) for item in product.data)
    voucher_total_price = 0
    voucher_total_price = sum(item.get('price', 0) for item in voucher.data)
    total_sale = total_sale + price_values + voucher_total_price
    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Client Order Sales!',
                'c_images': c_images,
                'error_message': None,
                'product': product.data,
                'service': services_data.data,
                'voucher': voucher_membership,
                'appointment': appointment.data,
                'appointments_count': appointment_checkout_all.count(),
                'total_sales': total_sale,
                'quick_sale_count': quick_sale_count,
                'voucher_count': len(voucher_membership)
            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_appointment_client(request):
    """
    This view is deprecated and not in use.
    """
    # user = request.user
    tenant_id = request.data.get('hash', None)
    business_id = request.data.get('business', None)
    appointments = request.data.get('appointments', None)
    appointment_date = request.data.get('appointment_date', None)
    text = request.data.get('appointment_notes', None)

    client = request.data.get('client', None)
    client_type = request.data.get('client_type', None)
    client_email = request.data.get('client_email', None)

    payment_method = request.data.get('payment_method', None)
    discount_type = request.data.get('discount_type', None)
    comments = request.data.get('comments', None)
    group_appointment = request.data.get('group_appointment', None)

    errors = []

    # if tenant_id is None:
    if not all([tenant_id, client_type, appointment_date, business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
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
        tenant = Tenant.objects.get(id=str(tenant_id))
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 400,
                'status_code_text': 'Invalid Data',
                'response': {
                    'message': 'Invalid Tenant Id',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    tenant_client, tennant_client_created = ClientTenantAppDetail.objects.get_or_create(
        user=request.user,
        tenant=tenant,
        is_appointment=True
    )

    if tennant_client_created:
        user_details = {
            'email': f'{request.user.email}',
            'full_name': f'{request.user.username}',
            'mobile_number': f'{request.user.mobile_number}',
        }
        client_id = None
    else:
        client_id = tenant_client.client_id

    with tenant_context(tenant):
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

        business_address_id = request.data.get('business_address', None)

        if business_address_id is not None:
            try:
                business_address = BusinessAddress.objects.get(id=business_address_id)
            except Exception as err:
                return Response(
                    {
                        'status': False,
                        # 'error_message' : str(err),
                        'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                        'response': {
                            'message': 'Business not found',
                        }
                    }
                )

        if client_id:
            client = Client.objects.get(id=client_id)
        else:
            client, created = Client.objects.get_or_create(
                email=user_details['email'],
                business=business,
            )

            if created:
                client.full_name = user_details['full_name']
                client.mobile_number = user_details['mobile_number']
                client.is_email_verified = True
                client.is_mobile_verified = True

                client.is_active = True
                client.save()

        client_id = f'{client.id}'
        tenant_client.client_id = client_id
        tenant_client.save()
        
        appointment = Appointment.objects.create(
            user=business.user,
            business=business,
            client=client,
            client_type='IN HOUSE',
            payment_method=payment_method,
            discount_type=discount_type,
            status=choices.AppointmentStatus.BOOKED
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
                    text=note
                )

        all_members = []
        for appoinmnt in appointments:
            member = appoinmnt['member']
            service = appoinmnt['service']
            app_duration = appoinmnt['duration']
            price = appoinmnt['price']
            date_time = appoinmnt['date_time']
            fav = appoinmnt.get('favourite', None)

            app_date_time = f'2000-01-01 {date_time}'

            duration = DURATION_CHOICES[app_duration.lower()]
            app_date_time = datetime.fromisoformat(app_date_time)
            datetime_duration = app_date_time + timedelta(minutes=duration)
            datetime_duration = datetime_duration.strftime('%H:%M:%S')
            end_time = datetime_duration

            try:
                member = Employee.objects.get(id=str(member))
                all_members.append(str(member.id))
            except Exception as err:
                return Response(
                    {
                        'status': False,
                        'status_code': StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
                        'response': {
                            'message': 'Employee not found',
                            'error_message': str(err),
                        }
                    }
                )
            try:
                service = Service.objects.get(id=service)
            except Exception as err:
                return Response(
                    {
                        'status': False,
                        'status_code': StatusCodes.SERVICE_NOT_FOUND_4035,
                        'response': {
                            'message': 'Service not found',
                            'error_message': str(err),
                        }
                    }
                )

            appointment_service = AppointmentService.objects.create(
                user=business.user,
                business=business,
                appointment=appointment,
                duration=app_duration,
                appointment_time=date_time,
                appointment_date=appointment_date,
                end_time=end_time,
                service=service,
                member=member,
                price=price,
                total_price=price,
                status=choices.AppointmentServiceStatus.BOOKED
            )
                
            if comments:
                comment = Comment.objects.create(
                    user=request.user,
                    comment=comments,
                    appointment=appointment.id,
                    group_appointment_id=group_appointment.id,   
                )
                comment.save()
            
            if fav is not None:
                appointment_service.is_favourite = True
                appointment_service.save()

            if business_address_id is not None:
                appointment_service.business_address = business_address
                appointment_service.save()
        serialized = AppoinmentSerializer(appointment)

        # try: 
        #     # thrd = Thread(target=Add_appointment_nn, args=[], kwargs={'appointment' : appointment, 'tenant' : request.tenant})
        #     # thrd.start()
        # except Exception as err:
        #     pass

        all_memebers = Employee.objects.filter(
            is_deleted=False,
            is_active=True,
            is_blocked=False,
        ).order_by('-created_at')
        serialized = EmployeeAppointmentSerializer(all_memebers, many=True, context={'request': request})

        return Response(
            {
                'status': True,
                'status_code': 201,
                'response': {
                    'message': 'Appointment Create!',
                    'error_message': None,
                    'appointments': serialized.data,
                    'client_id': client_id,
                    'errors': errors,
                    'comments': comments,
                }
            },
            status=status.HTTP_201_CREATED
        )


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def get_employee_check_time(request):
    emp_id = request.data.get('member_id', None)
    duration = request.data.get('duration', None)
    start_time = request.data.get('app_time', None)
    date = request.data.get('date', None)

    if duration and duration is not None:
        duration = duration.strip()

    if start_time is not None:
        dtime = datetime.strptime(start_time, "%H:%M:%S")
        start_time = dtime.time()

    if date is not None:
        dt = datetime.strptime(date, "%Y-%m-%d")
        date = dt.date()

    app_date_time = f'2000-01-01 {start_time}'

    duration = DURATION_CHOICES[duration]
    app_date_time = datetime.fromisoformat(app_date_time)
    datetime_duration = app_date_time + timedelta(minutes=duration)
    datetime_duration = datetime_duration.strftime('%H:%M:%S')
    tested = datetime.strptime(datetime_duration, '%H:%M:%S').time()
    end_time = datetime_duration

    EmployeDaily = False
    data = []

    try:
        employee = Employee.objects.get(
            id=emp_id,
        )
        try:
            daily_schedule = EmployeDailySchedule.objects.get(
                employee=employee,
                is_vacation=False,
                date=date,
            )
            if start_time >= daily_schedule.start_time and start_time < daily_schedule.end_time:
                pass
            elif daily_schedule.start_time_shift and daily_schedule.start_time_shift != None:
                if start_time >= daily_schedule.start_time_shift and start_time < daily_schedule.end_time_shift:
                    pass
                else:
                    st_time = convert_24_to_12(str(start_time))
                    ed_time = convert_24_to_12(str(tested))
                    return Response(
                        {
                            'status': True,
                            'status_code': 200,
                            'response': {
                                'message': f'{employee.full_name} isn’t available on the selected date {st_time} and {ed_time}, but your team member can still book appointments for them.',
                                'error_message': f'This Employee day off, {employee.full_name} date {date}',
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
                        'status': True,
                        'status_code': 200,
                        'response': {
                            'message': f'{employee.full_name} isn’t available on the selected time {st_time} and {ed_time}, but your team member can still book appointments for them.',
                            'error_message': f'This Employee day off, {employee.full_name} date {date}',
                            'Availability': False
                        }
                    },
                    status=status.HTTP_200_OK
                )

        except Exception as err:
            return Response(
                {
                    'status': True,
                    'status_code': 200,
                    'response': {
                        'message': f' This staff is not working on this day but your team member can still book an appointment for them.',
                        'error_message': f'This Employee day off, {employee.full_name} date {date} {str(err)}',
                        'Availability': False
                    }
                },
                status=status.HTTP_200_OK
            )
        try:
            av_staff_ids = AppointmentService.objects.filter(
                Q(appointment_time__range=(start_time, tested)) | Q(end_time__range=(start_time, tested)),
                member__id=employee.id,
                appointment_date=date,
                # is_blocked = False,
            ).exclude(appointment_status='Cancel')
            if len(av_staff_ids) > 0:
                st_time = convert_24_to_12(str(start_time))
                ed_time = convert_24_to_12(str(tested))
                data.append(AppointmentServiceSerializer(av_staff_ids, many=True).data)
                return Response(
                    {
                        'status': True,
                        'status_code': 200,
                        'status_code_text': '200',
                        'response': {
                            'message': f'{employee.full_name} isn’t available between {st_time} and {ed_time}, but your team member can still book appointments for them.',
                            'error_message': f'Appointments Found ({len(av_staff_ids)})',
                            'employee': data,
                            'extra_data': {
                                'start_time': start_time,
                                'end_time': tested,
                            }
                        }
                    },
                    status=status.HTTP_200_OK
                )

            for ser in av_staff_ids:
                if tested <= ser.appointment_time:
                    if start_time >= ser.end_time:
                        return Response(
                            {
                                'status': True,
                                'status_code': 200,
                                'status_code_text': '200',
                                'response': {
                                    'message': '',
                                    'error_message': None,
                                    'employee': data,
                                }
                            },
                            status=status.HTTP_200_OK
                        )
                        # data.append(f'Employees are free, employee name {employee.full_name}')

                    else:
                        st_time = convert_24_to_12(str(start_time))
                        ed_time = convert_24_to_12(str(tested))
                        return Response(
                            {
                                'status': True,
                                'status_code': 200,
                                'status_code_text': '200',
                                'response': {
                                    'message': f'{employee.full_name} isn’t available between {st_time} and {ed_time}, but your team member can still book appointments for them.',
                                    'error_message': None,
                                    'employee': data,
                                }
                            },
                            status=status.HTTP_200_OK
                        )
                        # data.append(f'{employee.full_name} isn’t available between {st_time} and {ed_time}, but your team member can still book appointments for them.')

                else:
                    data.append(f'The selected staff is not available at this time {employee.full_name}')
                    data.append(f'{tested}')
                    data.append(f'{ser.appointment_time}')
                    return Response(
                        {
                            'status': True,
                            'status_code': 200,
                            'status_code_text': '200',
                            'response': {
                                'message': f'The selected staff is not available at this time  {employee.full_name}',
                                'error_message': None,
                                'employee': data,
                            }
                        },
                        status=status.HTTP_200_OK
                    )
                    Availability = False

            if len(av_staff_ids) == 0:
                data.append(f'Employees are free, you can proceed further employee name {employee.full_name}')

        except Exception as err:
            data.append(f'the employe{employee}, start_time {str(err)}')
    except Exception as err:
        data.append(f'the Error  {str(err)},  Employee Not Available on this time')

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': '',
                'error_message': None,
                'employee': data,
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def get_employee_check_availability_list(request):
    check_availability = request.data.get('check_availability', None)
    appointment_date = request.data.get('appointment_date', None)

    if check_availability is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'check_availability',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if type(check_availability) == str:
        check_availability = json.loads(check_availability)
    else:
        pass

    data = []
    data_list = []

    for check in check_availability:
        emp_id = check.get('member', None)
        duration = check.get('duration', None)
        duration_res = check.get('duration', None)
        start_time = check.get('date_time', None)

        srv_name = check.get('srv_name', None)
        price = check.get('price', None)
        srv_duration = check.get('srv_duration', None)

        client_can_book = check.get('client_can_book', None)
        slot_availible_for_online = check.get('slot_availible_for_online', None)
        date = check.get('appointment_date', appointment_date)

        index = check.get('index', None)
        message = check.get('message', None)
        service = check.get('service', None)

        dtime = datetime.strptime(start_time, "%H:%M:%S")
        start_time = dtime.time()

        dt = datetime.strptime(date, "%Y-%m-%d")
        date = dt.date()

        app_date_time = f'2000-01-01 {start_time}'

        duration = DURATION_CHOICES[duration]
        app_date_time = datetime.fromisoformat(app_date_time)
        datetime_duration = app_date_time + timedelta(minutes=duration)
        datetime_duration = datetime_duration.strftime('%H:%M:%S')
        tested = datetime.strptime(datetime_duration, '%H:%M:%S').time()
        end_time = datetime_duration

        try:
            data_object = {}
            employee = Employee.objects.get(
                id=emp_id,
            )
            try:
                daily_schedule = EmployeDailySchedule.objects.get(
                    employee=employee,
                    is_vacation=False,
                    date=date,
                )
                if start_time >= daily_schedule.start_time and start_time < daily_schedule.end_time:
                    pass
                elif daily_schedule.start_time_shift != None:
                    if start_time >= daily_schedule.start_time_shift and start_time < daily_schedule.end_time_shift:
                        pass
                    else:
                        data_object.update({
                            'date_time': start_time,
                            'client_can_book': client_can_book,
                            'slot_availible_for_online': slot_availible_for_online,
                            'duration': duration_res,
                            'srv_name': srv_name,
                            'price': price,
                            'srv_duration': srv_duration,
                            'member': emp_id,
                            'appointment_date': date,
                            'index': index,
                            'service': service,
                            'message': f'{employee.full_name} isn’t available on the selected date {st_time} and {ed_time}, but your team member can still book appointments for them.',
                        })
                        data_list.append(data_object)
                        continue

                else:
                    st_time = convert_24_to_12(str(start_time))
                    ed_time = convert_24_to_12(str(tested))
                    data_object.update({
                        'date_time': start_time,
                        'client_can_book': client_can_book,
                        'slot_availible_for_online': slot_availible_for_online,
                        'duration': duration_res,
                        'srv_name': srv_name,
                        'price': price,
                        'srv_duration': srv_duration,
                        'member': emp_id,
                        'appointment_date': date,
                        'index': index,
                        'service': service,
                        'message': f'{employee.full_name} isn’t available on the selected date {st_time} and {ed_time}, but your team member can still book appointments for them.',
                    })
                    data_list.append(data_object)
                    continue


            except Exception as err:
                data_object.update({
                    'date_time': start_time,
                    'client_can_book': client_can_book,
                    'slot_availible_for_online': slot_availible_for_online,
                    'duration': duration_res,
                    'srv_name': srv_name,
                    'price': price,
                    'srv_duration': srv_duration,
                    'member': emp_id,
                    'appointment_date': date,
                    'index': index,
                    'service': service,
                    'message': f' This staff is not working on this day but your team member can still book an appointment for them.',
                })
                data_list.append(data_object)
                continue
                # pass

            try:
                av_staff_ids = AppointmentService.objects.filter(
                    member__id=employee.id,
                    appointment_date=date,
                    is_blocked=False,
                )

                for ser in av_staff_ids:
                    if tested <= ser.appointment_time:
                        if start_time >= ser.end_time:
                            data.append(f'Employees are free, employee name {employee.full_name}')

                        else:
                            st_time = convert_24_to_12(str(start_time))
                            ed_time = convert_24_to_12(str(tested))
                            data_object.update({
                                'date_time': start_time,
                                'client_can_book': client_can_book,
                                'slot_availible_for_online': slot_availible_for_online,
                                'duration': duration_res,
                                'srv_name': srv_name,
                                'price': price,
                                'srv_duration': srv_duration,
                                'member': emp_id,
                                'appointment_date': date,
                                'index': index,
                                'service': service,
                                'message': f'{employee.full_name} isn’t available on the selected date {st_time} and {ed_time}, but your team member can still book appointments for them.',
                            })
                            data_list.append(data_object)
                            continue
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
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Employee Availability',
                'error_message': None,
                'employee': data_list,
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_appointment_logs(request):
    location_id = request.GET.get('location_id', None)
    appointment_id = request.GET.get('appointment_id', None)

    if not all([location_id, appointment_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'location_id',
                        'appointment_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    appointment_logs = AppointmentLogs.objects.filter(
        location__id=location_id,
        appointment__id=appointment_id,
        location__is_deleted=False,
        is_deleted=False,
        is_active=True,
    ).order_by('-created_at')

    serialized = AppointmenttLogSerializer(appointment_logs, many=True)

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Appointment Logs',
                'error_message': None,
                'appointment_logs': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def appointment_service_status_update(request):
    appointment_id = request.data.get('appointment_id', None)
    appointment_service_id = request.data.get('appointment_service_id', None)
    appointment_service_status = request.data.get('status', None)
    service_void_reason = request.data.get('cancel_reason', None)
    # appointment_checkin_time = request.data.get('checkin_time', None)
    gst_price = None
    gst_price1 = None

    seperate_or_combined = None
    group_or_individual = None

    status_list = [choices.AppointmentServiceStatus.STARTED, choices.AppointmentServiceStatus.FINISHED]

    # changing the status
    appointment = Appointment.objects.get(id=appointment_id)
    appointment_service = AppointmentService.objects.get(id=appointment_service_id)
        
    appointment_service.status = appointment_service_status
    if appointment_service_status == choices.AppointmentServiceStatus.STARTED:
        appointment.status = 'Started'
        appointment.save()
        # Appointment Checkin time not exist 
        if appointment.check_in_time is None:
            # Appointment Checkin time when service started
            appointment.check_in_time = datetime.now()
            appointment.save()    
        appointment_service.service_start_time = datetime.now()
    elif appointment_service_status == choices.AppointmentServiceStatus.FINISHED:
        appointment_service.service_end_time = datetime.now()
    elif appointment_service_status == choices.AppointmentServiceStatus.VOID:
        appointment_service.reason=service_void_reason
    appointment_service.save()

    # # Appointment sperate Checkin time 
    # if appointment_checkin_time:
    #     appointment.check_in_time = datetime.now()
    #     appointment.save()
            
    appoint_service_statuses = list(
        AppointmentService.objects.filter(appointment=appointment).values_list('status', flat=True))

    is_all_finished = all(
        [True if status == choices.AppointmentServiceStatus.FINISHED else False for status in appoint_service_statuses]
        )
    is_all_void = all(
        [True if status == choices.AppointmentServiceStatus.VOID else False for status in appoint_service_statuses])
    is_all_started = all(
        [True if status == choices.AppointmentServiceStatus.STARTED else False for status in appoint_service_statuses])

    if "Started" in appoint_service_statuses:
        appointment.status = choices.AppointmentStatus.STARTED
        appointment.save()
    elif (is_all_finished or is_all_void) or (not is_all_started):
        appointment.status = choices.AppointmentStatus.FINISHED
        appointment.save()
    else:
        appointment.status = choices.AppointmentStatus.STARTED
        appointment.save()

    # When there is any appointment started make the appointment checkout here,
    # so that we can calculate the tax and the service prices using query
    # to monitor paid and unpaid appointment checkouts.
    # If all Void then don't create the checkout.
    any_service_started_or_funished = AppointmentService.objects.filter(
        appointment=appointment,
    ).exclude(status=choices.AppointmentServiceStatus.VOID)
    status_started_finished = appointment_service_status in status_list

    if any_service_started_or_funished.exists() or status_started_finished:
        appointment_checkout, created = AppointmentCheckout.objects.get_or_create(
            appointment=appointment,
            business_address=appointment.business_address
        )

        # save method is being called in apply_texes method.
        appointment_checkout.apply_taxes()

    serialized = AppointmentServiceSerializerBasic(appointment_service)

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Appointment Service',
                'error_message': None,
                'appointment_service': serialized.data,
                'seperate_or_combined': seperate_or_combined,
                'group_or_individual': group_or_individual,
                'appoint_service_statuses' : appoint_service_statuses,
                'is_all_finished' : [True if status == choices.AppointmentServiceStatus.FINISHED else False for status in appoint_service_statuses],
                'is_all_void' : [True if status == choices.AppointmentServiceStatus.VOID else False for status in appoint_service_statuses],
                'is_all_started' : [True if status == choices.AppointmentServiceStatus.STARTED else False for status in appoint_service_statuses]

            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def paid_unpaid_clients(request):
    location_id = request.GET.get('location_id', None)
    no_pagination = request.GET.get('no_pagination', None)
    is_paid = request.GET.get('is_paid', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    search_text = request.GET.get('search_text', None)

    query = Q()

    if is_paid == 'paid':
        query &= Q(appointment__status=choices.AppointmentStatus.DONE)

    if is_paid == 'unpaid':
        query &= ~Q(appointment__status=choices.AppointmentStatus.DONE)

    if location_id:
        query &= Q(business_address__id=location_id)

    if search_text:
        search_text = search_text.replace('#', '')
        query &= Q(appointment__client__full_name__icontains=search_text) | \
                 Q(appointment__id__icontains=search_text)

    if start_date and end_date:
        query &= Q(created_at__date__range=get_date_range_tuple(start_date, end_date))

    appointment_checkouts = AppointmentCheckout.objects \
        .select_related('appointment') \
        .filter(query) \
        .with_payment_status() \
        .with_client_name() \
        .with_payment_date() \
        .with_subtotal() \
        .with_total_tax() \
        .order_by('-created_at')

    serialized = list(PaidUnpaidAppointmentCheckoutSerializer(appointment_checkouts, many=True).data)

    paginator = CustomPagination()
    paginator.page_size = 100000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'appointments')
    return response


@api_view(['POST'])
@transaction.atomic
def create_missed_opportunity(request):
    client_type = request.data.get('client_type', None)
    client_id = request.data.get('client', None)
    opportunity_date = request.data.get('opportunity_date', None)
    note = request.data.get('notes', None)
    dependency = request.data.get('dependency', None)
    services_data = format_json_string(request.data.get('services', None))
    location_id = request.data.get('location_id', None)
    client = None

    services_list = []

    location = BusinessAddress.objects.get(id=location_id)
    if client_id:
        client = Client.objects.get(id=client_id)

    client_opportunity = ClientMissedOpportunity.objects.create(
        location=location,
        client=client,
        client_type=client_type,
        date_time=opportunity_date,
        dependency=dependency,
        note=note,
    )

    for data in services_data:
        employee_id = data.get('employee_id', None)
        employee = None

        if employee_id:
            try:
                employee = Employee.objects.get(id=employee_id)
            except Employee.DoesNotExist:
                pass  # Handle the case where the employee doesn't exist if needed

        service = Service.objects.get(id=data['service_id'])

        # Check if employee is not None before creating OpportunityEmployeeService
        if employee is not None:
            services_list.append(
                OpportunityEmployeeService(
                    client_missed_opportunity=client_opportunity,
                    employee=employee,
                    service=service,
                    duration=data['duration'],
                    time=data['time']
                )
            )
        else:
            # Handle the case where employee is None (skip or provide a default)
            pass

    OpportunityEmployeeService.objects.bulk_create(services_list)

    serializer = MissedOpportunityBasicSerializer(client_opportunity)
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Missed opportunity created',
                'error_message': None,
                'missed_opportunity': serializer.data
            }
        },
        status=status.HTTP_200_OK
    )


class MissedOpportunityListCreate(generics.ListAPIView,
                                  generics.DestroyAPIView,
                                  generics.RetrieveAPIView):
    serializer_class = MissedOpportunityBasicSerializer
    queryset = ClientMissedOpportunity.objects \
        .select_related('client')
    pagination_class = PageNumberPagination
    lookup_field = 'id'  # Specify the lookup field as 'id' for UUID
    lookup_url_kwarg = 'id'

    def list(self, request, *args, **kwargs):
        search_text = request.query_params.get('search_text', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        location_id = request.query_params.get('location_id', None)

        query = Q()

        if location_id:
            query &= Q(location__id=location_id)
        if search_text:
            query &= Q(client__full_name__icontains=search_text)

        if start_date and end_date:
            query &= Q(date_time__date__range=get_date_range_tuple(start_date, end_date))

        queryset = self.get_queryset().filter(query).order_by('-created_at')

        page = self.paginate_queryset(queryset)
        data = None

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
            response_data['pages'] = self.paginator.page.paginator.num_pages
            data = response_data

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'All missed opportunities',
                'error_message': None,
                'missed_opportunities': data
            }
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Missed opportunity retrieved successfully',
                'error_message': None,
                'missed_opportunity': serializer.data
            }
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Missed opportunity deleted successfully',
                'error_message': None,
            }
        }, status=status.HTTP_200_OK)


@api_view(['PUT'])
def cancel_appointment(request):
    appointment_id = request.data.get('appointment_id', None)
    cancel_reason = request.data.get('reason', None)
    cancel_note = request.data.get('cancel_note', None)

    if appointment_id:
        appointment = Appointment.objects.get(id=appointment_id)
        appointment.status = choices.AppointmentStatus.CANCELLED
        appointment.cancel_reason = cancel_reason
        appointment.cancel_note = cancel_note

        appointment.save()

    serializer = AppointmentSerializerForStatus(appointment)

    return Response({
        'status': True,
        'status_code': 200,
        'response': {
            'message': 'Appointment Cancelled',
            'error_message': None,
            'appointment': serializer.data
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_available_appointments(request):
    appointment_status = request.GET.get('appointment_status', None)
    appointment_id = request.GET.get('appointment_id', None)
    client_id = request.GET.get('client_id', None)
    employee_id = request.GET.get('employee_id', None)
    booking_id = request.GET.get('booking_id', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    no_pagination = request.GET.get('no_pagination', None)
    location_id = request.GET.get('location', None)
    search_text = request.GET.get('search_text', None)
    
    try:
        query = Q(is_deleted=False)
        if appointment_status is not None:
            query &= Q(status__icontains=appointment_status)
        if search_text:
            search_text = search_text.replace('#', '')
            query &= Q(client__full_name__icontains=search_text) | \
                    Q(id__icontains=search_text)
                    
        if start_date and end_date:
            query &= Q(appointment_services__appointment_date__range=(start_date, end_date))
        if location_id is not None:
            query &= Q(business_address__id=location_id)
        if appointment_id is not None:
            query &= Q(id=appointment_id)
        if booking_id is not None:
            query &= Q(appointment_services__id=booking_id)

        appointment = Appointment.objects.filter(query).distinct('id')

    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_APPOINMENT_ID_4038,
                'status_code_text': 'INVALID_APPOINMENT_ID_4038',
                'response': {
                    'message': 'Appointment Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    if no_pagination:
        serialized = SingleNoteResponseSerializer(appointment, many=True)
        return Response(
            {
                'status': True,
                'status_code': 200,
                'status_code_text': '200',
                'response': {
                    'message': 'All Appointments',
                    'error_message': None,
                    'data': serialized.data
                }
            },
            status=status.HTTP_200_OK
        )
    else:
        paginator = AppointmentsPagination()
        paginator.page_size = 10
        paginated_appointments = paginator.paginate_queryset(appointment, request)
        serialized = SingleNoteResponseSerializer(paginated_appointments, many=True)
        data = {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            "response": {
                "message": "Appointments  get Successfully",
                "error_message": None,
                "data": serialized.data,
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'current_page': paginator.page.number,
                'per_page': paginator.page_size,
                'total_pages': paginator.page.paginator.num_pages,
            }
        }
        return Response(data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([AllowAny])
def update_reversals(request):
    id = request.data.get('id', None)
    request_status = request.data.get('request_status', None)
    appointment_id = request.data.get("appointment_id", None)
    service_id = request.data.get("service_id", None)
    stat = request.data.get("status", None)

    if stat == "accepted":
        all_services = AppointmentService.objects.filter(appointment_id=appointment_id).exclude(status='void')
        qs = all_services.annotate(
            condition_check=Case(
                When(~Q(status='Started'), then=Value(True)),
                When(~Q(status='Finished'), then=Value(True)),
                default=Value(False),
                output_field=models.BooleanField(),
            )
        )
        check_status = qs.filter(condition_check=True)
        if check_status:
            Appointment.objects.filter(id=appointment_id).update(status='Booked')
            reversal = AppointmentService.objects.filter(appointment_id=appointment_id, id=service_id).update(
                status=request_status, service_start_time=None, service_end_time=None
            )
            Reversal.objects.filter(appointment_id=appointment_id, appointment_services_id=service_id).update(
                request_status=stat
            )
            data = {
                'status': True,
                'status_code': 200,
                'response': {
                    'message': 'Reversal Status Updated Successfully',
                    'error_message': None,
                }
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            reversal = AppointmentService.objects.filter(appointment_id=appointment_id, id=service_id).update(
                status=request_status, service_start_time=None, service_end_time=None
            )
            Reversal.objects.filter(appointment_id=appointment_id, appointment_services_id=service_id).update(
                request_status=stat
            )
            data = {
                'status': True,
                'status_code': 200,
                'response': {
                    'message': 'Reversal Status Updated Successfully',
                    'error_message': None,
                }
            }
            return Response(data, status=status.HTTP_200_OK)

    else:
        Reversal.objects.filter(appointment_id=appointment_id, appointment_services_id=service_id).update(
            request_status='rejected'
        )
        data = {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Reversal Status Updated Successfully',
                'error_message': None,
            }
        }
        return Response(data, status=status.HTTP_200_OK)

# Update Appointment check-in time ---------------------------------------------------
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_appointment_check_in(request):
    appointment_id = request.data.get('appointment_id', None)
    
    if appointment_id:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        appointment.check_in_time = datetime.now()
        appointment.save()
        appointment_data = CheckInSerializer(appointment).data
        data = {
                'status': True,
                'status_code': 200,
                'response': {
                    'message': 'Appointment Checked In Successfuly',
                    'error_message': None,
                    'Appointment' : appointment_data
                }
            }
        return Response(data, status=status.HTTP_200_OK)
    else :
        data = {
                'status': True,
                'status_code': 200,
                'response': {
                    'message': 'Appointment Checked In Failed',
                    'error_message': 'Missing Appointment ID',
                }
            }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


# Group Appointment Check-in ------------------------------------------     
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_group_appointment_check_in(request):
    group_appointment_id = request.data.get('group_appointment_id', None)
    
    if group_appointment_id:
        group_appointment = get_object_or_404(AppointmentGroup, id=group_appointment_id)
        # group_appointment.appointments.update(check_in_time=timezone.now())
        
        # Update each appointment individually
        for appointment in group_appointment.appointment.all():
            if appointment.check_in_time is None:
                appointment.check_in_time = timezone.now()
                appointment.save()
        
        group_appointment.group_check_in_time = timezone.now()
        group_appointment.save()
        
        group_appointment_data = GroupCheckInSerializer(group_appointment).data
        data = {
                'status': True,
                'status_code': 200,
                'response': {
                    'message': 'Group Checked In Successfuly',
                    'error_message': None,
                    'group_appointment' : group_appointment_data
                }
            }
        return Response(data, status=status.HTTP_200_OK)
    else :
        data = {
                'status': True,
                'status_code': 200,
                'response': {
                    'message': 'Group Checked In Failed',
                    'error_message': 'Missing Group Appointment ID',
                }
            }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    
# Appointment Time Report ----------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_time_report(request):
    appointment_id = request.query_params.get('appointment_id', None)
    appointment_service = request.query_params.get('appointment_service', None)
    
    if appointment_id and appointment_service:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        appointment_service  = get_object_or_404(AppointmentService, id=appointment_service)
        serializers = AppointmentTimeReportSerializer(appointment)
        appointment_service_serializer =AppointmentServiceTimeSerializer(appointment_service)
        
        data = {
                'status': True,
                'status_code': 200,
                'response': {
                    'message': 'Appointment Time Report Successfuly',
                    'error_message': None,
                    'data' : {
                        'appointment' : serializers.data,
                        'appointment_service' : appointment_service_serializer.data
                    }
                }
            }
        return Response(data, status=status.HTTP_200_OK)
    else:
        appointment = Appointment.objects.all()
        appointment_service = AppointmentService.objects.all()
        serializers = AppointmentTimeReportSerializer(appointment, many=True)
        appointment_service_serializer =AppointmentServiceTimeSerializer(appointment_service, many=True)
        data = {
                'status': True,
                'status_code': 200,
                'response': {
                    'message': 'All Appointment Time Report Failed',
                    'error_message': None,
                    'data': {
                        'appointment' : serializers.data,
                        'appointment_service' : appointment_service_serializer.data
                    }
                }
            }
        return Response(data, status=status.HTTP_200_OK)
