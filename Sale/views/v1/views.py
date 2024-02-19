from datetime import timedelta
import datetime
from threading import Thread
from django.shortcuts import render

from Promotions.models import Coupon
from Sale.Constants.StaffEmail import StaffSaleEmail
from Sale.Constants.stock_lowest import stock_lowest
from Sale.Constants.tunrover import ProductTurnover
from django.db import transaction

from rest_framework import status
from Appointment.models import Appointment, AppointmentCheckout, AppointmentService, AppointmentEmployeeTip
from Business.models import AdminNotificationSetting, Business, StaffNotificationSetting, StockNotificationSetting
from Client.models import Client, Membership, Vouchers, LoyaltyPoints, LoyaltyPointLogs, ClientLoyaltyPoint
from Client.Constants.client_order_email import send_order_email, send_membership_order_email
from Order.models import Checkout, MemberShipOrder, Order, ProductOrder, ServiceOrder, VoucherOrder
from Sale.Constants.Custom_pag import CustomPagination
from Utility.Constants.Data.months import MONTHS
from Utility.models import Country, Currency, ExceptionRecord, State, City
from Authentication.models import User
from NStyle.Constants import StatusCodes
import json

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from Employee.models import CategoryCommission, CommissionSchemeSetting, Employee, EmployeeSelectedService, \
    EmployeeCommission
from Business.models import BusinessAddress
from Service.models import PriceService, Service, ServiceGroup

from Product.models import Product, ProductOrderStockReport, ProductStock
from django.db.models import Avg, Count, Min, Sum, Q, F

from Sale.serializers import (AppointmentCheckoutSerializer, BusinessAddressSerializer, CheckoutSerializer,
                              MemberShipOrderSerializer,
                              ProductOrderSerializer, ServiceGroupSerializer, ServiceOrderSerializer, ServiceSerializer,
                              VoucherOrderSerializer, SaleOrders_CheckoutSerializer,
                              SaleOrders_AppointmentCheckoutSerializer,
                              ServiceSerializerDropdown, ServiceSerializerOP, ServiceGroupSerializerOP,
                              SaleOrders_CheckoutSerializerOP,
                              SaleOrders_AppointmentCheckoutSerializerOP, ServiceSerializerMainpage,
                              ServiceGroupSerializerMainPage,
                              ServiceGroupSerializerOptimized
                              )
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from Invoices.models import SaleInvoice
from datetime import datetime as dt
from Reports.models import DiscountPromotionSalesReport
from Service.models import ServiceTranlations
from Utility.models import Language
from Business.serializers.v1_serializers import BusinessAddressSerilaizer
from Appointment import choices


@api_view(['GET'])
@permission_classes([AllowAny])
def get_service(request):
    location = request.GET.get('location_id', None)
    is_mobile = request.GET.get('is_mobile', None)
    search_text = request.GET.get('search_text', None)
    no_pagination = request.GET.get('no_pagination', None)
    service_id = request.GET.get('service_id', None)

    query = Q(is_deleted=False)

    location_instance = None
    currency_code = None
    errors = []

    if search_text:
        query &= Q(name__icontains=search_text) | \
                 Q(servicegroup_services__name__icontains=search_text) | \
                 Q(location__address_name__icontains=search_text)

    if location:
        query &= Q(location__id=location)

    if service_id:
        query &= Q(id=service_id)

    elif request.user.is_authenticated:
        try:
            employee = Employee.objects.get(
                email=request.user.email
            )
        except Exception as err:
            errors.append(str(err))
        else:
            if len(employee.location.all()) > 0:
                first_location = employee.location.all()[0]
                location_instance = first_location
                currency_code = location_instance.currency.code
                query &= Q(location__id=first_location.id)
            else:
                errors.append('Employee Location 0')

    services = Service.objects \
        .filter(query) \
        .with_total_orders() \
        .order_by('-total_orders') \
        .distinct()

    # if is_mobile then request.user will be employee
    # so we will filter only those services which are assigned to
    # that particular employee
    if is_mobile:
        emp = Employee.objects.get(email=request.user.email)
        emp_service_ids = emp.employee_selected_service.distinct().values_list('service__id', flat=True)
        services = Service.objects.filter(id__in=emp_service_ids).order_by('-created_at')

    service_count = services.count()

    page_count = service_count / 10
    if page_count > int(page_count):
        page_count = int(page_count) + 1
    per_page_results = 100000 if no_pagination else 10
    paginator = Paginator(services, per_page_results)
    page_number = request.GET.get("page")
    services = paginator.get_page(page_number)

    serialized = ServiceSerializer(services, many=True,
                                   context={'request': request, 'location_instance': location_instance,
                                            'is_mobile': is_mobile, 'currency_code': currency_code})
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Service',
                'count': service_count,
                'pages': page_count,
                'per_page_result': 20,
                'error_message': None,
                'service': serialized.data,
                'errors': errors,
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_service_main_page(request):
    location = request.GET.get('location_id', None)
    is_mobile = request.GET.get('is_mobile', None)
    search_text = request.GET.get('search_text', None)
    no_pagination = request.GET.get('no_pagination', None)

    query = Q(is_deleted=False)

    location_instance = None
    currency_code = None
    errors = []

    if search_text:
        query &= Q(name__icontains=search_text) | \
                 Q(servicegroup_services__name__icontains=search_text) | \
                 Q(location__address_name__icontains=search_text)

    if location:
        query &= Q(location__id=location)

    elif request.user.is_authenticated:
        try:
            employee = Employee.objects.get(
                email=request.user.email
            )
        except Exception as err:
            errors.append(str(err))
        else:
            if len(employee.location.all()) > 0:
                first_location = employee.location.all()[0]
                location_instance = first_location
                currency_code = location_instance.currency.code
                query &= Q(location__id=first_location.id)
            else:
                errors.append('Employee Location 0')

    services = Service.objects \
        .filter(query) \
        .prefetch_related('location',
                          'servicegroup_services',
                          'employee_service',
                          'employee_service',
                          'service_priceservice') \
        .with_total_orders() \
        .order_by('-total_orders') \
        .distinct()

    # if is_mobile then request.user will be employee
    # so we will filter only those services which are assigned to
    # that particular employee
    if is_mobile:
        emp = Employee.objects.get(email=request.user.email)
        emp_service_ids = emp.employee_selected_service.distinct().values_list('service__id', flat=True)
        services = Service.objects.filter(id__in=emp_service_ids).order_by('-created_at')

    service_count = services.count()

    page_count = service_count / 10
    if page_count > int(page_count):
        page_count = int(page_count) + 1
    per_page_results = 100000 if no_pagination else 10
    paginator = Paginator(services, per_page_results)
    page_number = request.GET.get("page")
    services = paginator.get_page(page_number)

    serialized = ServiceSerializerMainpage(services, many=True, context={'request': request})
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Service',
                'count': service_count,
                'pages': page_count,
                'per_page_result': 20,
                'error_message': None,
                'service': serialized.data,
                'errors': errors,
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_service_optimized(request):
    location_id = request.GET.get('location_id', None)
    is_mobile = request.GET.get('is_mobile', None)
    search_text = request.GET.get('search_text', None)
    no_pagination = request.GET.get('no_pagination', None)
    aval_service_group_id = None
    servicegroup_ids = []
    service_list = []
    query = Q(is_deleted=False)

    currency = BusinessAddress.objects.get(id=location_id).currency
    if currency:
        # filter out those services which has the currency price for the current location currency.
        service_ids = list(PriceService.objects.filter(currency=currency).values_list('service__id', flat=True))
        query &= Q(id__in=service_ids)

    location_instance = None
    currency_code = None
    errors = []

    if search_text:
        query &= Q(name__icontains=search_text) | \
                 Q(servicegroup_services__name__icontains=search_text) | \
                 Q(location__address_name__icontains=search_text)

    if location_id:
        query &= Q(location__id=location_id)

    elif request.user.is_authenticated:
        try:
            employee = Employee.objects.get(
                email=request.user.email
            )
        except Exception as err:
            errors.append(str(err))
        else:
            if len(employee.location.all()) > 0:
                first_location = employee.location.all()[0]
                location_instance = first_location
                currency_code = location_instance.currency.code
                query &= Q(location__id=first_location.id)
            else:
                errors.append('Employee Location 0')
    services = Service.objects.filter(query).order_by('-created_at').distinct()
    for service in services:
        service_list.append(service.name)
        all_groups = ServiceGroup.objects.filter(id=service.id)
        for group in all_groups:
             servicegroup_ids.append(group.id)

    # if is_mobile then request.user will be employee
    # so we will filter only those services which are assigned to
    # that particular employee
    if is_mobile:
        emp = Employee.objects.get(email=request.user.email)
        emp_service_ids = emp.employee_selected_service.distinct().values_list('service__id', flat=True)
        services = Service.objects.filter(id__in=emp_service_ids).order_by('-created_at')

    service_count = services.count()

    page_count = service_count / 10
    if page_count > int(page_count):
        page_count = int(page_count) + 1
    per_page_results = 100000 if no_pagination else 10
    paginator = Paginator(services, per_page_results)
    page_number = request.GET.get("page")
    services = paginator.get_page(page_number)

    serialized = ServiceSerializerOP(services, many=True,
                                     context={'request': request, 'location_instance': location_instance,
                                              'is_mobile': is_mobile, 'currency_code': currency_code})
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Service',
                'count': service_count,
                'pages': page_count,
                'per_page_result': 20,
                'error_message': None,
                'service': serialized.data,
                'errors': errors,
                'service_group': aval_service_group_id,
                'servicegroup_ids': servicegroup_ids,
                'service_list':service_list
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_service_dropdown(request):
    location = request.GET.get('location_id', None)
    is_mobile = request.GET.get('is_mobile', None)
    search_text = request.GET.get('search_text', None)
    page = request.GET.get('page', None)
    is_searched = False

    query = Q(is_deleted=False, is_active=True)
    location_instance = None
    errors = []

    if location:
        query &= Q(location__id=location)

    if search_text:
        query &= Q(name__icontains=search_text) | \
                 Q(servicegroup_services__name__icontains=search_text) | \
                 Q(location__address_name__icontains=search_text)
        is_searched = True

    elif request.user.is_authenticated:
        try:
            employee = Employee.objects.get(
                email=request.user.email
            )
        except Exception as err:
            errors.append(str(err))
        else:
            if len(employee.location.all()) > 0:
                first_location = employee.location.all()[0]
                location_instance = first_location
                currency_code = location_instance.currency.code
                query &= Q(location__id=first_location.id)
            else:
                errors.append('Employee Location 0')

    services = Service.objects.filter(query).order_by('-created_at').distinct()

    # if is_mobile then request.user will be employee
    # so we will filter only those services which are assigned to
    # that particular employee
    if is_mobile:
        emp = Employee.objects.get(email=request.user.email)
        emp_service_ids = emp.employee_selected_service.distinct().values_list('service__id', flat=True)
        service = service.filter(id__in=emp_service_ids)

    serialized = list(ServiceSerializerDropdown(services, many=True).data)
    paginator = CustomPagination()
    paginator.page_size = 10 if page else 100000
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'vendors', invoice_translations=None, current_page=page,
                                                is_searched=is_searched)
    return response


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_service(request):
    user = request.user
    business = request.data.get('business', None)

    name = request.data.get('name', None)
    staffgroup_id = request.data.get('staffgroup_id', None)
    service = request.data.get('service', None)

    description = request.data.get('description', None)
    employee = request.data.get('employee', None)
    location_id = request.data.get('location', None)

    service_availible = request.data.get('service_availible', None)

    priceservice = request.data.get('priceservice', None)

    controls_time_slot = request.data.get('controls_time_slot', None)
    initial_deposit = request.data.get('initial_deposit', None)
    client_can_book = request.data.get('client_can_book', None)
    slot_availible_for_online = request.data.get('slot_availible_for_online', None)

    enable_team_comissions = request.data.get('enable_team_comissions', None)
    enable_vouchers = request.data.get('enable_vouchers', None)
    is_package = request.data.get('is_package', None)

    invoices = request.data.get('invoices', None)
    image = request.data.get('image', None)

    if not all([business, name, description]):
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
                        'employee',
                        'name',
                        'description'
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
    '''
    Services are being Creating over here
    '''
    service_obj = Service.objects.create(
        user=user,
        business=business_id,
        name=name,
        description=description,
        service_availible=service_availible,
        controls_time_slot=controls_time_slot,
        initial_deposit=initial_deposit,
        client_can_book=client_can_book,
        slot_availible_for_online=slot_availible_for_online,
        enable_vouchers=enable_vouchers,
        image=image,

    )
    if enable_team_comissions is not None:
        service_obj.enable_team_comissions = True
    else:
        service_obj.enable_team_comissions = False

    service_obj.save()

    employees_error = []
    if is_package is not None:
        service_obj.is_package = True
        service_obj.save()
        if service is None:
            pass
        else:
            if type(service) == str:
                service = json.loads(service)

            elif type(service) == list:
                pass

            for ser in service:
                try:
                    service_id = Service.objects.get(id=ser)
                    service_obj.parrent_service.add(service_id)
                except Exception as err:
                    employees_error.append(str(err))

    service_obj.save()

    if type(employee) == str:
        employee = json.loads(employee)

    elif type(employee) == list:
        pass

    for usr in employee:
        try:
            employe = Employee.objects.get(id=usr)
            employe_service = EmployeeSelectedService.objects.create(
                service=service_obj,
                employee=employe
            )
        except:
            employees_error.append(str(err))
            pass

    if type(location_id) == str:
        location_id = json.loads(location_id)

    elif type(location_id) == list:
        pass

    for usr in location_id:
        try:
            location = BusinessAddress.objects.get(id=usr)
            print(location)
            service_obj.location.add(location)
        except Exception as err:
            employees_error.append(str(err))

    employe_service.save()
    service_obj.save()

    try:
        service_group = ServiceGroup.objects.get(id=staffgroup_id)
        service_group.services.add(service_obj)
        service_group.save()

    except Exception as err:
        employees_error.append(str(err))

    if priceservice is not None:
        if type(priceservice) == str:
            priceservice = priceservice.replace("'", '"')
            priceservice = json.loads(priceservice)
        else:
            pass
        for ser in priceservice:
            try:
                duration = ser['duration']
                price = ser['price']
                currency = ser['currency']

                try:
                    currency_id = Currency.objects.get(id=currency)
                except Exception as err:
                    pass

                price_service = PriceService.objects.create(
                    service=service_obj,
                    currency=currency_id,
                    duration=duration,
                    price=price,
                )
            except Exception as err:
                employees_error.append(str(err))

    if invoices is not None:
        if type(invoices) == str:
            invoices = invoices.replace("'", '"')
            invoices = json.loads(invoices)
        else:
            pass
        for invoice in invoices:
            try:
                language = invoice['invoiceLanguage']
                service_name = invoice['service_name']
            except:
                pass
            else:
                serviceTranslation = ServiceTranlations(
                    service=service_obj,
                    service_name=service_name
                )
                language = Language.objects.get(id__icontains=str(language))
                serviceTranslation.language = language
                serviceTranslation.save()

    service_serializers = ServiceSerializer(service_obj, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Service Created Successfully!',
                'error_message': None,
                'employee_error': employees_error,
                'service': service_serializers.data,

            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_service(request):
    service_id = request.data.get('id', None)
    if id is None:
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
        service = Service.objects.get(id=service_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Service ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    service.is_deleted = True
    service.save()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Service deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_service(request):
    id = request.data.get('id', None)
    priceservice = request.data.get('priceservice', None)
    staffgroup_id = request.data.get('staffgroup_id', None)

    employeeslist = request.data.get('employee', None)
    service = request.data.get('service', None)
    location = request.data.get('location', None)
    check = True
    invoices = request.data.get('invoices', None)
    image = request.data.get('image', None)

    if id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Service ID are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        service_id = Service.objects.get(id=id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code_text': 'INVALID_SERVICE_ID',
                'response': {
                    'message': 'Service Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    error = []
    if image is not None :
        try:
            service_id.image = image
            service_id.save()
        except:
            pass
        
    if location is not None:
        if type(location) == str:
            location = json.loads(location)
        elif type(location) == list:
            pass
        service_id.location.clear()
        for loc in location:
            try:
                loca = BusinessAddress.objects.get(id=loc)
                service_id.location.add(loca)
            except Exception as err:
                error.append(f"error in locatoin update{str(err)}")

    if service is not None:
        if type(service) == str:
            service = json.loads(service)
        elif type(service) == list:
            pass
        service_id.parrent_service.clear()
        for usr in service:
            try:
                service = Service.objects.get(id=usr)
                service_id.parrent_service.add(service)
            except Exception as err:
                error.append(f"error usr service {str(err)}")

    if employeeslist is not None:
        if type(employeeslist) == str:
            employeeslist = json.loads(employeeslist)
        elif type(employeeslist) == list:
            pass
        all_pending_services = EmployeeSelectedService.objects.filter(service=service_id).exclude(
            employee__in=employeeslist)
        for empl_service in all_pending_services:
            empl_service.delete()

        for empl_id in employeeslist:
            try:
                employe = Employee.objects.get(id=empl_id)
                employe_service, created = EmployeeSelectedService.objects.get_or_create(
                    service=service_id,
                    employee=employe
                )

                # service_id.employee.add(employe)
            except Exception as err:
                error.append(f"error in employeelist loop {str(err)}")
    try:
        print(staffgroup_id)
        all_prev_ser_grops = ServiceGroup.objects.filter(services=service_id, is_deleted=False)
        for i in all_prev_ser_grops:
            i.services.remove(service_id)
            i.save()

        service_group = ServiceGroup.objects.get(id=staffgroup_id)
        service_group.services.add(service_id)
        service_group.save()

    except Exception as err:
        error.append(f"error in service group{str(err)}")

    if priceservice is not None:
        if check == True:
            vch = PriceService.objects.filter(service=service_id).order_by('-created_at')
            check = False
            for i in vch:
                try:
                    voucher = PriceService.objects.get(id=i.id)
                    voucher.delete()
                except:
                    pass

        if type(priceservice) == str:
            priceservice = priceservice.replace("'", '"')
            priceservice = json.loads(priceservice)
        else:
            pass
        
        sum = 0
        for ser in priceservice:
            sum = sum + 1
            s_service_id = ser.get('id', None)
            duration = ser.get('duration', None)
            price = ser.get('price', None)
            currency = ser.get('currency', None)
            is_deleted = ser.get('is_deleted', None)
            try:
                currency_id = Currency.objects.get(id=currency)
            except Exception as err:
                pass

            ser = Service.objects.get(id=id)
            PriceService.objects.create(
                service=ser,
                duration=duration,
                price=price,
                currency=currency_id
            )

    if invoices is not None:
        if type(invoices) == str:
            invoices = invoices.replace("'", '"')
            invoices = json.loads(invoices)
        else:
            pass

        old_data = ServiceTranlations.objects.filter(service=service_id)
        for old in old_data:
            old = ServiceTranlations.objects.get(id=old.id)
            old.delete()

        for invoice in invoices:
            try:
                language = invoice['invoiceLanguage']
                service_name = invoice['service_name']
            except:
                pass
            else:
                serviceTranslation = ServiceTranlations(
                    service=service_id,
                    service_name=service_name
                )
                language = Language.objects.get(id__icontains=str(language))
                serviceTranslation.language = language
                serviceTranslation.save()

    serializer = ServiceSerializer(service_id, context={'request': request}, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                'status': True,
                'status_code': 200,
                'response': {
                    'message': ' Service updated successfully',
                    'error_message': None,
                    'error': error,
                    'service': serializer.data,
                    'sum': sum,

                }
            },
            status=status.HTTP_200_OK
        )

    else:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.SERIALIZER_INVALID_4024,
                'response': {
                    'message': 'Invialid Data',
                    'error_message': str(serializer.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_servicegroup(request):
    user = request.user
    business = request.data.get('business', None)
    name = request.data.get('name', None)
    service = request.data.get('service', None)
    is_status = request.data.get('status', None)
    allow_client_to_select_team_member = request.data.get('allow_client_to_select_team_member', None)
    image = request.data.get('image', None)
    is_deleted = False
            
    servicegroup_error = []
    if not all([business, name]):
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
                        'service'

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
    service_group = ServiceGroup.objects.create(
        user=user,
        business=business_id,
        name=name,
        image=image,
        is_deleted=is_deleted,
    )
    if is_status is None:
        service_group.is_active = False
    else:
        service_group.is_active = True

    if allow_client_to_select_team_member is None:
        service_group.allow_client_to_select_team_member = False
    else:
        service_group.allow_client_to_select_team_member = True
    if service:
        if type(service) == str:
            service = json.loads(service)
        elif type(service) == list:
            pass

        for ser in service:
            try:
                services = Service.objects.get(id=ser)
                service_group.services.add(services)
            except Exception as err:
                servicegroup_error.append(str(err))
    service_group.save()
    serialized = ServiceGroupSerializer(service_group, context={'request': request})
    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Service Group Created!',
                'error_message': None,
                'service_group': serialized.data,
                'servicegroup_errors': servicegroup_error,
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_servicegroup(request):
    no_pagination = request.GET.get('no_pagination', None)
    search_text = request.GET.get('search_text', None)
    service_group_id = request.GET.get('service_group_id', None)

    query = Q(is_deleted=False)

    if service_group_id:
        query &= Q(id=service_group_id)

    if search_text:
        query &= Q(name__icontains=search_text)

    service_group = ServiceGroup.objects \
        .prefetch_related('services') \
        .filter(query).order_by('-created_at')
    serialized = list(ServiceGroupSerializer(service_group, many=True, context={'request': request}).data)

    paginator = CustomPagination()
    paginator.page_size = 100000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'sales')
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def get_servicegroup_main_page(request):
    no_pagination = request.GET.get('no_pagination', None)
    search_text = request.GET.get('search_text', '')
    is_active = request.GET.get('is_active', None)
    page = request.GET.get('page', None)
    is_searched = False

    query = {}

    if is_active:
        query['is_active'] = True

    if search_text:
        is_searched = True

    service_group = ServiceGroup.objects \
        .prefetch_related('services') \
        .filter(is_deleted=False, name__icontains=search_text, **query).order_by('-created_at')
    serialized = list(ServiceGroupSerializerMainPage(service_group, many=True,
                                                    context={'request': request}).data)

    paginator = CustomPagination()
    paginator.page_size = 100000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'sales', is_searched=is_searched, current_page=page)
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def get_servicegroup_optimized(request):
    location_id = request.GET.get('location_id', None)
    no_pagination = request.GET.get('no_pagination', None)
    search_text = request.GET.get('search_text', None)

    query = Q(is_deleted=False)
    if search_text:
        query &= Q(name__icontains=search_text)

    service_group = ServiceGroup.objects \
        .prefetch_related('services') \
        .filter(query).order_by('-created_at')
    serialized = list(ServiceGroupSerializerOptimized(service_group, many=True, context={'request': request,
                                                                                         'location_id': location_id}).data)

    paginator = CustomPagination()
    paginator.page_size = 100000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'sales')
    return response


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_servicegroup(request):
    service_id = request.data.get('id', None)
    if service_id is None:
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
        service_group = ServiceGroup.objects.get(id=service_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Invalid Service Group ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    service_group.is_deleted = True
    service_group.save()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'ServiceGroup deleted successfully',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_servicegroup(request):
    error = []
    service = request.data.get('service', None)
    id = request.data.get('id', None)

    is_status = request.data.get('status', None)
    allow_client_to_select_team_member = request.data.get('allow_client_to_select_team_member', None)

    if id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Service ID are required.',
                    'fields': [
                        'id'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        service_id = ServiceGroup.objects.get(id=id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code_text': 'INVALID_SERVICE_ID',
                'response': {
                    'message': 'ServiceGroup Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if is_status is None:
        service_id.is_active = False
    else:
        service_id.is_active = True

    if allow_client_to_select_team_member is None:
        service_id.allow_client_to_select_team_member = False
    else:
        service_id.allow_client_to_select_team_member = True

    if service is not None:
        if type(service) == str:
            service = json.loads(service)
        elif type(service) == list:
            pass
        service_id.services.clear()
        for ser in service:
            try:
                service = Service.objects.get(id=ser)
                service_id.services.add(service)
            except Exception as err:
                error.append(str(err))
    service_id.save()

    serializer = ServiceGroupSerializer(service_id, context={'request': request}, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                'status': True,
                'status_code': 200,
                'response': {
                    'message': ' ServiceGroup updated successfully',
                    'error_message': None,
                    'error': error,
                    'service': serializer.data

                }
            },
            status=status.HTTP_200_OK
        )

    else:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.SERIALIZER_INVALID_4024,
                'response': {
                    'message': 'Invalid Data',
                    'error_message': str(serializer.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_sale_orders(request):
    data = []
    checkout_order = Checkout.objects.filter(is_deleted=False)  # .order_by('-created_at')
    serialized = CheckoutSerializer(checkout_order, many=True, context={'request': request})
    data.extend(serialized.data)

    appointment_checkout = AppointmentCheckout.objects.filter(
        appointment_service__appointment_status='Done')  # .order_by('-created_at')
    serialized = AppointmentCheckoutSerializer(appointment_checkout,
                                               many=True,
                                               context={'request': request
                                                        })
    data.extend(serialized.data)

    sorted_data = sorted(data, key=lambda x: x['created_at'], reverse=True)

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Sale Orders',
                'error_message': None,
                'sales': sorted_data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_sale_orders_pagination(request):
    location_id = request.GET.get('location', None)
    range_start = request.GET.get('range_start', None)
    range_end = request.GET.get('range_end', None)
    no_pagination = request.GET.get('no_pagination', None)
    recent_five_sales = request.GET.get('recent_five_sales', False)
    search_text = request.GET.get('search_text', None)
    client_id = request.GET.get('client', None)
    service_id = request.GET.get('service', None)
    checkout_id = request.GET.get('checkout_id', None)

    sale_checkouts = None
    appointment_checkouts = None

    if range_end is not None:
        range_end = dt.strptime(range_end, '%Y-%m-%d').date()
        range_end = range_end + timedelta(days=1)
        range_end = str(range_end)

    queries = {}
    app_queries = {}
    sale_queries = {}

    if checkout_id:
        queries['id'] = checkout_id

    if range_start:
        queries['created_at__range'] = (range_start, range_end)

    if client_id:
        sale_queries['client__id'] = client_id
        app_queries['appointment__client__id'] = client_id

    if service_id:
        service_orders = ServiceOrder.objects.filter(
            service__id=service_id
        ).values_list('checkout', flat=True)

        sale_queries['id__in'] = list(service_orders)
        app_queries['appointment__appointment_services__service__id'] = service_id

    if search_text:
        # removing # for better search
        search_text = search_text.replace('#', '')
        sale_queries['client__full_name__icontains'] = search_text
        app_queries['appointment__client__full_name__icontains'] = search_text

        invoice_checkout_ids = list(
            SaleInvoice.objects.filter(id__icontains=search_text).values_list('checkout', flat=True))
        sale_checkouts = Checkout.objects.select_related(
            'location',
            'location__currency',
            'client',
            'member'
        ).prefetch_related(
            'checkout_orders',
            'checkout_orders__user',
            'checkout_orders__client',
            'checkout_orders__member',
            'checkout_orders__location',
            'checkout_orders__location__currency',
        ).filter(id__in=invoice_checkout_ids) \
            .distinct()
        appointment_checkouts = AppointmentCheckout.objects.select_related(
            'appointment_service',
            'business_address',
            'appointment',
            'appointment__client',
            'service',
        ).filter(
            id__in=invoice_checkout_ids
        ).distinct()

    checkout_order = Checkout.objects.select_related(
        'location',
        'location__currency',
        'client',
        'member'
    ).prefetch_related(
        'checkout_orders',
        'checkout_orders__user',
        'checkout_orders__client',
        'checkout_orders__member',
        'checkout_orders__location',
        'checkout_orders__location__currency',
    ).filter(
        is_deleted=False,
        location__id=location_id,
        **queries,
        **sale_queries
    ).distinct()

    appointment_checkout = AppointmentCheckout.objects.select_related(
        'appointment_service',
        'business_address',
        'appointment',
        'appointment__client',
        'service',
    ).filter(
        business_address__id=location_id,
        **queries,
        **app_queries
    ).distinct()

    if sale_checkouts:
        checkout_order = checkout_order | sale_checkouts

    if appointment_checkouts:
        appointment_checkout = appointment_checkout | appointment_checkouts

    checkout_data = list(SaleOrders_CheckoutSerializer(checkout_order, many=True, context={'request': request}).data)
    appointment_data = list(
        SaleOrders_AppointmentCheckoutSerializer(appointment_checkout, many=True, context={'request': request}).data)

    data_total = checkout_data + appointment_data
    sorted_data = sorted(data_total, key=lambda x: x['created_at'], reverse=True)

    if recent_five_sales:
        sorted_data = sorted_data[:5]

    # invoicce translation data
    business_address = BusinessAddress.objects.get(id=location_id)
    invoice_translations = BusinessAddressSerilaizer(business_address).data

    paginator = CustomPagination()
    paginator.page_size = 100000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(sorted_data, request)
    response = paginator.get_paginated_response(paginated_data, 'sales', invoice_translations)

    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_sale_orders_optimized(request):
    location_id = request.GET.get('location', None)
    range_start = request.GET.get('range_start', None)
    range_end = request.GET.get('range_end', None)
    no_pagination = request.GET.get('no_pagination', None)
    recent_five_sales = request.GET.get('recent_five_sales', False)
    search_text = request.GET.get('search_text', None)
    client_id = request.GET.get('client', None)
    service_id = request.GET.get('service', None)

    if range_end is not None:
        range_end = dt.strptime(range_end, '%Y-%m-%d').date()
        range_end = range_end + timedelta(days=1)
        range_end = str(range_end)

    query = Q()
    app_queries = Q(business_address__id=location_id, appointment__status=choices.AppointmentStatus.DONE)
    sale_queries = Q(is_deleted=False, location__id=location_id)

    if range_start:
        query &= Q(created_at__range=(range_start, range_end))

    if client_id:
        sale_queries &= Q(client__id=client_id) & query
        app_queries &= Q(appointment__client__id=client_id) & query

    if service_id:
        service_orders = ServiceOrder.objects.filter(
            service__id = service_id
        ).values_list('checkout' , flat=True)

        sale_queries &= Q(id__in=list(service_orders))
        app_queries &= Q(appointment__appointment_services__service__id=service_id)

    if search_text:
        # removing # for better search
        search_text = search_text.replace('#', '')
        invoice_checkout_ids = list(
            SaleInvoice.objects.filter(id__icontains=search_text).values_list('checkout', flat=True))
        sale_queries &= Q(id__in=invoice_checkout_ids) | Q(client__full_name__icontains=search_text)
        app_queries &= Q(id__in=invoice_checkout_ids) | Q(appointment__client__full_name__icontains=search_text)

    checkout_order = Checkout.objects \
        .filter(sale_queries) \
        .select_related('client', 'member') \
        .prefetch_related('checkout_orders') \
        .with_total_tax() \
        .distinct()

    appointment_checkout = AppointmentCheckout.objects \
        .filter(app_queries) \
        .select_related('appointment__client') \
        .prefetch_related('appointment__tips_checkout') \
        .with_subtotal() \
        .with_total_tax() \
        .distinct()

    checkout_data = list(SaleOrders_CheckoutSerializerOP(checkout_order, many=True).data)
    appointment_data = list(SaleOrders_AppointmentCheckoutSerializerOP(appointment_checkout, many=True).data)

    data_total = checkout_data + appointment_data
    sorted_data = sorted(data_total, key=lambda x: x['created_at'], reverse=True)

    if recent_five_sales:
        sorted_data = sorted_data[:5]

    paginator = CustomPagination()
    paginator.page_size = 100000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(sorted_data, request)
    response = paginator.get_paginated_response(paginated_data, 'sales')

    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_sale_orders_default(request):
    paginator = PageNumberPagination()
    paginator.page_size = 5

    checkout_order = Checkout.objects.filter(
        is_deleted=False)
    paginated_checkout_order = paginator.paginate_queryset(checkout_order, request)
    checkout_data = CheckoutSerializer(paginated_checkout_order, many=True, context={'request': request}).data

    appointment_checkout = AppointmentCheckout.objects.filter(appointment_service__appointment_status='Done')
    paginated_appointment_checkout = paginator.paginate_queryset(appointment_checkout, request)
    appointment_checkout_data = AppointmentCheckoutSerializer(paginated_appointment_checkout, many=True,
                                                              context={'request': request}).data

    data = checkout_data + appointment_checkout_data
    sorted_data = sorted(data, key=lambda x: x['created_at'], reverse=True)

    return paginator.get_paginated_response(sorted_data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_orders(request):
    product_order = ProductOrder.objects.filter(is_deleted=False).order_by('-created_at')

    serialized = ProductOrderSerializer(product_order, many=True, context={'request': request, })
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Product Orders',
                'error_message': None,
                'orders': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_membership_orders(request):
    membership_order = MemberShipOrder.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = MemberShipOrderSerializer(membership_order, many=True, context={'request': request, })
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Membership Orders',
                'error_message': None,
                'orders': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_service_orders(request):
    service_orders = ServiceOrder.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = ServiceOrderSerializer(service_orders, many=True, context={'request': request, })
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Service Orders',
                'error_message': None,
                'orders': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_voucher_orders(request):
    voucher_orders = VoucherOrder.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = VoucherOrderSerializer(voucher_orders, many=True, context={'request': request, })
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Voucher Orders',
                'error_message': None,
                'orders': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_total_revenue(request):
    data = {
        'appointments_jan': 0,
        'appointments_feb': 0,
        'appointments_mar': 0,
        'appointments_apr': 0,
        'appointments_may': 0,
        'appointments_jun': 0,
        'appointments_july': 0,
        'appointments_aug': 0,
        'appointments_sep': 0,
        'appointments_oct': 0,
        'appointments_nov': 0,
        'appointments_dec': 0,

        'sale_jan': 0,
        'sale_feb': 0,
        'sale_mar': 0,
        'sale_apr': 0,
        'sale_may': 0,
        'sale_jun': 0,
        'sale_july': 0,
        'sale_aug': 0,
        'sale_sep': 0,
        'sale_oct': 0,
        'sale_nov': 0,
        'sale_dec': 0,
    }
    appointment = AppointmentCheckout.objects.filter(appointment_service__appointment_status='Paid')
    for ind, value in enumerate(appointment):
        create_at = str(value.created_at)

        matching = int(create_at.split(" ")[0].split("-")[1])
        if (matching == 0):
            data['appointments_jan'] += 1
            MONTHS[0]['appointments'] = data['appointments_jan']

        if (matching == 1):
            data['appointments_feb'] += 1
            MONTHS[1]['appointments'] = data['appointments_feb']

        if (matching == 2):
            data['appointments_mar'] += 1
            MONTHS[2]['appointments'] = data['appointments_mar']

        if (matching == 3):
            data['appointments_apr'] += 1
            MONTHS[3]['appointments'] = data['appointments_apr']

        if (matching == 4):
            data['appointments_may'] += 1
            MONTHS[4]['appointments'] = data['appointments_may']

        if (matching == 5):
            data['appointments_jun'] += 1
            MONTHS[5]['appointments'] = data['appointments_jun']
        if (matching == 6):
            data['appointments_july'] += 1
            MONTHS[6]['appointments'] = data['appointments_july']

        if (matching == 7):
            data['appointments_aug'] += 1
            MONTHS[7]['appointments'] = data['appointments_aug']
        if (matching == 8):
            data['appointments_sep'] += 1
            MONTHS[8]['appointments'] = data['appointments_sep']
        if (matching == 9):
            data['appointments_oct'] += 1
            MONTHS[9]['appointments'] = data['appointments_oct']
        if (matching == 10):
            data['appointments_nov'] += 1
            MONTHS[10]['appointments'] = data['appointments_nov']
        if (matching == 11):
            data['appointments_dec'] += 1
            MONTHS[11]['appointments'] = data['appointments_dec']

    orders = Order.objects.filter(is_deleted=False)
    for order in orders:
        create_at = str(order.created_at)

        matching = int(create_at.split(" ")[0].split("-")[1])
        if (matching == 0):
            data['sale_jan'] += 1
            MONTHS[0]['sales'] = data['sale_jan']

        if (matching == 1):
            data['sale_feb'] += 1
            MONTHS[1]['sales'] = data['sale_feb']

        if (matching == 2):
            data['sale_mar'] += 1
            MONTHS[2]['sales'] = data['sale_mar']

        if (matching == 3):
            data['sale_apr'] += 1
            MONTHS[3]['sales'] = data['sale_apr']

        if (matching == 4):
            data['sale_may'] += 1
            MONTHS[4]['sales'] = data['sale_may']

        if (matching == 5):
            data['sale_jun'] += 1
            MONTHS[5]['sales'] = data['sale_jun']
        if (matching == 6):
            data['sale_july'] += 1
            MONTHS[6]['sales'] = data['sale_july']

        if (matching == 7):
            data['sale_aug'] += 1
            MONTHS[7]['sales'] = data['sale_aug']
        if (matching == 8):
            data['sale_sep'] += 1
            MONTHS[8]['sales'] = data['sale_sep']
        if (matching == 9):
            data['sale_oct'] += 1
            MONTHS[9]['sales'] = data['sale_oct']
        if (matching == 10):
            data['sale_nov'] += 1
            MONTHS[10]['sales'] = data['sale_nov']
        if (matching == 11):
            data['sale_dec'] += 1
            MONTHS[11]['sales'] = data['sale_dec']

    total = 0
    appointmemnt_sale = 0
    order_sale = 0
    orders_price = Order.objects.filter(is_deleted=False)
    for order in orders_price:
        order_sale += 1
        if order.total_price is not None:
            total += float(order.total_price)

    appointment_checkouts = AppointmentCheckout.objects.filter(
        Q(appointment_service__appointment_status='Paid') |
        Q(appointment_service__appointment_status='Done')
    ).distinct()

    for checkout_instance in appointment_checkouts:
        appointmemnt_sale += 1
        if checkout_instance.total_price is not None:
            total += float(checkout_instance.total_price)

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'Total Revenue',
                'error_message': None,
                'revenue': total,
                'sale': order_sale,
                'appointment_sale': appointmemnt_sale,
                'dashboard': MONTHS
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_location_tax(request):
    location_id = request.GET.get('location_id', None)
    if location_id is None:
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
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        location = BusinessAddress.objects.get(id=location_id, is_deleted=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': 'OBJECT_NOT_FOUND',
                'response': {
                    'message': 'Business Location Not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    serialized = BusinessAddressSerializer(location, context={'request': request, })

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'All Business Tax!',
                'error_message': None,
                'tax': serialized.data
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sale_checkout(request):
    checkout = Checkout.objects.all()
    serialized = CheckoutSerializer(checkout, many=True, context={'request': request, })

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Product Order Sale Created!',
                'error_message': None,
                'sale': serialized.data
            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_sale_order(request):
    user = request.user

    sale_type = request.data.get('selection_type', None)
    client_id = request.data.get('client', None)
    sale_status = request.data.get('status', None)
    member_id = request.data.get('employee_id', None)
    location_id = request.data.get('location', None)
    payment_type = request.data.get('payment_type', None)
    client_type = request.data.get('client_type', None)
    ids = request.data.get('ids', None)

    free_services_quantity = request.data.get('free_services_quantity', None)

    service_total_price = request.data.get('service_total_price', None)
    product_total_price = request.data.get('product_total_price', None)
    voucher_total_price = request.data.get('voucher_total_price', None)

    service_commission = request.data.get('service_commission', None)
    product_commission = request.data.get('product_commission', None)
    voucher_commission = request.data.get('voucher_commission', None)

    service_commission_type = request.data.get('service_commission_type', '')
    product_commission_type = request.data.get('product_commission_type', '')
    voucher_commission_type = request.data.get('voucher_commission_type', '')

    is_promotion_availed = request.data.get('is_promotion_availed', None)
    is_promotion = request.data.get('is_promotion', False)

    tip = request.data.get('tip', 0)
    total_price = request.data.get('total_price', None)
    minus_price = 0

    errors = []

    if not all([client_type, location_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        #   'member', 
                        'selection_type',
                        'location'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        client = Client.objects.get(id=client_id)
    except Exception as err:
        client = None

    try:
        member = Employee.objects.get(id=member_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
                'response': {
                    'message': 'Member not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business_address = BusinessAddress.objects.get(id=location_id)
    except Exception as err:
        print(err)
        pass

    if type(ids) == str:
        ids = json.loads(ids)

    elif type(ids) == list:
        pass

    checkout = Checkout.objects.create(
        user=user,

        client=client,
        location=business_address,
        member=member,
        client_type=client_type,
        payment_type=payment_type,

        total_voucher_price=voucher_total_price,
        total_service_price=service_total_price,
        total_product_price=product_total_price,

        service_commission_type=service_commission_type,
        product_commission_type=product_commission_type,
        voucher_commission_type=voucher_commission_type,
    )

    invoice = SaleInvoice.objects.create(
        user=user,

        client=client,
        location=business_address,
        member=member,
        client_type=client_type,
        payment_type=payment_type,

        total_voucher_price=voucher_total_price,
        total_service_price=service_total_price,
        total_product_price=product_total_price,

        service_commission_type=service_commission_type,
        product_commission_type=product_commission_type,
        voucher_commission_type=voucher_commission_type,
        checkout=f'{checkout.id}',
    )
    invoice.save()

    if bool(is_promotion) == True:
        checkout.is_promotion = True
        checkout.save()
        invoice.is_promotion = True
        invoice.save()

    test = True

    if bool(is_promotion_availed) == True:
        for item in ids:
            price = item["price"]
            minus_price += (price)

    for id in ids:

        sale_type = id['selection_type']
        service_id = id['id']
        quantity = id['quantity']
        price = id['price']
        member_id = id['employee_id']
        discount_price = id.get('discount_price', None)

        if discount_price is not None:
            price = int(discount_price)

        if price == 0 and bool(is_promotion_availed) == True:
            number = int(float(total_price))
            rem_price = number - minus_price
            price = int(rem_price) / int(free_services_quantity)

            if test == True:
                checkout.total_service_price = int(float(total_price))
                checkout.save()
                invoice.total_service_price = int(float(total_price))
                invoice.save()
                test = False

    if type(tip) == str:
        tip = json.loads(tip)

    elif type(tip) == list:
        pass

        for t in tip:
            member_id = t.get('employee', None)
            checkout_tip = t.get('tip', None)
            try:
                member_tips_id = Employee.objects.get(id=member_id)

                create_tip = AppointmentEmployeeTip.objects.create(
                    member=member_tips_id,
                    tip=checkout_tip,
                    business_address=business_address,

                )
            except Exception as err:
                pass

        if sale_type == 'PRODUCT':
            try:
                product = Product.objects.get(id=service_id)
            except Exception as err:
                return Response(
                    {
                        'status': False,
                        'status_code': StatusCodes.PRODUCT_NOT_FOUND_4037,
                        'response': {
                            'message': 'Something Went Wrong',
                            'error_message': str(err),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                transfer = ProductStock.objects.get(product__id=product.id, location=business_address.id)

                if transfer.available_quantity >= int(quantity):
                    stock_transfer = ProductOrderStockReport.objects.create(
                        report_choice='Sold',
                        product=product,
                        user=request.user,
                        location=business_address,
                        before_quantity=transfer.available_quantity
                    )
                    sold = transfer.available_quantity - int(quantity)
                    transfer.available_quantity = sold
                    transfer.sold_quantity += int(quantity)
                    transfer.save()

                    stock_transfer.after_quantity = sold
                    stock_transfer.save()

                else:
                    errors.append('Available quantity issue')

            except Exception as err:
                errors.append(str(err))
            try:
                admin_email = StockNotificationSetting.objects.get(business=str(business_address.business))
                if admin_email.notify_stock_turnover == True and transfer.available_quantity <= 5:
                    try:
                        thrd = Thread(target=ProductTurnover, args=[],
                                      kwargs={'product': product, 'product_stock': transfer,
                                              'business_address': business_address.id, 'tenant': request.tenant})
                        thrd.start()
                    except Exception as err:
                        ExceptionRecord.objects.create(
                            text=f' error in Turnover email sale{str(err)}'
                        )
            except:
                pass

            try:
                admin_email = StockNotificationSetting.objects.get(business=str(business_address.business))
                if admin_email.notify_for_lowest_stock == True and transfer.available_quantity <= 5:
                    try:
                        thrd = Thread(target=stock_lowest, args=[],
                                      kwargs={'product': product, 'product_stock': transfer,
                                              'business_address': business_address.id, 'tenant': request.tenant,
                                              'quantity': transfer.available_quantity})
                        thrd.start()
                    except Exception as err:
                        ExceptionRecord.objects.create(
                            text=f' error in Stock lowest email sale{str(err)}'
                        )
            except:
                pass

            product_order = ProductOrder.objects.create(
                user=user,
                client=client,
                product=product,
                checkout=checkout,
                member=member,
                location=business_address,
                total_price=total_price,
                payment_type=payment_type,
                client_type=client_type,
                quantity=quantity,
                current_price=price,
                price=price,
            )
            product_order.sold_quantity += 1  # product_stock.sold_quantity
            product_order.save()
            checkout.product_commission = product_commission
            checkout.save()
            invoice.product_commission = product_commission
            invoice.save()

        elif sale_type == 'SERVICE':
            try:
                service = Service.objects.get(id=service_id)
                service_price = PriceService.objects.filter(service=service_id).order_by('-created_at').first()
                dur = service_price.duration

                service_order = ServiceOrder.objects.create(
                    user=user,
                    service=service,
                    duration=dur,
                    checkout=checkout,
                    client=client,
                    member=member,
                    location=business_address,
                    total_price=total_price,
                    payment_type=payment_type,
                    client_type=client_type,
                    quantity=quantity,
                    current_price=price,
                    price=price,

                )
                checkout.service_commission = service_commission
                checkout.save()
                invoice.service_commission = service_commission
                invoice.save()
            except Exception as err:
                return Response(
                    {
                        'status': False,
                        'status_code': StatusCodes.SERVICE_NOT_FOUND_4035,
                        'response': {
                            'message': 'Service not found',
                            'error_message': str(err),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif sale_type == 'MEMBERSHIP':
            try:
                membership = Membership.objects.get(id=service_id)
                validity = int(membership.valid_for.split(" ")[0])
                end_date_cal = membership.created_at + timedelta(days=validity)
                start_date_cal = membership.created_at

                membership_order = MemberShipOrder.objects.create(
                    user=user,

                    membership=membership,
                    start_date=start_date_cal,
                    end_date=end_date_cal,
                    checkout=checkout,
                    client=client,
                    member=member,
                    total_price=total_price,
                    payment_type=payment_type,
                    client_type=client_type,
                    quantity=quantity,
                    location=business_address,
                    current_price=price,
                    price=price,
                )
            except Exception as err:
                return Response(
                    {
                        'status': False,
                        'status_code': StatusCodes.INVALID_MEMBERSHIP_ID_4040,
                        'response': {
                            'message': 'Membership not found',
                            'error_message': str(err),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif sale_type == 'VOUCHER':

            try:
                days = 0
                voucher = Vouchers.objects.get(id=service_id)
                test = voucher.validity.split(" ")[1]

                if test == 'Days':
                    day = voucher.validity.split(" ")[0]
                    day = int(day)
                    days = day

                elif test == 'Months':
                    day = voucher.validity.split(" ")[0]
                    data = int(day)
                    days = data * 30


                elif test == 'Years':
                    day = voucher.validity.split(" ")[0]
                    day = int(day)
                    days = day * 360
                print(days)
                end_date_cal = voucher.created_at + timedelta(days=days)
                start_date_cal = voucher.created_at

                voucher_order = VoucherOrder.objects.create(
                    user=user,

                    voucher=voucher,
                    start_date=start_date_cal,
                    end_date=end_date_cal,
                    checkout=checkout,
                    client=client,
                    member=member,
                    total_price=total_price,
                    payment_type=payment_type,
                    client_type=client_type,
                    quantity=quantity,
                    location=business_address,
                    current_price=price,
                    price=price,

                )
                checkout.voucher_commission = voucher_commission
                checkout.save()
                invoice.voucher_commission = voucher_commission
                invoice.save()
            except Exception as err:
                return Response(
                    {
                        'status': False,
                        'status_code': StatusCodes.INVALID_VOUCHER_ID_4041,
                        'response': {
                            'message': 'Voucher not found',
                            'error_message': str(err),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

    try:
        thrd = Thread(target=StaffSaleEmail, args=[],
                      kwargs={'ids': ids, 'location': business_address.address_name, 'tenant': request.tenant,
                              'member': member, 'invoice': checkout.id, 'client': client})
        thrd.start()
    except Exception as err:
        ExceptionRecord.objects.create(
            text=f' error in email sale{str(err)}'
        )
    invoice.save()  # Do not remove this
    serialized = CheckoutSerializer(checkout, context={'request': request, })

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Product Order Sale Created!',
                'error_message': errors,
                'sale': serialized.data,
            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])

def new_create_sale_order(request):
    user = request.user
    
    sale_type = request.data.get('selection_type', None)
    client_id = request.data.get('client', None)
    tax_amount = request.data.get('tax_amount', 0)
    tax_amount1 = request.data.get('tax_amount1', 0)
    tax_applied = request.data.get('tax_applied', 0)
    tax_applied1 = request.data.get('tax_applied1', 0)
    tax_name = request.data.get('tax_name', '')
    tax_name1 = request.data.get('tax_name1', '')
    location_id = request.data.get('location', None)
    payment_type = request.data.get('payment_type', None)
    client_type = request.data.get('client_type', None)
    ids = request.data.get('ids', None)
    is_voucher_redeemed_global = request.data.get('is_voucher_redeemed', None)
    redeemed_membership_id = request.data.get('redeemed_membership_id', False)
    redeemed_voucher_id = request.data.get('redeemed_voucher_id', None)
    free_services_quantity = request.data.get('free_services_quantity', None)
    service_total_price = request.data.get('service_total_price', None)
    product_total_price = request.data.get('product_total_price', None)
    voucher_total_price = request.data.get('voucher_total_price', None)
    voucher_redeem_percentage = request.data.get('voucher_redeem_percentage', None)
    redeem_option = request.data.get('redeem_option', None)
    service_commission_type = request.data.get('service_commission_type', '')
    product_commission_type = request.data.get('product_commission_type', '')
    voucher_commission_type = request.data.get('voucher_commission_type', '')
    is_promotion_availed = request.data.get('is_promotion_availed', None)
    is_loyalty_points_redeemed = request.data.get('is_redeemed', None)
    loyalty_points_redeemed_id = request.data.get('redeemed_id', None)
    loyalty_points_redeemed = request.data.get('redeemed_points', None)
    total_discount_value = request.data.get('discount_value', None)
    coupon_discounted_price = request.data.get('coupon_discounted_price', None)
    redeemed_coupon_id = request.data.get('redeemed_coupon_id',None)
    tip = request.data.get('tip', [])
    total_price = request.data.get('total_price', None)
    is_coupon_redeemed = request.data.get('is_coupon_redeemed', None)
    minus_price = 0

    errors = []

    # using this flag to email membership sale only if its membership sale
    # same for rest of other three sales email
    is_membership_sale = False



    if not all([client_type, location_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'selection_type',
                        'location'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        client = Client.objects.get(id=client_id)
    except Exception as err:
        client = None

    try:
        business_address = BusinessAddress.objects.get(id=location_id)
    except Exception as err:
        print(err)
        pass

    if type(ids) == str:
        ids = json.loads(ids)

    elif type(ids) == list:
        pass

    checkout = Checkout.objects.create(
        user=user,

        client=client,
        location=business_address,
        client_type=client_type,
        payment_type=payment_type,

        voucher_redeem_percentage=voucher_redeem_percentage,
        redeem_option=redeem_option,

        total_voucher_price=voucher_total_price,
        total_service_price=service_total_price,
        total_product_price=product_total_price,

        service_commission_type=service_commission_type,
        product_commission_type=product_commission_type,
        voucher_commission_type=voucher_commission_type,
        tax_amount=tax_amount,
        tax_amount1=tax_amount1,
        tax_applied=tax_applied,
        tax_applied1=tax_applied1,
        tax_name=tax_name,
        tax_name1=tax_name1,
        total_discount=total_discount_value,
        coupon_discounted_price=coupon_discounted_price,
        coupon_id = redeemed_coupon_id,
        is_coupon_redeemed=is_coupon_redeemed
    )

    checkout.save()
    if redeemed_coupon_id:
        coupon = Coupon.objects.get(id=redeemed_coupon_id)
        coupon.usage_limit -= 1
        coupon.user_limit -= 1
        coupon.save()
    '''
    Invoice is being created here for QuickSale
    '''
    invoice = SaleInvoice.objects.create(
        user=user,
        client=client,
        location=business_address,
        client_type=client_type,
        payment_type=payment_type,
        
        # Added new fields
        invoice_type = 'order',
        checkout_type = 'sale',

        total_voucher_price=voucher_total_price,
        total_service_price=service_total_price,
        total_product_price=product_total_price,

        service_commission_type=service_commission_type,
        product_commission_type=product_commission_type,
        voucher_commission_type=voucher_commission_type,
        checkout=f'{checkout.id}',
    )
    invoice.save()

    test = True

    if is_promotion_availed:
        checkout.is_promotion = True
        checkout.selected_promotion_id = request.data.get('selected_promotion_id', '')
        checkout.selected_promotion_type = request.data.get('selected_promotion_type', '')
        checkout.save()

        for item in ids:
            price = item["price"]
            minus_price += float(price)

    for id in ids:

        sale_type = id['selection_type']
        service_id = id['id']
        quantity = id['quantity']
        price = id['price']
        employee_id = id['employee_id']
        discount_price = id.get('discount_price', None)
        discount_percentage = id.get('discount_percentage', None)
        is_membership_redeemed = id.get('is_membership_redeemed', None)
        is_voucher_redeemed = id.get('is_voucher_redeemed', None)
        is_coupon_redeemed = id.get('is_coupon_redeemed', None)
        redeemed_price = id.get('redeemed_price', None)
        redeemed_coupon_id = id.get('redeemed_coupon_id', None)

        if redeemed_coupon_id:
            coupon = Coupon.objects.get(id=redeemed_coupon_id)
            coupon.usage_limit -= 1
            coupon.user_limit -= 1
            coupon.save()
        if redeemed_price is None:
            redeemed_price = 0

        is_redeemed = is_membership_redeemed or is_voucher_redeemed or is_coupon_redeemed

        item_name = ''
        item_id = service_id
        try:
            employee_id = Employee.objects.get(id=employee_id)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
                    'response': {
                        'message': 'Employee not found',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if price == 0 and free_services_quantity and bool(is_promotion_availed) == True:
            number = float(total_price)
            rem_price = number - float(minus_price)
            price = float(rem_price) / float(free_services_quantity)

            if test == True:
                checkout.total_service_price = float(total_price)
                checkout.save()
                invoice.total_service_price = float(total_price)
                invoice.save()
                test = False

        original_price = float(price)
        order_discount_price = None

        if discount_price is not None:
            order_discount_price = float(discount_price)
            discount_percentage = float(discount_percentage) if discount_percentage else None

        order_instance = None
        if sale_type == 'PRODUCT':
            try:
                product = Product.objects.get(id=service_id)
            except Exception as err:
                return Response(
                    {
                        'status': False,
                        'status_code': StatusCodes.PRODUCT_NOT_FOUND_4037,
                        'response': {
                            'message': 'Something Went Wrong',
                            'error_message': str(err),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                item_name = product.name

            try:
                product_stock = ProductStock.objects.get(product__id=product.id, location=business_address.id)

                if product_stock.available_quantity >= int(quantity):
                    stock_transfer = ProductOrderStockReport.objects.create(
                        report_choice='Sold',
                        product=product,
                        user=request.user,
                        location=business_address,
                        before_quantity=product_stock.available_quantity
                    )
                    sold = product_stock.available_quantity - int(quantity)
                    product_stock.available_quantity = sold
                    product_stock.sold_quantity += int(quantity)
                    product_stock.save()

                    stock_transfer.after_quantity = sold
                    stock_transfer.save()

                else:
                    errors.append('Available quantity issue')

            except Exception as err:
                errors.append(str(err))
            try:
                admin_email = StockNotificationSetting.objects.get(business=str(business_address.business))
                if admin_email.notify_stock_turnover == True and product_stock.available_quantity <= 5:
                    try:
                        thrd = Thread(target=ProductTurnover, args=[],
                                      kwargs={'product': product, 'product_stock': product_stock,
                                              'business_address': business_address.id, 'tenant': request.tenant})
                        thrd.start()
                    except Exception as err:
                        ExceptionRecord.objects.create(
                            text=f' error in Turnover email sale{str(err)}'
                        )
            except:
                pass

            try:
                admin_email = StockNotificationSetting.objects.get(business=str(business_address.business))
                if admin_email.notify_for_lowest_stock == True and product_stock.available_quantity <= 5:
                    try:
                        thrd = Thread(target=stock_lowest, args=[],
                                      kwargs={'product': product, 'product_stock': product_stock,
                                              'business_address': business_address.id, 'tenant': request.tenant,
                                              'quantity': product_stock.available_quantity})
                        thrd.start()
                    except Exception as err:
                        ExceptionRecord.objects.create(
                            text=f' error in Stock lowest email sale{str(err)}'
                        )
            except:
                pass

            product_order = ProductOrder.objects.create(
                user=user,
                member=employee_id,
                client=client,
                product=product,
                checkout=checkout,
                location=business_address,
                total_price=float(original_price),
                payment_type=payment_type,
                client_type=client_type,
                quantity=quantity,
                current_price=float(price),
                discount_percentage=discount_percentage,
                discount_price=order_discount_price,
            )
            product_order.sold_quantity += 1  # product_stock.sold_quantity
            product_order.save()
            order_instance = product_order

        elif sale_type == 'SERVICE':
            try:
                service = Service.objects.get(id=service_id)
                item_name = service.name
                service_price = PriceService.objects.filter(
                    service=service_id,
                    currency=business_address.currency
                ).order_by('-created_at')
                if len(service_price) > 0:
                    service_price = service_price[0]
                else:
                    service_price = PriceService.objects.filter(service=service_id).order_by('-created_at').first()
                dur = service_price.duration

                service_order = ServiceOrder.objects.create(
                    user=user,
                    member=employee_id,
                    service=service,
                    duration=dur,
                    checkout=checkout,
                    client=client,
                    location=business_address,
                    total_price=float(original_price),
                    payment_type=payment_type,
                    client_type=client_type,
                    quantity=quantity,
                    current_price=float(price),
                    discount_percentage=discount_percentage,
                    discount_price=order_discount_price,
                )

                order_instance = service_order



            except Exception as err:
                return Response(
                    {
                        'status': False,
                        'status_code': StatusCodes.SERVICE_NOT_FOUND_4035,
                        'response': {
                            'message': 'Service not found',
                            'error_message': str(err),
                        }
                    }, status=status.HTTP_400_BAD_REQUEST
                )

        elif sale_type == 'MEMBERSHIP':
            try:
                membership = Membership.objects.get(id=service_id)
                validity = int(membership.valid_for.split(" ")[0])
                end_date_cal = membership.created_at + timedelta(days=validity)
                start_date_cal = membership.created_at

                membership_order = MemberShipOrder.objects.create(
                    user=user,
                    member=employee_id,
                    membership=membership,
                    start_date=start_date_cal,
                    end_date=end_date_cal,
                    checkout=checkout,
                    client=client,
                    total_price=float(original_price),
                    payment_type=payment_type,
                    client_type=client_type,
                    quantity=quantity,
                    location=business_address,
                    current_price=float(price),
                    discount_percentage=discount_percentage,
                    discount_price=order_discount_price,
                )
            except Exception as err:
                ExceptionRecord.objects.create(
                    text=f' error in member price{str(err)}'
                )
                return Response(
                    {
                        'status': False,
                        'status_code': StatusCodes.INVALID_MEMBERSHIP_ID_4040,
                        'response': {
                            'message': 'Membership not found',
                            'error_message': str(err),
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                order_instance = membership_order
            is_membership_sale = True

        elif sale_type == 'VOUCHER':

            try:
                days = 0
                voucher = Vouchers.objects.get(id=service_id)
                item_name = voucher.name
                test = voucher.validity.split(" ")[1]

                # TODO: remove this Min Condition
                if test == 'Min':
                    minutes = voucher.validity.split(" ")[0]
                    minute = int(minutes)
                    days = minute

                if test == 'Days':
                    day = voucher.validity.split(" ")[0]
                    day = int(day)
                    days = day

                elif test == 'Months':
                    day = voucher.validity.split(" ")[0]
                    data = int(day)
                    days = data * 30


                elif test == 'Years':
                    day = voucher.validity.split(" ")[0]
                    day = int(day)
                    days = day * 360

                start_date_cal = datetime.datetime.now()
                end_date_cal = datetime.datetime.now() + timedelta(days=days)

                discount_percentage = voucher.discount_percentage

                voucher_order = VoucherOrder.objects.create(
                    user=user,
                    member=employee_id,
                    voucher=voucher,
                    start_date=start_date_cal,
                    end_date=end_date_cal,
                    checkout=checkout,
                    client=client,
                    discount_percentage=float(discount_percentage),
                    total_price=float(original_price),
                    payment_type=payment_type,
                    client_type=client_type,
                    quantity=quantity,
                    location=business_address,
                    current_price=float(price),
                    discount_price=order_discount_price,

                )



            except Exception as err:
                ExceptionRecord.objects.create(
                    text=f' error in voucher price{str(err)}'
                )
                return Response(
                    {
                        'status': False,
                        'status_code': StatusCodes.INVALID_VOUCHER_ID_4041,
                        'response': {
                            'message': 'Voucher not found',
                            'error_message': str(err),
                        }
                    }, status=status.HTTP_400_BAD_REQUEST
                )
            else:
                order_instance = voucher_order

        if order_instance is not None and is_redeemed:
            order_instance.is_redeemed = True

            order_instance.redeemed_type = 'Membership' if is_membership_redeemed else 'Voucher' if is_voucher_redeemed else 'Coupon'
            order_instance.redeemed_price = float(redeemed_price)
            order_instance.redeemed_instance_id = redeemed_membership_id
            order_instance.total_discount = float(total_discount_value) if total_discount_value else None
            order_instance.save()

        if sale_type in ['PRODUCT', 'SERVICE', 'VOUCHER']:

            CommissionType = {
                'PRODUCT': 'Retail',
                'SERVICE': 'Service',
                'VOUCHER': 'Voucher',
            }
            commission_category = CommissionType[sale_type]

            sale_price = 0
            if order_discount_price:
                sale_price = float(order_discount_price)
            else:
                sale_price = float(price)

            total_from_value = float(sale_price) * float(quantity)

            sale_commissions = CategoryCommission.objects.filter(
                commission__employee=employee_id,
                from_value__lte=float(total_from_value),
                category_comission__iexact=commission_category
            ).order_by('-from_value')

            if len(sale_commissions) > 0:
                commission = sale_commissions[0]

                calculated_commission = commission.calculated_commission(total_from_value)
                employee_commission = EmployeeCommission.objects.create(
                    user=request.user,
                    business=business_address.business,
                    location=business_address,
                    employee=employee_id,
                    commission=commission.commission,
                    category_commission=commission,
                    commission_category=commission_category,
                    commission_type=commission.comission_choice,
                    sale_value=float(order_discount_price) if order_discount_price else float(price),
                    commission_rate=float(commission.commission_percentage),
                    commission_amount=float(calculated_commission),
                    symbol=commission.symbol,
                    item_name=item_name,
                    item_id=item_id,
                    quantity=quantity,
                    tip=0
                )
                employee_commission.sale_id = checkout.id
                employee_commission.save()

    if type(tip) == str:
        tip = json.loads(tip)
    if type(tip) == list:

        for t in tip:
            employee_id = t.get('employee', None)
            checkout_tip = t.get('tip', None)

            try:
                employee_tips_id = Employee.objects.get(id=employee_id)
            except Exception as err:
                print(f"Error: Employee with ID {employee_id} does not exist")
                errors.append(str(err))
            else:
                AppointmentEmployeeTip.objects.create(
                    checkout=checkout,
                    member=employee_tips_id,
                    tip=float(checkout_tip),
                    business_address=business_address,
                )
# ======================================================= Loyalty point calculations ===========================
    if checkout.client:
        these_orders = Order.objects.filter(
            checkout=checkout
        )
        # .values_list('total_price', flat=True)

        # these_orders = list(these_orders)
        total_price = 0
        for sale_order in these_orders:
            sale_order_price = 0
            if sale_order.discount_price:
                sale_order_price = sale_order.discount_price
            else:
                sale_order_price = sale_order.total_price

            total_price += float(sale_order_price * sale_order.quantity) # total Price  of the orders 

        logs_points_redeemed = 0
        logs_total_redeened_value = 0
        
        # ========================================= Updating the loyalty point ===================================
        
        if all([is_loyalty_points_redeemed, loyalty_points_redeemed_id, loyalty_points_redeemed]):
            try:
                client_points = ClientLoyaltyPoint.objects.get(id=loyalty_points_redeemed_id)
            except Exception as err:
                ExceptionRecord.objects.create(text=f'LOYALTY : {err}')
                pass
            else:
                # updating the already present loyalty_points for the client
                client_points.points_redeemed = float(client_points.points_redeemed) + float(loyalty_points_redeemed)
                client_points.save()

                single_point_value = client_points.customer_will_get_amount / client_points.for_every_points
                total_redeened_value = float(single_point_value) * float(loyalty_points_redeemed)

                logs_points_redeemed = loyalty_points_redeemed
                logs_total_redeened_value = total_redeened_value

        allowed_points = LoyaltyPoints.objects.filter(
            Q(loyaltytype='Service') |
            Q(loyaltytype='Both'),
            location=business_address,
            # amount_spend = total_price,
            is_active=True,
            is_deleted=False
        )
        if len(allowed_points) > 0:
            point = allowed_points[0]
            client_points, created = ClientLoyaltyPoint.objects.get_or_create(
                location=business_address,
                client=checkout.client,
                loyalty_points=point, # loyalty Foreignkey
            )

            loyalty_spend_amount = point.amount_spend
            loyalty_earned_points = point.number_points  # total earned points if user spend amount point.amount_spend

            # gained points based on customer's total Checkout Bill

            earned_points = (float(total_price) / float(loyalty_spend_amount)) * float(loyalty_earned_points)
            earned_amount = (earned_points / point.earn_points) * float(point.total_earn_from_points)

            if created:
                client_points.total_earn = earned_points
                client_points.total_amount = earned_amount

            else:
                client_points.total_earn = float(client_points.total_earn) + float(earned_points)
                client_points.total_amount = client_points.total_amount + float(earned_amount)

            client_points.for_every_points = point.earn_points
            client_points.customer_will_get_amount = point.total_earn_from_points

            client_points.save()

            LoyaltyPointLogs.objects.create(
                location=business_address,
                client=client_points.client,
                client_points=client_points,
                loyalty=point,
                points_earned=earned_points,
                points_redeemed=logs_points_redeemed,
                balance=client_points.total_available_points,
                actual_sale_value_redeemed=logs_total_redeened_value,
                invoice=invoice,
                checkout=checkout
            )
    if checkout.is_promotion:
        disc_sale = DiscountPromotionSalesReport(
            checkout_id=checkout.id,
            checkout_type='Sale',
            invoice=invoice,
            promotion_id=checkout.selected_promotion_id,
            promotion_type=checkout.selected_promotion_type,
            user=checkout.user,
            client=checkout.client,
            location=checkout.location,
        )
        disc_sale.save()

    invoice.save()  # Do not remove this
    serialized = CheckoutSerializer(checkout, context={'request': request, })

    if client:
        """
        Sending order details to client through 
        """
        if is_membership_sale:
            send_membership_order_email(membership_order, business_address, request)
        else:
            send_order_email(checkout, request)

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Product Order Sale Created!',
                'error_message': errors,
                'sale': serialized.data,
                'total_price':total_price,
                'coupon_discounted_price':coupon_discounted_price
            }
        },
        status=status.HTTP_201_CREATED
    )
