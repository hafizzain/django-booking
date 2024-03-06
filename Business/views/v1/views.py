from datetime import datetime, time, timedelta
from rest_framework import viewsets
import email
import csv
from typing import Any
from django.conf import settings
from operator import ge
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import (ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveAPIView)
from Appointment.Constants.durationchoice import DURATION_CHOICES
from Authentication.serializers import UserTenantLoginSerializer

from Business.models import BusinessAddressMedia, BusinessType, BusinessPrivacy, BusinessPolicy
from Business.serializers.v1_serializers import (BusinessAddress_CustomerSerializer,
                                                 EmployeAppointmentServiceSerializer,
                                                 EmployeTenatSerializer, OpeningHoursSerializer,
                                                 AdminNotificationSettingSerializer,
                                                 BookingSettingSerializer, BusinessTypeSerializer,
                                                 Business_GetSerializer, Business_PutSerializer,
                                                 BusinessAddress_GetSerializer, BusinessThemeSerializer,
                                                 BusinessVendorSerializer,
                                                 ClientNotificationSettingSerializer,
                                                 StaffNotificationSettingSerializer, StockNotificationSettingSerializer,
                                                 BusinessTaxSerializer, PaymentMethodSerializer,
                                                 BusinessTaxSettingSerializer, BusinessPrivacySerializer,
                                                 BusinessPolicySerializer, BusinessVendorSerializerDropdown)
from Client.models import Client
from Employee.models import EmployeDailySchedule, Employee, EmployeeProfessionalInfo, EmployeeSelectedService
from Employee.Constants.Add_Employe import add_employee
from Client.Constants.Add_Employe import add_client

from NStyle.Constants import StatusCodes

from Appointment.models import AppointmentService
from Appointment.serializers import PriceServiceSaleSerializer
from Authentication.models import User, AccountType
from Business.models import Business, BusinessSocial, BusinessAddress, BusinessOpeningHour, BusinessTheme, \
    StaffNotificationSetting, ClientNotificationSetting, AdminNotificationSetting, StockNotificationSetting, \
    BookingSetting, BusinessPaymentMethod, BusinessTax, BusinessVendor, BusinessTaxSetting
from Product.models import Product, ProductStock
from Profile.models import UserLanguage
from Profile.serializers import UserLanguageSerializer
from Service.models import Service, ServiceGroup, PriceService
from Tenants.models import Domain, Tenant
from Utility.models import Country, Currency, ExceptionRecord, Language, NstyleFile, Software, State, City
from Utility.serializers import LanguageSerializer
import json
from django.db.models import Q, F
from threading import Thread
from django_tenants.utils import tenant_context
from Sale.Constants.Custom_pag import CustomPagination
from Sale.serializers import AppointmentCheckoutSerializer, BusinessAddressSerializer, CheckoutSerializer, \
    EmployeeBusinessSerializer, MemberShipOrderSerializer, ProductOrderSerializer, ServiceGroupSerializer, \
    ServiceOrderSerializer, ServiceSerializer, VoucherOrderSerializer
from Utility.Constants.get_from_public_schema import get_country_from_public, get_state_from_public
from MultiLanguage.models import InvoiceTranslation
from django.db import transaction


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_default_data(request):
    business_id = request.GET.get('business_id', None)

    if not all([business_id]):
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
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    admin_user = User.objects.filter(is_admin=True, is_active=True, is_staff=True, is_superuser=True)
    data = {
        'service': [],
        'admin_email': admin_user[0].email,
        'admin_phone_number': admin_user[0].mobile_number,
    }

    locations = BusinessAddress.objects.filter(
        is_default=True
    )

    if len(locations) > 0:
        location_instance = locations[0]
        data['location'] = {
            'name': f'{location_instance.address_name}',
            'id': f'{location_instance.id}',
            'business_address': f'{location_instance.address}',
            'email': f'{location_instance.email}',
            'type': 'location',
        }

    services = Service.objects.filter(
        is_default=True
    )

    service_group = ServiceGroup.objects.filter(is_deleted=False)
    if len(service_group) > 0:
        data['service_group'] = {
            'id': service_group[0].id,
            'name': service_group[0].name
        }

    for service_instance in services:
        data['service'].append({
            'id': f'{service_instance.id}',
            'name': f'{service_instance.name}',
            'description': f'{service_instance.description}',
            'type': 'service',
            'priceservice': PriceServiceSaleSerializer(PriceService.objects.filter(service=service_instance),
                                                       many=True).data,
        })

    clients = Client.objects.filter(
        is_default=True
    )

    if len(clients) > 0:
        client_instance = clients[0]
        data['client'] = {
            'id': f'{client_instance.id}',
            'name': '',
            'email': '',
            'phone_number': '',
            'type': 'client'
        }

    employees = Employee.objects.filter(
        is_default=True
    )

    if len(employees) > 0:
        employee_instance = employees[0]
        try:
            info = EmployeeProfessionalInfo.objects.get(employee=employee_instance)
        except:
            info = None

        emp_services = EmployeeSelectedService.objects.filter(employee=employee_instance)

        data['employee'] = {
            'id': f'{employee_instance.id}',
            'name': '',
            'type': 'employee',
            'email': '',
            'address': f'{employee_instance.address}',
            'designation': f'{info.designation}' if info else '',
            'income_type': f'{info.income_type}' if info else '',
            'salary': f'{info.salary}' if info else '',
            'assigned_services': [
                {'id': serv.service.id, 'name': serv.service.name} for serv in emp_services
            ],
        }

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Business default Data',
                'data': data
            }
        }
    )


{
    "service": {
        "id": "02bb064a-f78d-4f84-9bcd-8671d719830a",
        "name": "Hair color",
        "type": "service",
        "priceservice": [
            {
                "id": "83017f5c-9938-481f-88e3-47e2e07205f9",
                "service": "02bb064a-f78d-4f84-9bcd-8671d719830a",
                "duration": "30Min",
                "price": 500
            }
        ],
        "service_group_id": "e44ccae3-40d7-44e1-87e1-80b7a48f044d",
        "service_group_name": "Hair Care"
    },
    "location": {
        "name": "Dubai",
        "id": "841ba0cb-de64-4e9f-b29a-fbba24141df2",
        "business_address": "Dubai - United Arab Emirates",
        "currency": "bf71d666-5b0f-4185-a857-cae2a0c5d86c",
        "email": "muhammadtayyabahmed14@gmail.com",
        "type": "location"
    },
    "client": {
        "id": "c42cadea-3cab-461a-a7c1-4f6362fd72dc",
        "name": "Muhammad Tayyab",
        "email": "",
        "phone_number": "+92-3176742642",
        "type": "client"
    },
    "employee": {
        "id": "b63d060c-0548-45bc-b394-ca35a133fef5",
        "name": "Muhammad Tayyab Ahmed",
        "type": "employee",
        "email": "muhammadtayyabahmed14@gmail.com",
        "address": "Dubai Marina",
        "designation": "Store Manager",
        "income_type": "Hourly_Rate",
        "salary": "20",
        "assigned_services": [
            {
                "id": "02bb064a-f78d-4f84-9bcd-8671d719830a",
                "name": "Hair color"
            },
            {
                "id": "0e2d70fd-3a9e-4b17-a17f-a01f6f91c3fa",
                "name": "Hair cut"
            }
        ]
    }
}


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def update_user_default_data(request):
    location = request.data.get('location', None)
    client = request.data.get('client', None)
    services = request.data.get('service', None)
    employee = request.data.get('employee', None)
    service_group = request.data.get('service_group', None)

    if not all([location, services, employee]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'location',
                        'client',
                        'service',
                        'employee',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    errors = []

    location_currency = None
    if location is not None:
        location = json.loads(location)
        name = location.get('name', '')
        id = location.get('id', None)
        address_name = location.get('business_address', '')
        currency = location.get('currency', '')
        email = location.get('email', '')

        try:
            location = BusinessAddress.objects.get(
                id=id
            )
        except Exception as err:
            errors.append(str(err))
        else:
            location.address_name = name
            location.address = address_name
            try:
                currency = Currency.objects.get(id=currency)
            except Exception as err:
                errors.append(str(err))
            else:
                location_currency = currency
                location.currency = currency
            location.email = email
            location.save()

    if service_group is not None:
        service_group = json.loads(service_group)

        service_group_name = service_group.get('name', '')
        service_group_id = service_group.get('id', None)

        try:
            service_group = ServiceGroup.objects.get(
                id=service_group_id
            )
        except Exception as err:
            errors.append(str(err))
        else:
            service_group.name = service_group_name
            service_group.save()

    services = json.loads(services)
    for service in services:
        id = service.get('id', None)
        name = service.get('name', None)
        description = service.get('description', '')
        priceservice = service.get('priceservice', None)
        service_group_id = service.get('service_group_id', None)
        service_group_name = service.get('service_group_name', None)

        try:
            service_instance = Service.objects.get(
                id=id
            )
        except Exception as err:
            errors.append(str(err))
        else:
            service_instance.name = name
            service_instance.description = description
            service_instance.save()

            price_services_ids = []
            for price in priceservice:
                price_id = price.get('id', None)
                price_services_ids.append(price_id)
            deleted_items = PriceService.objects.filter(service=service_instance).exclude(id__in=price_services_ids)
            deleted_items.delete()

            for price in priceservice:
                price_id = price.get('id', None)
                price_price = price.get('price', 0)
                price_duration = price.get('duration', '')
                try:
                    service_price = PriceService.objects.get(
                        id=price_id
                    )
                except:
                    PriceService.objects.create(
                        price=price_price,
                        duration=price_duration,
                        currency=location_currency,
                        service=service_instance
                    )
                else:
                    if location_currency is not None:
                        service_price.currency = location_currency
                    service_price.price = price_price
                    service_price.duration = price_duration
                    service_price.save()

    if client:
        client = json.loads(client)
        # id = client.get('id', None)
        name = client.get('name', None)
        email = client.get('email', '')
        phone_number = client.get('phone_number', None)

        if not name in ['', None]:

            try:
                client_instance = Client()
            except:
                pass
            else:
                client_instance.full_name = name
                client_instance.email = email
                client_instance.mobile_number = phone_number
                client_instance.business = location.business
                client_instance.is_activ = True
                client_instance.save()

            if email not in ['', None]:
                try:
                    thrd = Thread(target=add_client,
                                  args=[name, email, request.tenant_name, client_instance.business.business_name, ])
                    thrd.start()
                except Exception as err:
                    errors.append(str(err))

    if employee:
        employee = json.loads(employee)
        id = employee.get('id', None)
        name = employee.get('name', None)
        email = employee.get('email', None)
        address = employee.get('address', None)
        designation = employee.get('designation', None)
        income_type = employee.get('income_type', None)
        salary = employee.get('salary', None)
        assigned_services = employee.get('assigned_services', None)
        try:
            employee_instance = Employee.objects.get(
                id=id
            )
        except:
            pass
        else:
            employee_instance.full_name = name
            employee_instance.email = email
            employee_instance.address = address
            employee_instance.save()

            try:
                info = EmployeeProfessionalInfo.objects.get(
                    employee=employee_instance
                )
            except:
                pass
            else:
                info.designation = designation
                info.income_type = income_type
                info.salary = salary
                info.save()

            empl_servs_ids = []

            for empl_serv in assigned_services:
                emp_serv_id = empl_serv.get('id', None)
                empl_servs_ids.append(emp_serv_id)

            EmployeeSelectedService.objects.filter(
                employee=employee_instance
            ).exclude(service__id__in=empl_servs_ids).delete()

            for empl_serv in assigned_services:
                emp_serv_id = empl_serv.get('id', None)
                EmployeeSelectedService.objects.get_or_create(
                    service__id=emp_serv_id
                )

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
                        first_name=name,
                        username=username,
                        email=email,
                        is_email_verified=True,
                        is_active=True,
                        mobile_number=phone_number,
                    )
                    account_type = AccountType.objects.create(
                        user=user,
                        account_type='Employee'
                    )
                except Exception as err:
                    pass
                    # stop_thread = False
            try:
                thrd = Thread(target=add_employee, args=[name, email, phone_number, request.tenant_name,
                                                         employee_instance.business.business_name, request.tenant.id,
                                                         request.tenant_name, user])
                thrd.start()
            except Exception as err:
                errors.append(str(err))

    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'Business Default Data updated',
                'errors': errors
            }
        }
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_types(request):
    all_types = BusinessType.objects.filter(
        is_active=True,
        is_deleted=False
    )
    serialized = BusinessTypeSerializer(all_types, many=True, context={'request': request})
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'All business types',
                'data': serialized.data
            }
        }
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def create_user_business(request):
    user_id = request.data.get('user', None)
    business_name = request.data.get('business_name', None)
    country = request.data.get('country', None)
    state = request.data.get('state', None)
    city = request.data.get('city', None)
    postal_code = request.data.get('postal_code', None)
    address = request.data.get('address', None)
    opening_hours = request.data.get('opening_hours', None)
    business_types = request.data.get('business_types', None)
    software_used = request.data.get('software_used', None)

    if not all([user_id, business_name, country, state, city, postal_code, address, opening_hours, business_types,
                software_used]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'user',
                        'business_name',
                        'country',
                        'state',
                        'city',
                        'postal_code',
                        'address',
                        'opening_hours',
                        'business_types',
                        'software_used',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(
            id=user_id,
            is_blocked=False,
            is_deleted=False
        )
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.USER_NOT_EXIST_4005,
                'response': {
                    'message': 'User not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        domain = Domain.objects.get(
            domain=business_name.replace(' ', '-'),
            is_deleted=False,
            is_active=True,
            is_blocked=False
        )
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NAME_ALREADY_TAKEN_4014,
                'status_code_text': 'BUSINESS_NAME_ALREADY_TAKEN_4014',
                'response': {
                    'message': 'Business Name already taken',
                }
            },
            status=status.HTTP_403_FORBIDDEN
        )
    except:
        pass

    user_tenant = Tenant.objects.get(
        user=user,
        is_deleted=False,
        is_blocked=False
    )

    with tenant_context(user_tenant):
        website = request.data.get('website', '')
        sub_domain_new_name = business_name.replace(' ', '-')

        try:
            tnt_country = Country.objects.get(
                unique_code=country,
                is_deleted=False
            )
        except:
            tnt_country = None

        try:
            tnt_state = State.objects.get(
                unique_code=state,
                is_deleted=False
            )
        except:
            tnt_state = None

        try:
            tnt_city = City.objects.get(
                unique_code=state,
                is_deleted=False
            )
        except:
            tnt_city = None

    return Response(
        {
            'status': True,
            'status_code': 201,
            'response': {
                'message': 'Business Account Created',
                'data': {
                    'domain': sub_domain_new_name,
                }
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_business(request):
    user = request.GET.get('user', None)
    employee = request.GET.get('employee', None)

    if user is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'User id is required',
                    'fields': [
                        'user',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    if str(employee) == 'true':
        try:
            user = User.objects.get(id=user)
            emp = Employee.objects.get(email=user.email)
        except:
            pass
        try:
            user_business = Business.objects.get(
                user=emp.user.id,
                is_deleted=False,
                is_active=True,
                is_blocked=False
            )
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                    'response': {
                        'message': 'Business Not Found',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

    else:
        try:
            user_business = Business.objects.get(
                user=user,
                is_deleted=False,
                is_active=True,
                is_blocked=False
            )
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                    'response': {
                        'message': 'Business Not Found',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

    serialized = Business_GetSerializer(user_business, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': 'BUSINESS_FOUND',
            'response': {
                'message': 'Business Found',
                'error_message': None,
                'business': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_by_domain(request):
    domain_name = request.GET.get('domain', None)
    id = ''
    if domain_name is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'User id is required',
                    'fields': [
                        'domain',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        domain_name = f'{domain_name}.{settings.BACKEND_DOMAIN_NAME}'
        domain = None
        try:
            tenant_id = Tenant.objects.get(domain__iexact=domain_name)
            id = tenant_id.id
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code_text': 'Tenants Not Found',
                    'response': {
                        'message': 'Tenants Not Found',
                        'error_message': str(err),
                        'domain_name': domain_name,
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

        with tenant_context(Tenant.objects.get(schema_name='public')):
            domain = Domain.objects.get(domain__iexact=domain_name)

        if domain is not None:
            with tenant_context(domain.tenant):
                user_business = Business.objects.filter(
                    is_deleted=False,
                    is_active=True,
                    is_blocked=False
                )
                if len(user_business) > 0:
                    user_business = user_business[0]
                else:
                    raise Exception('0 Business found')
        else:
            raise Exception('Business Not Exist')
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': 'BUSINESS_FOUND',
            'response': {
                'message': 'Business Found',
                'error_message': None,
                'business': {
                    'id': str(user_business.id),
                    'business_name': str(user_business.business_name),
                    'tenant_id': str(id),
                    # 'logo' : user_business.logo if user_business.logo else None ,
                }
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business_additional_information(request):
    business_id = request.data.get('business', None)

    if business_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'User id is required',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(
            id=business_id,
            is_deleted=False,
            is_blocked=False
        )
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    is_completed = request.data.get('is_completed', None)

    team_size = request.data.get('team_size', business.team_size)
    how_find_us = request.data.get('how_find_us', business.how_find_us)

    selected_softwares = request.data.get('selected_softwares', [])
    selected_types = request.data.get('selected_types', [])
    currency_id = request.data.get('currency', None)

    try:
        currency = Currency.objects.get(id=currency_id)
        business.currency = currency
    except Exception as err:
        print(str(err))

    if is_completed is not None:
        business.is_completed = True
    else:
        business.is_completed = False

    business.team_size = team_size
    business.how_find_us = how_find_us
    business.save()

    if type(selected_softwares) == str:
        selected_softwares = json.loads(selected_softwares)
    elif type(selected_softwares) == list:
        pass

    business.software_used.clear()
    for software_id in selected_softwares:
        software = Software.objects.get(id=software_id)
        business.software_used.add(software)

    if type(selected_types) == str:
        selected_types = json.loads(selected_types)
    elif type(selected_types) == list:
        pass

    business.business_types.clear()
    for type_id in selected_types:
        type_obj = BusinessType.objects.get(id=type_id)
        business.business_types.add(type_obj)

    business.save()

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': 'Saved Data',
            'response': {
                'message': 'Successfully updated',
                'error_message': None,
            }
        },
        status=status.HTTP_200_OK
    )


# business_types
# software_used

@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business(request):
    business_id = request.data.get('business', None)

    if business_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'User id is required',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(
            id=business_id,
            is_deleted=False,
            is_blocked=False
        )
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    serialized = Business_PutSerializer(business, data=request.data)

    if serialized.is_valid():
        serialized.save()

        website_url = request.data.get('website', None)
        fb_url = request.data.get('facebook', None)
        insta_url = request.data.get('instagram', None)
        business_social, created = BusinessSocial.objects.get_or_create(
            business=business,
            user=business.user
        )

        if website_url is not None:
            business_social.website = website_url
        else:
            business_social.website = ''

        if fb_url is not None:
            business_social.facebook = fb_url
        else:
            business_social.facebook = ''

        if insta_url is not None:
            business_social.instagram = insta_url
        else:
            business_social.instagram = ''

        business_social.save()

        logo = request.data.get('logo', None)
        if logo is not None:
            business.logo = logo
            business.save()
        serialized = Business_GetSerializer(business, context={'request': request})
        return Response(
            {
                'status': True,
                'status_code': 200,
                'status_code_text': 'Saved Data',
                'response': {
                    'message': 'Successfully updated',
                    'error_message': None,
                    'business': serialized.data
                }
            },
            status=status.HTTP_200_OK
        )

    else:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.COULD_NOT_SAVE_FORM_DATA_4016,
                'status_code_text': 'COULD_NOT_SAVE_FORM_DATA_4016',
                'response': {
                    'message': 'Could not save, Something went wrong',
                    'error_message': serialized.errors,
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_locations(request, business_id):
    try:
        business = Business.objects.get(
            id=business_id,
            is_deleted=False,
            is_blocked=False,
            is_active=True
        )
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    business_addresses = BusinessAddress.objects.filter(
        business=business,
        is_deleted=False,
        is_closed=False,
        is_active=True
    ).order_by('-created_at').distinct()

    data = []
    if len(business_addresses) > 0:
        serialized = BusinessAddress_GetSerializer(business_addresses, many=True, context={'request': request})
        data = serialized.data

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Business All Locations',
                'error_message': None,
                'count': len(data),
                'locations': data,
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_business_location(request):
    business_id = request.data.get('business', None)
    user = request.user
    address = request.data.get('address', None)
    address_name = request.data.get('address_name', None)
    country_unique_id = request.data.get('country', None)
    state_unique_id = request.data.get('state', None)
    city_name = request.data.get('city', None)
    postal_code = request.data.get('postal_code', None)
    primary_translation_id = request.data.get('primary_translation_id', None)
    secondary_translation_id = request.data.get('secondary_translation_id', None)
    privacy_policy = request.data.get('privacy_policy', None)

    email = request.data.get('email', None)
    mobile_number = request.data.get('mobile_number', None)

    banking = request.data.get('banking', None)
    currency = request.data.get('currency', None)

    if not all([business_id, address, email, mobile_number, address_name]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'business',
                        'address',
                        'address_name',
                        'email',
                        'mobile_number',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(
            id=business_id,
            is_deleted=False,
            is_blocked=False,
            is_active=True
        )
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if business.user.id != user.id:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.USER_HAS_NO_PERMISSION_1001,
                'status_code_text': 'USER_HAS_NO_PERMISSION_1001',
                'response': {
                    'message': 'You are not allowed to add Business Location, Only Business owner can',
                    'error_message': 'Error message',
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        if currency is not None:
            currency_id = Currency.objects.get(id=currency, is_deleted=False, is_active=True)
        if country_unique_id is not None:
            public_country = get_country_from_public(country_unique_id)
            country, created = Country.objects.get_or_create(
                name=public_country.name,
                unique_id=public_country.unique_id
            )
        if state_unique_id is not None:
            public_state = get_state_from_public(state_unique_id)
            state, created = State.objects.get_or_create(
                name=public_state.name,
                unique_id=public_state.unique_id
            )
        if city_name is not None:
            city, created = City.objects.get_or_create(name=city_name,
                                                       country=country,
                                                       state=state,
                                                       country_unique_id=country_unique_id,
                                                       state_unique_id=state_unique_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 400,
                'status_code_text': 'Invalid Data',
                'response': {
                    'message': 'Invalid Country, State or City',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    primary_invoice_trans = InvoiceTranslation.objects.get(id=primary_translation_id)

    business_address = BusinessAddress(
        business=business,
        user=user,
        address=address,
        address_name=address_name,
        email=email,
        mobile_number=mobile_number,
        currency=currency_id,
        country=country if country_unique_id else None,
        state=state if state_unique_id else None,
        city=city if city_name else None,
        banking=banking,
        primary_translation=primary_invoice_trans,
        is_primary=False,
        is_active=True,
        is_deleted=False,
        is_closed=False,
        privacy_policy=privacy_policy
    )

    if secondary_translation_id:
        secondary_invoice_trans = InvoiceTranslation.objects.get(id=secondary_translation_id)
        business_address.secondary_translation = secondary_invoice_trans

    if postal_code is not None:
        business_address.postal_code = postal_code
    business_address.save()

    opening_day = request.data.get('open_day', None)
    if type(opening_day) == str:
        opening_day = json.loads(opening_day)
    else:
        pass

    days = [
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday',
    ]
    for day in days:

        bds_schedule = BusinessOpeningHour.objects.create(
            business_address=business_address,
            business=business,
            day=day,
        )
        s_day = opening_day.get(day.lower(), None)
        if s_day is not None:
            # bds_schedule.start_time = s_day.get('start_time', None)
            # bds_schedule.close_time = s_day.get('close_time', None)

            bds_schedule.start_time = s_day['start_time']
            bds_schedule.close_time = s_day['end_time']
        else:
            bds_schedule.is_closed = True

        bds_schedule.save()

    # serialized = OpeningHoursSerializer(busines_opening,  data=request.data)
    # if serialized.is_valid():
    #     serialized.save()
    #     data.update(serialized.data)
    try:
        all_product = Product.objects.filter(
            is_deleted=False
        )

        for pro in all_product:
            product = Product.objects.get(
                id=pro.id,
                is_deleted=False,
            )
            stock = ProductStock.objects.create(
                user=user,
                business=business,
                product=product,
                location=business_address,
                available_quantity=0,
                low_stock=0,
                reorder_quantity=0,
                # alert_when_stock_becomes_lowest = alert_when_stock_becomes_lowest,
                # is_active = stock_status,
            )
    except Exception as err:
        print(str(err))
        ExceptionRecord.objects.create(
            text=f'{str(err)} line number 761'
        )

    serialized = BusinessAddress_GetSerializer(business_address, context={'request': request})
    # if serialized.is_valid():
    #     serialized.save()
    #     data.update(serialized.data)
    return Response(
        {
            'status': True,
            'status_code': 201,
            'status_code_text': 'Created',
            'response': {
                'message': 'Location Added successfully',
                'error_message': None,
                'locations': serialized.data
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_location(request):
    user = request.user
    location_id = request.GET.get('location', None)

    if location_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'location',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business_address = BusinessAddress.objects.get(
            id=location_id,
            is_deleted=False,
            is_closed=False,
        )
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.LOCATION_NOT_FOUND_4017,
                'status_code_text': 'LOCATION_NOT_FOUND_4017',
                'response': {
                    'message': 'Location Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if business_address.user == user or business_address.business.user == user:
        business_address.is_deleted = True
        business_address.save()
        return Response(
            {
                'status': True,
                'status_code': 200,
                'status_code_text': '200',
                'response': {
                    'message': 'Location deleted!',
                    'error_message': None,
                }
            },
            status=status.HTTP_200_OK
        )

    else:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.USER_HAS_NO_PERMISSION_1001,
                'status_code_text': 'USER_HAS_NO_PERMISSION_1001',
                'response': {
                    'message': 'You don"t have permission to delete this location',
                    'error_message': 'User don"t have permission to delete this Business Address, user must be Business Owner or Location creator',
                }
            },
            status=status.HTTP_403_FORBIDDEN
        )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_location(request):
    location_id = request.data.get('location', None)
    primary_translation_id = request.data.get('primary_translation_id', None)
    secondary_translation_id = request.data.get('secondary_translation_id', None)

    if location_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'location',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business_address = BusinessAddress.objects.get(
            id=location_id,
            is_deleted=False,
            is_closed=False,
        )
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.LOCATION_NOT_FOUND_4017,
                'status_code_text': 'LOCATION_NOT_FOUND_4017',
                'response': {
                    'message': 'Location Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    opening_day = request.data.get('open_day', None)
    if type(opening_day) == str:
        opening_day = json.loads(opening_day)
    else:
        pass

    user = request.user
    # if business_address.user == user or business_address.business.user == user :
    business_address.privacy_policy = request.data.get('privacy_policy', business_address.privacy_policy)
    business_address.address_name = request.data.get('address_name', business_address.address_name)
    business_address.address = request.data.get('address', business_address.address)
    business_address.postal_code = request.data.get('postal_code', business_address.postal_code)
    business_address.mobile_number = request.data.get('mobile_number', business_address.mobile_number)
    business_address.email = request.data.get('email', business_address.email)
    business_address.banking = request.data.get('banking', business_address.banking)
    business_address.service_avaiable = request.data.get('service_avaiable', business_address.service_avaiable)
    business_address.location_name = request.data.get('location_name', business_address.location_name)
    business_address.description = request.data.get('description', business_address.description)

    country_unique_id = request.data.get('country', None)
    state_unique_id = request.data.get('state', None)
    city_name = request.data.get('city', None)
    currency = request.data.get('currency', None)
    images = request.data.get('images', None)
    is_publish = request.data.get('is_publish', None)

    if primary_translation_id:
        primary_invoice_trans = InvoiceTranslation.objects.get(id=primary_translation_id)
        business_address.primary_translation = primary_invoice_trans

    if secondary_translation_id:
        secondary_invoice_trans = InvoiceTranslation.objects.get(id=secondary_translation_id)
        business_address.secondary_translation = secondary_invoice_trans

    business_address.save()

    if is_publish is not None:
        business_address.is_publish = True
    else:
        business_address.is_publish = business_address.is_publish

    if images is not None:
        try:
            image = BusinessAddressMedia.objects.get(business=business_address.business,
                                                     business_address=business_address, )
            image.delete()
        except:
            pass
        images = BusinessAddressMedia.objects.create(
            user=user,
            business=business_address.business,
            business_address=business_address,
            image=images
        )

    try:
        if country_unique_id is not None:
            public_country = get_country_from_public(country_unique_id)
            country, created = Country.objects.get_or_create(
                name=public_country.name,
                unique_id=public_country.unique_id
            )
            business_address.country = country

        if state_unique_id is not None:
            public_state = get_state_from_public(state_unique_id)
            state, created = State.objects.get_or_create(
                name=public_state.name,
                unique_id=public_state.unique_id
            )
            business_address.state = state

        if city_name is not None:
            city, created = City.objects.get_or_create(name=city_name,
                                                       country=country,
                                                       state=state,
                                                       country_unique_id=country_unique_id,
                                                       state_unique_id=state_unique_id)
            business_address.city = city

        business_address.save()
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 400,
                'status_code_text': 'Invalid Data',
                'response': {
                    'message': 'Invalid Country, State or City',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    business_address.save()

    days = [
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday',
    ]

    for day in days:
        try:
            bds_schedule = BusinessOpeningHour.objects.get(business_address=business_address, day=day)

        except Exception as err:
            pass

        print(day)
        s_day = opening_day.get(day.lower(), None)
        if s_day is not None:
            bds_schedule.start_time = s_day['start_time']
            bds_schedule.close_time = s_day['end_time']
            bds_schedule.is_closed = False

        else:
            bds_schedule.is_closed = True

        bds_schedule.save()

    serialized = BusinessAddress_GetSerializer(business_address, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': 'Updated',
            'response': {
                'message': 'Location updated successful',
                'error_message': None,
                'location': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_theme(request):
    business_id = request.GET.get('business', None)

    if business_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    business_theme, created = BusinessTheme.objects.get_or_create(
        business=business,
        user=business.user,
        is_deleted=False,
        is_active=True
    )

    serialized = BusinessThemeSerializer(business_theme)
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': 'BusinessTheme',
            'response': {
                'message': 'Business Theme',
                'error_message': None,
                'theme': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business_theme(request):
    theme_id = request.data.get('theme', None)
    business_id = request.data.get('business', None)

    if not all([theme_id, business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'theme',
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    business_theme, created = BusinessTheme.objects.get_or_create(
        business=business,
        user=business.user,
        is_deleted=False,
        is_active=True
    )

    serialized = BusinessThemeSerializer(business_theme, data=request.data)
    if serialized.is_valid():
        serialized.save()
        return Response(
            {
                'status': True,
                'status_code': 200,
                'status_code_text': 'BusinessTheme',
                'response': {
                    'message': 'Business theme updated',
                    'error_message': None,
                    'theme': serialized.data
                }
            },
            status=status.HTTP_200_OK
        )

    return Response(
        {
            'status': True,
            'status_code': 400,
            'status_code_text': 'INVALID DATA',
            'response': {
                'message': 'Invalid Values',
                'error_message': str(serialized.errors),
            }
        },
        status=status.HTTP_400_BAD_REQUEST
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_business_language(request):
    business_id = request.data.get('business', None)
    language_id = request.data.get('language', None)
    is_default = request.data.get('is_default', False)

    if not all([language_id, business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'language',
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        language = Language.objects.get(id=language_id, is_active=True, is_deleted=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.LANGUAGE_NOT_FOUND_4018,
                'status_code_text': 'LANGUAGE_NOT_FOUND_4018',
                'response': {
                    'message': 'Language Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    language_obj = UserLanguage.objects.create(
        user=business.user,
        profile=business.profile,
        language=language,
        is_default=is_default
    )
    language_obj.save()

    prev_langs = UserLanguage.objects.all().exclude(id=language_obj.id)
    prev_langs.delete()
    seralized = UserLanguageSerializer(language_obj)
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Language Added',
                'error_message': None,
                'language': seralized.data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_language(request):
    id = request.data.get('id', None)

    if not all([id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        language = UserLanguage.objects.get(id=id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.LANGUAGE_NOT_FOUND_4018,
                'status_code_text': 'LANGUAGE_NOT_FOUND_4018',
                'response': {
                    'message': 'UserLanguage Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    seralized = UserLanguageSerializer(language, data=request.data, partial=True)
    if seralized.is_valid():
        seralized.save()
        return Response(
            {
                'status': True,
                'status_code': 200,
                'status_code_text': '200',
                'response': {
                    'message': 'Language Added',
                    'error_message': None,
                    'language': seralized.data
                }
            },
            status=status.HTTP_200_OK
        )

    else:
        return Response(
            {
                'status': False,
                'status_code': 400,
                'status_code_text': 'INVALID DATA',
                'response': {
                    'message': 'Updated unsuccessful',
                    'error_message': seralized.error_messages,
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_languages(request):
    business_id = request.GET.get('business', None)

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    business_languages = UserLanguage.objects.filter(user=business.user)
    seralized = UserLanguageSerializer(business_languages, many=True)
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Business languages',
                'error_message': None,
                'languages': seralized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_languages(request):
    id = request.data.get('id', None)

    if id is None:
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
        language = UserLanguage.objects.get(id=id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'UserLanguage Not Found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    language.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Language deleted successful',
                'error_message': None
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_languages(request):
    is_business_langugaes = request.GET.get('business_languages', False)

    only_english_and_arabic = ['English', 'Arabic']
    other_languages = ['Urdu', 'Spanish', 'French', 'Hindi', 'Russian',
                       'Chinese', 'Portuguese', 'Bengali']

    query = Q(is_active=True, is_deleted=False)

    if is_business_langugaes:
        query &= Q(name__in=only_english_and_arabic)
    else:
        all_list = only_english_and_arabic + other_languages
        query &= Q(name__in=all_list)

    all_languages = Language.objects.filter(query)

    serialized = LanguageSerializer(all_languages, many=True)
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'All languages',
                'error_message': None,
                'languages': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_business_notification_settings(request):
    business_id = request.GET.get('business', None)

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    staff_set, created = StaffNotificationSetting.objects.get_or_create(business=business, user=business.user,
                                                                        is_active=True)
    client_set, created = ClientNotificationSetting.objects.get_or_create(business=business, user=business.user,
                                                                          is_active=True)
    admin_set, created = AdminNotificationSetting.objects.get_or_create(business=business, user=business.user,
                                                                        is_active=True)
    stock_set, created = StockNotificationSetting.objects.get_or_create(business=business, user=business.user,
                                                                        is_active=True)

    staff_serializer = StaffNotificationSettingSerializer(staff_set)
    client_serializer = ClientNotificationSettingSerializer(client_set)
    admin_serializer = AdminNotificationSettingSerializer(admin_set)
    stock_serializer = StockNotificationSettingSerializer(stock_set)

    data = {}
    data.update(staff_serializer.data)
    data.update(client_serializer.data)
    data.update(admin_serializer.data)
    data.update(stock_serializer.data)
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'All Notification Settings',
                'error_message': None,
                'settings': data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business_notification_settings(request):
    business_id = request.data.get('business', None)
    if business_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    staff_set, created = StaffNotificationSetting.objects.get_or_create(business=business, user=business.user,
                                                                        is_active=True)
    client_set, created = ClientNotificationSetting.objects.get_or_create(business=business, user=business.user,
                                                                          is_active=True)
    admin_set, created = AdminNotificationSetting.objects.get_or_create(business=business, user=business.user,
                                                                        is_active=True)
    stock_set, created = StockNotificationSetting.objects.get_or_create(business=business, user=business.user,
                                                                        is_active=True)

    staff_serializer = StaffNotificationSettingSerializer(staff_set, data=request.data)
    client_serializer = ClientNotificationSettingSerializer(client_set, data=request.data)
    admin_serializer = AdminNotificationSettingSerializer(admin_set, data=request.data)
    stock_serializer = StockNotificationSettingSerializer(stock_set, data=request.data)

    data = {}
    if staff_serializer.is_valid():
        staff_serializer.save()
        data.update(staff_serializer.data)

    if client_serializer.is_valid():
        client_serializer.save()
        data.update(client_serializer.data)

    if admin_serializer.is_valid():
        admin_serializer.save()
        data.update(admin_serializer.data)

    if stock_serializer.is_valid():
        stock_serializer.save()
        data.update(stock_serializer.data)

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Notification setting updated',
                'error_message': None,
                'settings': data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_booking_settings(request):
    business_id = request.GET.get('business', None)

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    booking_setting, created = BookingSetting.objects.get_or_create(business=business, user=business.user,
                                                                    is_active=True)
    serializer = BookingSettingSerializer(booking_setting)

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Business Booking Setting',
                'error_message': None,
                'setting': serializer.data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business_booking_settings(request):
    business_id = request.data.get('business', None)

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    booking_setting, created = BookingSetting.objects.get_or_create(
        business=business,
        user=business.user,
        is_active=True
    )
    serializer = BookingSettingSerializer(booking_setting, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                'status': True,
                'status_code': 200,
                'status_code_text': '200',
                'response': {
                    'message': 'Business Booking setting updated!',
                    'error_message': None,
                    'setting': serializer.data
                }
            },
            status=status.HTTP_200_OK
        )

    else:
        return Response(
            {
                'status': False,
                'status_code': 400,
                'status_code_text': '400',
                'response': {
                    'message': 'Invalid Data',
                    'error_message': str(serializer.error_messages),
                    'tech_message': str(serializer.errors),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_payment_method(request):
    method_type = request.data.get('method_type', None)
    business_id = request.data.get('business', None)
    method_status = request.data.get('is_active', None)

    if not all([method_type, business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'method_type',
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    payment_method = BusinessPaymentMethod(
        user=user,
        business=business,
        method_type=method_type,
        is_active=method_status
    )
    payment_method.save()
    serialized = PaymentMethodSerializer(payment_method)

    return Response(
        {
            'status': True,
            'status_code': 201,
            'status_code_text': '201',
            'response': {
                'message': 'Payment method added!',
                'error_message': None,
                'payment_method': serialized.data
            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_payment_method(request):
    method_type = request.data.get('method_type', None)
    method_id = request.data.get('id', None)
    method_status = request.data.get('is_active', None)

    if not all([method_type, method_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'id',
                        'method_type',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user
    try:
        payment_method = BusinessPaymentMethod.objects.get(id=method_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Payment method Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    payment_method.method_type = method_type
    payment_method.is_active = method_status
    payment_method.save()
    serialized = PaymentMethodSerializer(payment_method, context={'request': request})

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Payment method updated!',
                'error_message': None,
                'payment_method': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_payment_methods(request):
    business_id = request.GET.get('business', None)
    get_all = request.GET.get('get_all', None)

    if not all([business_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    query = Q(business=business)

    if not get_all:
        query &= Q(is_active=True)

    payment_methods = BusinessPaymentMethod.objects.filter(query)
    serialized = PaymentMethodSerializer(payment_methods, many=True)

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Payment method added!',
                'error_message': None,
                'payment_methods': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_business_tax(request):
    business_id = request.data.get('business', None)
    tax_type = request.data.get('tax_type', 'Individual')
    name = request.data.get('name', None)
    tax_rate = request.data.get('tax_rate', None)
    tax_ids = request.data.get('tax_ids', None)
    location = request.data.get('location', None)

    tax_id = request.data.get('tax_id', None)

    if business_id is None or (tax_type != 'Location' and name is None) or (
            tax_type == 'Group' and tax_ids is None) or (tax_type == 'Location' and location is None):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'name',
                        'business',
                        'tax_type',

                        # 'tax_rate',
                        'tax_ids',
                        'location',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if tax_type == 'Location':
        try:
            location = BusinessAddress.objects.get(id=location)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.LOCATION_NOT_FOUND_4017,
                    'status_code_text': 'LOCATION_NOT_FOUND_4017',
                    'response': {
                        'message': 'Location Not Found',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            tax = BusinessTax.objects.get(id=tax_id)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.LOCATION_NOT_FOUND_4017,
                    'status_code_text': 'BUSINESSS_TAX_NOT_FOUND',
                    'response': {
                        'message': 'Business tax not found',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    if tax_rate is None:
        tax_rate = 0

    business_tax = BusinessTax.objects.create(
        user=user,
        business=business,
        tax_type=tax_type,
        tax_rate=tax_rate,
    )
    if tax_type == 'Group' or tax_type == 'Individual':
        business_tax.name = name
    if tax_type == 'Location':
        business_tax.location = location
        business_tax.parent_tax.add(tax)

    all_errors = []
    import json

    if tax_type == 'Group':
        # all_errors.append({'type' : str(type(tax_ids))})
        # all_errors.append({'tax_ids' : tax_ids})
        if tax_ids is not None:
            if type(tax_ids) == str:
                ids_data = json.loads(tax_ids)
            else:
                ids_data = tax_ids
            for id in ids_data:
                # all_errors.append(str(id))
                try:
                    get_p_tax = BusinessTax.objects.get(id=id)
                    business_tax.parent_tax.add(get_p_tax)
                except Exception as err:
                    all_errors.append(str(err))

    # parent_tax = 
    business_tax.save()
    serialized = BusinessTaxSerializer(business_tax, context={'request': request})
    return Response(
        {
            'status': True,
            'status_code': 201,
            'status_code_text': '201',
            'response': {
                'message': 'Business tax added!',
                'error_message': None,
                'tax': serialized.data,
                'errors': json.dumps(all_errors)
            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business_tax(request):
    tax_id = request.data.get('tax_id', None)
    business_id = request.data.get('business', None)
    tax_type = request.data.get('tax_type', None)
    name = request.data.get('name', None)
    tax_rate = request.data.get('tax_rate', None)
    tax_ids = request.data.get('tax_ids', None)
    location = request.data.get('location', None)
    parent_tax = request.data.get('parent_tax', None)

    if business_id is None or (tax_type != 'Location' and name is None) or (
            tax_type == 'Group' and tax_ids is None) or (tax_type == 'Location' and location is None):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'name',
                        'business',
                        'tax_type',
                        # 'tax_rate',
                        # 'tax_ids',
                        # 'location',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if (tax_type != 'Group' and tax_type != 'Location'):
        tax_rate = float(tax_rate)

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if tax_type == 'Location':
        try:
            location = BusinessAddress.objects.get(id=location)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.LOCATION_NOT_FOUND_4017,
                    'status_code_text': 'LOCATION_NOT_FOUND_4017',
                    'response': {
                        'message': 'Location Not Found',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            tax = BusinessTax.objects.get(id=parent_tax)
            print(tax)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.LOCATION_NOT_FOUND_4017,
                    'status_code_text': 'BUSINESSS_TAX_NOT_FOUND',
                    'response': {
                        'message': 'Business tax not found',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

    if tax_rate is None:
        tax_rate = 0

    try:
        business_tax = BusinessTax.objects.get(
            id=str(tax_id),
            # user = user,
            business=business,
        )
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Business tax Not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    business_tax.tax_type = tax_type
    business_tax.tax_rate = tax_rate
    if tax_type == 'Group' or tax_type == 'Individual':
        business_tax.name = name
    if tax_type == 'Location':
        business_tax.parent_tax.clear()
        business_tax.location = location
        business_tax.parent_tax.add(tax)

    if tax_type == 'Group':
        try:
            business_tax.parent_tax.clear()
        except:
            pass
        if type(tax_ids) == str:
            import json
            ids_data = json.loads(tax_ids)
        else:
            ids_data = tax_ids
        for id in ids_data:
            try:
                get_p_tax = BusinessTax.objects.get(id=id)
                business_tax.parent_tax.add(get_p_tax)
            except:
                pass
            # print(id)

    # parent_tax =
    business_tax.save()
    serialized = BusinessTaxSerializer(business_tax, context={'request': request})
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Business tax updated!',
                'error_message': None,
                'tax': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_business_payment_methods(request):
    user = request.user
    method_id = request.data.get('id', None)

    if method_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        payment_method = BusinessPaymentMethod.objects.get(id=method_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Business payment method not found!',
                    'error_message': None,
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if payment_method.business.user != user and payment_method.user != user:
        return Response(
            {
                'status': False,
                'status_code': 403,
                'status_code_text': '403',
                'response': {
                    'message': 'You are not allowed to delete this payment method!',
                    'error_message': None,
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    payment_method.delete()

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Business payment method deleted!',
                'error_message': None,
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_taxes(request):
    business_id = request.GET.get('business', None)

    if business_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    all_taxes = BusinessTax.objects.filter(business=business, is_active=True)
    serialized = BusinessTaxSerializer(all_taxes, many=True, context={'request': request})
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Business Taxes!',
                'error_message': None,
                'tax': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_business_tax(request):
    tax_id = request.data.get('tax', None)

    if tax_id is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'tax',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        tax = BusinessTax.objects.get(id=tax_id)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Tax Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    tax.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Business tax deleted!',
                'error_message': None,
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_business_vendor(request):
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
    vendor_csv = request.data.get('file', None)

    file = NstyleFile.objects.create(
        file=vendor_csv
    )

    vendors_list = []
    with open(file.file.path, 'r', encoding='utf-8-sig', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        for row in csv_reader:

            name = row.get('Vendor Name', None)
            contact = row.get('Contact', None)
            email = row.get('Email', None)
            address = row.get('Address', None)
            status_check = row.get('Status', None)
            gst_in = row.get('GST IN', None)

            if all([name, contact, email, address, status_check, gst_in]) and (name not in ["", None]):
                is_active = True if status_check == 'Active' else False
                vendors_list.append(
                    BusinessVendor(
                        user=user,
                        vendor_name=name,
                        mobile_number=contact,
                        email=email,
                        address=address,
                        gstin=gst_in,
                        is_active=is_active
                    )
                )
            else:
                return Response(
                    {
                        'status': False,
                        'status_code': StatusCodes.MISSING_FIELDS_4001,
                        'status_code_text': 'MISSING_FIELDS_4001',
                        'response': {
                            'message': 'Invalid Data!',
                            'error_message': 'All fields are required.',
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        BusinessVendor.objects.bulk_create(vendors_list)

    file.delete()
    all_vendors = BusinessVendor.objects.filter(is_deleted=False, is_closed=False)
    serialized = BusinessVendorSerializer(all_vendors, many=True)
    # return Response({'Status' : 'Success'})
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'All available business vendors!',
                'error_message': None,
                'vendors': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_vendors(request):
    search_text = request.query_params.get('search_text', None)
    no_pagination = request.query_params.get('no_pagination', None)

    all_vendors = BusinessVendor.objects.filter(is_deleted=False, is_closed=False).order_by('-created_at')

    if search_text:
        # query
        query = Q(vendor_name__icontains=search_text)
        query |= Q(mobile_number__icontains=search_text)
        query |= Q(address__icontains=search_text)
        query |= Q(user__email__icontains=search_text)
        all_vendors = all_vendors.filter(query)

    serialized = list(BusinessVendorSerializer(all_vendors, many=True).data)

    paginator = CustomPagination()
    paginator.page_size = 100000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'vendors')
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def get_business_vendors_dropdown(request):
    search_text = request.query_params.get('search_text', None)
    # no_pagination = request.GET.get('no_pagination', None)
    page = request.GET.get('page', None)
    is_searched = False

    all_vendors = BusinessVendor.objects.filter(is_deleted=False, is_closed=False, is_active=True).order_by(
        '-created_at')

    if search_text:
        # query
        query = Q(vendor_name__icontains=search_text)
        query |= Q(mobile_number__icontains=search_text)
        query |= Q(address__icontains=search_text)
        query |= Q(user__email__icontains=search_text)
        all_vendors = all_vendors.filter(query)
        is_searched = True

    serialized = list(BusinessVendorSerializerDropdown(all_vendors, many=True).data)

    paginator = CustomPagination()
    paginator.page_size = 10 if page else 100000
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'vendors', invoice_translations=None, current_page=page,
                                                is_searched=is_searched)
    return response


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def check_vendor_existance(request):
    email = request.data.get('email', None)
    mobile_number = request.data.get('mobile_number', None)
    instanceId = request.data.get('instance_id', None)

    if email and mobile_number:
        all_vendors = BusinessVendor.objects.filter(
            Q(email=email) |
            Q(mobile_number=mobile_number),
            is_deleted=False,
            is_closed=False,
        )
    else:
        queries = {}
        if email:
            queries['email'] = email
        if mobile_number:
            queries['mobile_number'] = mobile_number

        all_vendors = BusinessVendor.objects.filter(
            is_deleted=False,
            is_closed=False,
            **queries
        )

    if instanceId:
        all_vendors = all_vendors.exclude(id=instanceId)

    fields = []
    for vendor in all_vendors:
        if email and vendor.email == email:
            fields.append('EMAIL')
        if mobile_number and vendor.mobile_number == mobile_number:
            fields.append('MOBILE_NUMBER')
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'All available business vendors!',
                'error_message': None,
                'fields': fields,
                'count': all_vendors.count(),
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_business_vendor(request):
    user = request.user
    business_id = request.data.get('business', None)
    vendor_name = request.data.get('vendor_name', None)
    address = request.data.get('address', None)
    mobile_number = request.data.get('mobile_number', None)

    email = request.data.get('email', '')
    country_unique_id = request.data.get('country', None)
    state_unique_id = request.data.get('state', None)
    city_name = request.data.get('city', None)
    gstin = request.data.get('gstin', None)
    website = request.data.get('website', None)
    is_active = request.data.get('is_active', None)

    if not all([business_id, vendor_name, address, is_active]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'business', 'vendor_name', 'address', 'is_active'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        if country_unique_id is not None:
            public_country = get_country_from_public(country_unique_id)
            country, created = Country.objects.get_or_create(
                name=public_country.name,
                unique_id=public_country.unique_id
            )
        if state_unique_id is not None:
            public_state = get_state_from_public(state_unique_id)
            state, created = State.objects.get_or_create(
                name=public_state.name,
                unique_id=public_state.unique_id
            )
        if city_name is not None:
            city, created = City.objects.get_or_create(name=city_name,
                                                       country=country,
                                                       state=state,
                                                       country_unique_id=country_unique_id,
                                                       state_unique_id=state_unique_id
                                                       )
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 400,
                'status_code_text': 'Invalid Data',
                'response': {
                    'message': 'Invalid Country, State or City',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'Business Not Found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    if is_active is not None:
        is_active = json.loads(is_active)
    else:
        is_active = True

    try:
        vendor = BusinessVendor.objects.create(
            email=email,
            user=user,
            business=business,
            country=country if country_unique_id else None,
            state=state if state_unique_id else None,
            city=city if city_name else None,
            vendor_name=vendor_name,
            address=address,
            gstin=gstin,
            website=website,
            mobile_number=mobile_number,
            is_active=is_active,
        )
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 400,
                'status_code_text': 'Invalid Data',
                'response': {
                    'message': 'Something went wrong',
                    'error_message': str(err),
                    'email': email
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    serialized = BusinessVendorSerializer(vendor)
    return Response(
        {
            'status': True,
            'status_code': 201,
            'status_code_text': '201',
            'response': {
                'message': 'Business vendors created!',
                'error_message': None,
                'vendor': serialized.data
            }
        },
        status=status.HTTP_201_CREATED
    )


@transaction.atomic
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business_vendor(request):
    vendor_id = request.data.get('vendor', True)
    country_unique_id = request.data.get('country', None)
    state_unique_id = request.data.get('state', None)
    city_name = request.data.get('city', None)
    email = request.data.get('email', None)

    if not all([vendor_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'vendor'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        vendor = BusinessVendor.objects.get(
            id=vendor_id
        )
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Vendor not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    phone_number = request.data.get('mobile_number', None)
    if phone_number is not None:
        vendor.mobile_number = phone_number
    else:
        vendor.mobile_number = None
    vendor.save()
    if country_unique_id is not None:
        public_country = get_country_from_public(country_unique_id)
        country, created = Country.objects.get_or_create(
            name=public_country.name,
            unique_id=public_country.unique_id
        )
        vendor.country = country

    if state_unique_id is not None:
        public_state = get_state_from_public(state_unique_id)
        state, created = State.objects.get_or_create(
            name=public_state.name,
            unique_id=public_state.unique_id
        )
        vendor.state = state

    if city_name is not None:
        city, created = City.objects.get_or_create(name=city_name,
                                                   country=country,
                                                   state=state,
                                                   country_unique_id=country_unique_id,
                                                   state_unique_id=state_unique_id)
        vendor.city = city

    vendor.save()
    serialized = BusinessVendorSerializer(vendor, data=request.data)
    if serialized.is_valid():
        serialized.save()
        return Response(
            {
                'status': True,
                'status_code': 200,
                'status_code_text': '200',
                'response': {
                    'message': 'Business vendors updated!',
                    'error_message': None,
                    'vendor': serialized.data
                }
            },
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {
                'status': False,
                'status_code': 400,
                'status_code_text': '400',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': str(serialized.errors),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_business_vendor(request):
    vendor_id = request.data.get('vendor', True)

    if not all([vendor_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'Following fields are required',
                    'fields': [
                        'vendor'
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        vendor = BusinessVendor.objects.get(
            id=vendor_id
        )
    except Exception as err:
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Vendor not found',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    vendor.delete()
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Business vendors deleted!',
                'error_message': None,
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def search_business_vendor(request):
    text = request.GET.get('text', None)

    if text is None:
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'All fields are required.',
                    'fields': [
                        'text',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    search_vendor = BusinessVendor.objects.filter(
        Q(vendor_name__icontains=text) |
        Q(address__icontains=text) |
        Q(mobile_number__icontains=text) |
        Q(email__icontains=text)

    )
    serialized = BusinessVendorSerializer(search_vendor, many=True, context={'request': request})
    return Response(
        {
            'status': True,
            'status_code': 200,
            'response': {
                'message': 'All Search Business Vendor!',
                'error_message': None,
                'count': len(serialized.data),
                'vendors': serialized.data,
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_domain_business_address(request):
    tenant_id = request.GET.get('hash', None)
    data = []
    service_group = []

    if tenant_id is None:
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
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        tenant = Tenant.objects.get(id=tenant_id)
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
    with tenant_context(tenant):
        user_business = Business.objects.filter(
            is_deleted=False,
            is_active=True,
            is_blocked=False
        )
        if len(user_business) > 0:
            user_business = user_business[0]
        else:
            raise Exception('0 Business found')
        try:
            business_addresses = BusinessAddress.objects.filter(
                business=str(user_business.id),
                is_deleted=False,
                is_closed=False,
                is_active=True
            ).order_by('-created_at').distinct()
        except Exception as err:
            print(err)

        if len(business_addresses) > 0:
            serialized = BusinessAddress_CustomerSerializer(business_addresses, many=True, context={
                'tenant': tenant.schema_name})
            data = serialized.data
        else:
            raise Exception('0 business addresses found')
        try:
            services_group = ServiceGroup.objects.filter(
                business=str(user_business.id)
                , is_deleted=False,
                is_blocked=False).order_by('-created_at')
        except Exception as err:
            print(err)

        if len(services_group) > 0:
            serialized = ServiceGroupSerializer(services_group, many=True,
                                                context={'request': request, 'tenant': tenant.schema_name})
            service_group = serialized.data
        else:
            raise Exception('0 business addresses found')

    #     else :
    #         raise Exception('Business Not Exist')
    # except Exception as err:
    #     return Response(
    #         {
    #             'status' : False,
    #             'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
    #             'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
    #             'response' : {
    #                 'message' : 'Business Not Found',
    #                 'error_message' : str(err),
    #             }
    #         },
    #         status=status.HTTP_404_NOT_FOUND
    #     )

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Business All Locations',
                'error_message': None,
                'count': len(data),
                'locations': data,
                'service_group': service_group,
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def get_check_availability(request):
    check_availability = request.data.get('check_availability', None)
    tenant_id = request.data.get('hash', None)

    Availability = True
    if tenant_id is None:
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
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        tenant = Tenant.objects.get(id=tenant_id)
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

    if type(check_availability) == str:
        check_availability = json.loads(check_availability)
    else:
        pass

    data = []
    with tenant_context(tenant):
        for check in check_availability:
            emp_id = check.get('member_id', None)
            duration = check.get('duration', None)
            start_time = check.get('app_time', None)
            date = check.get('date', None)

            dtime = datetime.strptime(start_time, "%H:%M:%S")
            start_time = dtime.time()

            dt = datetime.strptime(date, "%Y-%m-%d")
            date = dt.date()

            app_date_time = f'2000-01-01 {start_time}'

            duration = DURATION_CHOICES[duration.lower()]
            app_date_time = datetime.fromisoformat(app_date_time)
            datetime_duration = app_date_time + timedelta(minutes=duration)
            datetime_duration = datetime_duration.strftime('%H:%M:%S')
            tested = datetime.strptime(datetime_duration, '%H:%M:%S').time()
            end_time = datetime_duration

            EmployeDaily = False

            try:
                employee = Employee.objects.get(
                    id=emp_id,
                    # employedailyschedule__is_vacation = False,
                    # employedailyschedule__created_at__lte = dt,
                    # employedailyschedule__start_time__gte = start_time,
                    # employedailyschedule__end_time__lte = start_time
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
                            return Response(
                                {
                                    'status': True,
                                    'status_code': 200,
                                    'response': {
                                        'message': f'{employee.full_name} is not available at this time',
                                        'error_message': f'This Employee day off, {employee.full_name} date {date}',
                                        'Availability': False
                                    }
                                },
                                status=status.HTTP_200_OK
                            )
                    else:
                        return Response(
                            {
                                'status': True,
                                'status_code': 200,
                                'response': {
                                    'message': f'{employee.full_name} is not available at this time',
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
                                'message': 'Employee Day Off',
                                'error_message': f'This Employee day off, {employee.full_name} date {date} {str(err)}',
                                'Availability': False
                            }
                        },
                        status=status.HTTP_200_OK
                    )

                # if EmployeDaily:
                #     data.append(f'Employees daily schedule not Available {employee.full_name}')

                # try:

                # av_staff_ids = AppointmentService.objects.filter(
                #     member__id = employee.id,
                #     appointment_date = date,
                #     # appointment_time__gte = start_time, # 1:00
                #     # end_time__lte = start_time, # 1:40
                #     # member__employee_employedailyschedule__date = date,
                #     # member__employee_employedailyschedule__start_time__gte = start_time,
                #     # member__employee_employedailyschedule__end_time__lte = start_time,
                #     is_blocked = False,
                # )

                # for ser in av_staff_ids:
                #     if tested <= ser.appointment_time:# or start_time >= ser.end_time:
                #         if start_time >= ser.end_time:
                #             data.append(f'Employees are free, employee name {employee.full_name}')

                #         else:
                #             pass
                #             # data.append(f'The selected staff is not available at this time  {employee.full_name}')
                #             # Availability = False

                #     else:
                #         data.append(f'Employees are free, employee name: {employee.full_name}')

                # if len(av_staff_ids) == 0:
                #     data.append(f'Employees are free, you can proceed further employee name {employee.full_name}')

                # av_staff_ids = AppointmentService.objects.filter(
                #         member__id=employee.id,
                #         appointment_date=date,
                #         is_blocked= True,
                #         appointment_time__lt=end_time,
                #         end_time__gt=start_time,
                #     )

                # if av_staff_ids:
                #         # Check if the selected time slot overlaps with any existing appointments
                #         for appointment in av_staff_ids:
                #             if start_time < appointment.end_time and tested > appointment.appointment_time:
                #                 Availability = False
                #                 data.append(f'Error: Employee {employee.full_name} already has an appointment scheduled during the selected time slot.')
                #                 break

                try:
                    av_staff_ids = AppointmentService.objects.filter(
                        member__id=employee.id,
                        appointment_date=date,
                        # is_blocked=False,
                        appointment_time__lt=end_time,
                        end_time__gt=start_time,
                    )

                    if av_staff_ids:
                        # Check if the selected time slot overlaps with any existing appointments
                        for appointment in av_staff_ids:
                            if start_time < appointment.end_time and tested > appointment.appointment_time:
                                Availability = False
                                data.append(
                                    f'Error: Employee {employee.full_name} already has an appointment scheduled during the selected time slot.')
                                break
                        else:
                            data.append(f'Employees are free, employee name: {employee.full_name}')
                    else:
                        data.append(f'Employees are free, employee name: {employee.full_name}')

                except Exception as err:
                    data.append(f'Error: {str(err)}')


            except Exception as err:
                data.append(f'the Error  {str(err)},  Employee Not Available on this time')

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'The selected staff is not available at this time',
                'error_message': None,
                'employee': data,
                'Availability': Availability,
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def get_employee_appointment(request):
    tenant_id = request.data.get('hash', None)
    business_id = request.data.get('business', None)
    appointment_date = request.data.get('appointment_date', None)
    start_time = request.data.get('start_time', None)
    # employee_list = request.data.get('emp_list', None)

    if tenant_id is None:
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

    data = []
    error = []

    dtime = datetime.strptime(start_time, "%H:%M:%S")
    start_time = dtime.time()

    dt = datetime.strptime(appointment_date, "%Y-%m-%d")
    date = dt.date()
    # if type(employee_list) == str:
    #     employee_list = json.loads(employee_list)
    # else:
    #     pass

    with tenant_context(tenant):

        try:
            business = BusinessAddress.objects.get(id=business_id)
        except Exception as err:
            return Response(
                {
                    'status': True,
                    'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                    'response': {
                        'message': 'Business Address not found!',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        employee = Employee.objects.filter(
            is_deleted=False,
            location__id=business.id,
            # employee_employedailyschedule__is_vacation = False,
            # employee_selected_service__service__id = str(service),
        )
        for emp in employee:
            serializer = EmployeeBusinessSerializer(emp)
            data.append(serializer.data)
            # try:
            #     daily_schedule = EmployeDailySchedule.objects.get(
            #         employee = emp.id,
            #         is_vacation = False,
            #         date = date,
            #     )  
            #     if start_time >= daily_schedule.start_time and start_time < daily_schedule.end_time :
            #         serializer = EmployeeBusinessSerializer(emp)
            #         data.append(serializer.data)
            #     elif daily_schedule.start_time_shift != None:
            #         if start_time >= daily_schedule.start_time_shift and start_time < daily_schedule.end_time_shift:
            #             serializer = EmployeeBusinessSerializer(emp)
            #             data.append(serializer.data)
            #         else:
            #             pass
            #         #     return Response(
            #         #     {
            #         #         'status' : True,
            #         #         'status_code' : 200,
            #         #         'response' : {
            #         #             'message' : f'This time {employee.full_name} not Available',
            #         #             'error_message' : f'This Employee day off, {employee.full_name} date {date}',
            #         #             'Availability': False
            #         #         }
            #         #     },
            #         #     status=status.HTTP_200_OK
            #         # )
            #     else:
            #         pass
            #     #     return Response(
            #     #     {
            #     #         'status' : True,
            #     #         'status_code' : 200,
            #     #         'response' : {
            #     #             'message' : f'This time {employee.full_name} not Available',
            #     #             'error_message' : f'This Employee day off, {employee.full_name} date {date}',
            #     #             'Availability': False
            #     #         }
            #     #     },
            #     #     status=status.HTTP_200_OK
            #     # )
            # except Exception as err:
            #     pass

        # serializer = EmployeeBusinessSerializer(employee)
        # data.append(serializer.data)

        # for check in employee_list:
        #     date = check.get('date', None)
        #     start_time = check.get('app_time', None)
        #     duration = check.get('duration', None)
        #     service = check.get('service', None)

        #     dtime = datetime.strptime(start_time, "%H:%M:%S")
        #     start_time = dtime.time()

        #     app_date_time = f'2000-01-01 {start_time}'

        #     duration = DURATION_CHOICES[duration]
        #     app_date_time = datetime.fromisoformat(app_date_time)
        #     datetime_duration = app_date_time + timedelta(minutes=duration)
        #     datetime_duration = datetime_duration.strftime('%H:%M:%S')
        #     tested = datetime.strptime(datetime_duration ,'%H:%M:%S').time()
        #     end_time = datetime_duration

        #     # try:
        #     #     service_id=Service.objects.get(id=str(service))
        #     # except Exception as err:
        #     #     #service_id = ''
        #     #     pass
        # #     return Response(
        # #     {
        # #         'status' : True,
        # #         'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
        # #         'status_code_text' :'BUSINESS_NOT_FOUND_4015' ,
        # #         'response' : {
        # #             'message' : 'Business Address not found!',
        # #             'error_message' : str(err),
        # #         }
        # #     },
        # #     status=status.HTTP_404_NOT_FOUND
        # # )

        #     employee = Employee.objects.get(is_deleted=False, 
        #         location__id = business.id, 
        #         #employee_employedailyschedule__is_vacation = False,
        #         #employee_selected_service__service__id = str(service),
        #         )#.order_by('-created_at')

        #     try:
        #         av_staff_ids = AppointmentService.objects.filter(
        #             member__id = employee.id,
        #             appointment_date = date,
        #             # appointment_time__gte = start_time, # 1:00
        #             # end_time__lte = start_time, # 1:40
        #             # member__employee_employedailyschedule__date = date,
        #             member__employee_employedailyschedule__start_time__gte = start_time,
        #             member__employee_employedailyschedule__end_time__lte = start_time,
        #             is_blocked = False,
        #         )#.values_list('member__id', flat=True)

        #         for ser in av_staff_ids:
        #             #data.append(f'{av_staff_ids} type {type(start_time)}, tested {ser.appointment_time}')
        #             if tested <= ser.appointment_time:# or start_time >= ser.end_time:
        #                 if start_time >= ser.end_time:
        #                     serializer = EmployeeBusinessSerializer(employee)
        #                     data.append(serializer.data)
        #                     #data.append(f'Employees are free, employee name {employee.full_name}')

        #                 else:
        #                     #data.append(f'The selected staff is not available at this time  {employee.full_name}')
        #                     Availability = False

        #             else:
        #                 serializer = EmployeeBusinessSerializer(employee)
        #                 data.append(serializer.data)
        #                 #data.append(f'Employees are free, employee name: {employee.full_name}')

        #         if len(av_staff_ids) == 0:
        #             serializer = EmployeeBusinessSerializer(employee)
        #             data.append(serializer.data)
        #             #data.append(f'Employees are free, you can proceed further employee name {employee.full_name}')

        #             #data.append(f'{av_staff_ids} type {type(datetime_duration)}, ')

        #     except Exception as err:
        #         pass
        # data.append(f'the employe{employee}, start_time {str(err)}')

        # for emp in all_emp:

        #     #data.append(emp)
        #     serializer = EmployeeBusinessSerializer(emp)
        #     data.append(serializer.data)

        # for emp in all_emp:
        #     availability = AppointmentService.objects.filter(
        #         #member__id__in = empl_list,
        #         #business = ,
        #         member__id = emp.id,
        #         appointment_date = date,
        #         is_blocked = False,
        #         # appointment_time__lte = start_time, # 1:00
        #         # end_time__gte = start_time,
        #     )
        # for ser in availability:
        #     #data.append(f'{av_staff_ids} type {type(start_time)}, tested {ser.appointment_time}')
        #     if tested <= ser.appointment_time:# or start_time >= ser.end_time:
        #         if start_time >= ser.end_time:
        #             serializer = EmployeeBusinessSerializer(emp)
        #             data.append(serializer.data)
        #             #data.append(f'Employees are free, employee name {employee.full_name}')

        #         else:
        #             pass
        #             data.append(f'The selected staff is not available at this time  {employee.full_name}')
        #             #Availability = False

        #     else:
        #         data.append(f'Employees are free, employee name: {employee.full_name}')

        # if len(availability) >= 0 or len(availability) <= 3 :
        #     serializer = EmployeeBusinessSerializer(emp)
        #     data.append(serializer.data)

        #     return Response(
        #     {
        #         'status' : True,
        #         'status_code' : 200,
        #         'status_code_text' : '200',
        #         'response' : {
        #             'message' : 'Employees are free',
        #             'error_message' : None,
        #             'employee':serializer.data
        #         }
        #     },
        #     status=status.HTTP_200_OK
        # )
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Employees are free',
                'error_message': None,
                'error': error,
                'employee': data
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def create_client_business(request):
    tenant_id = request.data.get('hash', None)
    name = request.data.get('full_name', None)
    email = request.data.get('email', None)
    number = request.data.get('mobile_number', None)
    password = request.data.get('password', None)

    business_id = request.data.get('business', None)

    data = []

    if tenant_id is None:
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
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        tenant = Tenant.objects.get(id=tenant_id)
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

    with tenant_context(tenant):

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
            client = Client.objects.get(mobile_number__icontains=number)
        except Exception as err:
            client = ''
            pass
        if len(client) > 0:
            data.append(f'Client Phone number already exist {client.full_name}')
        else:
            client = Client.objects.create(
                # user = tenant.user,
                business=business,
                full_name=name,
                mobile_number=number,
                email=email,
            )
            data.append(f'Client Created Successfully {client.full_name}')
    try:
        username = email.split('@')[0]
        user = User.objects.create(
            first_name=name,
            username=username,
            email=email,
            is_email_verified=True,
            is_active=True,
            mobile_number=number,
        )
        user.set_password(password)
        user.save()
    except Exception as err:
        return Response(
            {
                'status': True,
                'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                'response': {
                    'message': 'User not found!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    serialized = UserTenantLoginSerializer(user)

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Client Create Successfully',
                'error_message': None,
                'client': serialized.data,
            }
        },
        status=status.HTTP_200_OK
    )


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def employee_availability(request):
    employee = request.data.get('employee', None)
    tenant_id = request.data.get('hash', None)
    date = request.data.get('date', None)

    if tenant_id is None:
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
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        tenant = Tenant.objects.get(id=tenant_id)
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

    if type(employee) == str:
        employee = json.loads(employee)
    else:
        pass

    data = []
    dt = datetime.strptime(date, "%Y-%m-%d")
    date = dt.date()

    with tenant_context(tenant):
        for check in employee:
            emp_id = check.get('member_id', None)

            try:
                employee = Employee.objects.get(id=emp_id)
                av_staff_ids = AppointmentService.objects.filter(

                    member__id=employee.id,
                    appointment_date=date,
                    is_blocked=False,
                )  # .values_list('member__id', flat=True)
                serilizer = EmployeAppointmentServiceSerializer(av_staff_ids, many=True)
                data.extend(serilizer.data)
            except Exception as err:
                pass

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Employees Check Availability',
                'error_message': None,
                'employee': data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_tenant_business_taxes(request):
    tenant_id = request.GET.get('hash', None)
    business_id = request.GET.get('business', None)

    if tenant_id is None:
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
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        tenant = Tenant.objects.get(id=tenant_id)
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
    data = []
    with tenant_context(tenant):
        try:
            business = Business.objects.get(id=business_id, is_deleted=False, is_active=True, is_blocked=False)
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                    'response': {
                        'message': 'Business Not Found',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

        all_taxes = BusinessTax.objects.filter(business=business, is_active=True)
        serialized = BusinessTaxSerializer(all_taxes, many=True, context={'request': request})
        data.append(serialized.data)
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Business Taxes!',
                'error_message': None,
                'tax': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_tenant_address_taxes(request):
    tenant_id = request.GET.get('hash', None)
    location_id = request.GET.get('location_id', None)
    data = []
    if tenant_id is None:
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
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        tenant = Tenant.objects.get(id=tenant_id)
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

    data = []
    with tenant_context(tenant):
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
        data.append(serialized.data)
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Address Taxes!',
                'error_message': None,
                'tax': data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_address_taxes_device(request):
    location_id = request.GET.get('location_id', None)
    data = []
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
    data.append(serialized.data)
    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Address Taxes!',
                'error_message': None,
                'tax': data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_common_tenant(request):
    tenant_id = '14c286c6-c36c-4c7a-aa51-545efcd8738d'  # request.GET.get('hash', None)
    business_location = '6febd650-50ba-4719-aaf2-02bccebb7856'
    business = '38a86f91-f0cb-4673-a68c-11645d0046b4'
    address = 'MR lahore'
    address_name = 'Multan Road, Samanabad Town, Lahore, Pakistan'

    return Response(
        {
            'status': True,
            'status_code': 200,
            'status_code_text': '200',
            'response': {
                'message': 'Tenant Details!',
                'error_message': None,
                'hash': tenant_id,
                'business': business,
                'business_location': business_location,
                'address': address,
                'address_name': address_name,
            }
        },
        status=status.HTTP_200_OK
    )


class getUserBusinessProfileCompletionProgress(APIView):
    permission_classes = [AllowAny]

    def get_business_info_progress(self, request):

        total_modules = 4
        completed_modules = 0

        if len(self.business.business_types.all()) > 0:
            completed_modules += 1

        if self.business.how_find_us:
            completed_modules += 1

        if self.business.team_size:
            completed_modules += 1

        if self.business.currency:
            completed_modules += 1

        return {
            'total_modules': total_modules,
            'completed_modules': completed_modules,
        }

    def get_business_setting_progress(self, request):

        total_modules = 6
        completed_modules = 0

        if self.business.business_name:
            completed_modules += 1

        if self.business.logo:
            completed_modules += 1

        business_locations = BusinessAddress.objects.filter(
            business=self.business
        )

        if len(business_locations) > 0:
            completed_modules += 1

        try:
            social_links = BusinessSocial.objects.get(
                business=self.business
            )
        except:
            pass
        else:
            if social_links.website:
                completed_modules += 1
            if social_links.facebook:
                completed_modules += 1
            if social_links.instagram:
                completed_modules += 1

        return {
            'total_modules': total_modules,
            'completed_modules': completed_modules,
        }

    def get_financial_settings_progress(self, request):
        total_modules = 4
        completed_modules = 0

        payment_methods = BusinessPaymentMethod.objects.filter(
            business=self.business
        )
        if len(payment_methods) > 0:
            completed_modules += 1

        business_taxes = BusinessTax.objects.filter(
            business=self.business
        ).values_list('tax_type', flat=True)
        business_taxes = list(business_taxes)

        for tax_type in ['Individual', 'Group', 'Location']:
            if business_taxes.count(tax_type) > 0:
                completed_modules += 1

        return {
            'total_modules': total_modules,
            'completed_modules': completed_modules,
        }

    def get_business_services_progress(self, request):
        total_modules = 2
        completed_modules = 0

        services = Service.objects.filter(
            business=self.business,
            is_deleted=False
        )

        if len(services) > 0:
            completed_modules += 1

            service_groups = ServiceGroup.objects.filter(
                is_deleted=False,
                is_active=True,
                is_blocked=False
            )

            if len(service_groups) > 0:
                completed_modules += 1

        return {
            'total_modules': total_modules,
            'completed_modules': completed_modules,
        }

    def get(self, request):
        business_id = request.GET.get('business_id', None)

        if not business_id:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.MISSING_FIELDS_4001,
                    'status_code_text': 'MISSING_FIELDS_4001',
                    'response': {
                        'message': 'Invalid Data!',
                        'error_message': 'Following fields are required',
                        'fields': [
                            'business_id',
                        ]
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            business = Business.objects.get(
                id=business_id
            )
        except Exception as err:
            return Response(
                {
                    'status': False,
                    'status_code': StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text': 'BUSINESS_NOT_FOUND_4015',
                    'response': {
                        'message': 'Business Doest exist',
                        'error_message': str(err)
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            self.business = business
            # Do everything after this Line self.business is IMP.

        data = {
            'business_info': self.get_business_info_progress(request),
            'business_settings': self.get_business_setting_progress(request),
            'financial_settings': self.get_financial_settings_progress(request),
            'service_management': self.get_business_services_progress(request),
        }

        total_modules = 0
        completed_modules = 0

        for value in data.values():
            total_modules += value['total_modules']
            completed_modules += value['completed_modules']

        percentage_value = (completed_modules / total_modules) * 100

        data['completion_percentage'] = percentage_value

        return Response(
            {
                'status': True,
                'status_code': 200,
                'status_code_text': '200',
                'response': {
                    'message': 'Profile completion progress!',
                    'error_message': None,
                    'data': data
                }
            },
            status=status.HTTP_200_OK
        )


class BusinessTaxSettingView(APIView):
    serializer = BusinessTaxSettingSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        business = Business.objects.get(id=request.query_params.get('business_id'))
        try:
            bu_tax_setting = BusinessTaxSetting.objects.get(
                business=business,
            )
        except:
            bu_tax_setting = BusinessTaxSetting.objects.create(
                business=business,
                user=request.user
            )

        serializer = self.serializer(bu_tax_setting)

        data = {
            'data': serializer.data,
            'choices': self.get_choices()
        }
        return Response(
            {
                'status': True,
                'status_code': 200,
                'status_code_text': '200',
                'response': {
                    'message': 'Created tax setting',
                    'error_message': None,
                    'data': data
                }
            },
            status=status.HTTP_200_OK
        )

    def put(self, request, *args, **kwargs):
        bu_tax_setting = BusinessTaxSetting.objects.get(id=request.data.get('business_tax_id'))
        bu_tax_setting.tax_setting = request.data.get('tax_setting')
        bu_tax_setting.user = request.user
        bu_tax_setting.save()

        serializer = self.serializer(bu_tax_setting)
        data = {
            'data': serializer.data,
            'choices': self.get_choices()
        }

        return Response(
            {
                'status': True,
                'status_code': 200,
                'status_code_text': '200',
                'response': {
                    'message': 'Updated tax setting',
                    'error_message': None,
                    'data': data
                }
            },
            status=status.HTTP_200_OK
        )

    def get_choices(self):
        """
        Get available choices for business tax setting    
        """
        return [item[0] for item in BusinessTaxSetting.SETTING_TYPE]


# """
# Below are the API's for Business Policy
# """


# class BusinessPrivacyCreateView(CreateAPIView):
#     authentication_classes = [IsAuthenticated]
#     queryset = BusinessPrivacy.objects.all()
#     serializer_class = BusinessPolicySerializer


# class BusinessPrivacyListView(ListAPIView):
#     authentication_classes = [IsAuthenticated]
#     queryset = BusinessPrivacy.objects.all()
#     serializer_class = BusinessPolicySerializer


# class BusinessPrivacyUpdateView(UpdateAPIView):
#     authentication_classes = [IsAuthenticated]
#     queryset = BusinessPrivacy.objects.all()
#     serializer_class = BusinessPolicySerializer


# class BusinessPrivacyRetreiveView(RetrieveAPIView):
#     authentication_classes = [IsAuthenticated]
#     queryset = BusinessPrivacy.objects.all()
#     serializer_class = BusinessPolicySerializer


# class BusinessPrivacyDestroyView(DestroyAPIView):
#     authentication_classes = [IsAuthenticated]
#     queryset = BusinessPrivacy.objects.all()
#     serializer_class = BusinessPolicySerializer


# """
# Below are the API's for Business Policy
# """


# class BusinessPolicyCreateView(CreateAPIView):
#     authentication_classes = [IsAuthenticated]
#     queryset = BusinessPolicy.objects.all()
#     serializer_class = BusinessPolicy.objects.all()


# class BusinessPolicyListView(ListAPIView):
#     authentication_classes = [IsAuthenticated]
#     queryset = BusinessPolicy.objects.all()
#     serializer_class = BusinessPolicy.objects.all()


# class BusinessPolicyUpdateView(UpdateAPIView):
#     authentication_classes = [IsAuthenticated]
#     queryset = BusinessPolicy.objects.all()
#     serializer_class = BusinessPolicy.objects.all()


# class BusinessPolicyRetreiveView(RetrieveAPIView):
#     authentication_classes = [IsAuthenticated]
#     queryset = BusinessPolicy.objects.all()
#     serializer_class = BusinessPolicy.objects.all()


# class BusinessPolicyDestroyView(DestroyAPIView):
#     authentication_classes = [IsAuthenticated]
#     queryset = BusinessPolicy.objects.all()
#     serializer_class = BusinessPolicy.objects.all()


# class BusinessPolicyViewSet(viewsets.ModelViewSet):
#     authentication_classes = [AllowAny]
#     queryset = BusinessPolicy.objects.all()
#     serializer_class = BusinessPolicySerializer