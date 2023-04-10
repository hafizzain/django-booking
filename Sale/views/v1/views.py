from datetime import timedelta
from threading import Thread
from django.shortcuts import render
from Sale.Constants.StaffEmail import StaffSaleEmail
from Sale.Constants.stock_lowest import stock_lowest
from Sale.Constants.tunrover import ProductTurnover

from rest_framework import status
from Appointment.models import Appointment, AppointmentCheckout, AppointmentService
from Business.models import AdminNotificationSetting, Business, StaffNotificationSetting, StockNotificationSetting
from Client.models import Client, Membership, Vouchers
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

from Employee.models import CategoryCommission, CommissionSchemeSetting, Employee, EmployeeSelectedService
from Business.models import BusinessAddress
from Service.models import PriceService, Service, ServiceGroup

from Product.models import Product, ProductOrderStockReport, ProductStock
from django.db.models import Avg, Count, Min, Sum


from Sale.serializers import AppointmentCheckoutSerializer, BusinessAddressSerializer, CheckoutSerializer, MemberShipOrderSerializer, ProductOrderSerializer, ServiceGroupSerializer, ServiceOrderSerializer, ServiceSerializer, VoucherOrderSerializer
from rest_framework.pagination import PageNumberPagination


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_my_apply_on_jobs(request):
#     try:
#         profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
#     except Exception as e:
#         return Response({"success": False, 'response': {'message': str(e)}},
#                         status=status.HTTP_404_NOT_FOUND)

#     apply_jobs = list(JobApply.objects.filter(profile=profile, is_deleted=False).values_list('job__id', flat=True))

#     jobapply = Job.objects.filter(id__in=apply_jobs, is_deleted=False)
#     paginator = CustomPagination()
#     paginator.page_size = 10
#     result_page = paginator.paginate_queryset(jobapply, request)
#     serializer = GetJobSerializer(result_page, many=True)
#     return paginator.get_paginated_response(serializer.data)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_service(request):
    title = request.GET.get('title', None)
    # SORTED_OPTIONS = {
    #     'default' : '-created_at',
    #     'title': title
    # }
    # sorted_value = SORTED_OPTIONS.get(title, '-created_at')
    if title:
        service= Service.objects.filter(name__icontains = title , is_deleted=False, is_blocked=False).order_by('-created_at').distinct()
        serialized = ServiceSerializer(service,  many=True, context={'request' : request} )
    else:
        service= Service.objects.filter( is_deleted=False, is_blocked=False).order_by('-created_at').distinct()
        serialized = ServiceSerializer(service,  many=True, context={'request' : request} )
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Service',
                'error_message' : None,
                'service' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_service(request):
    user = request.user
    business = request.data.get('business', None)
    
    name = request.data.get('name', None)
    staffgroup_id = request.data.get('staffgroup_id',None)
    service = request.data.get('service', None)
    
    description = request.data.get('description',None)
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
    
    if not all([business, name, description ]):
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
                          'employee',
                          'name', 
                          'description'
                            ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business_id=Business.objects.get(id=business)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Business not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # try:
    #     location=BusinessAddress.objects.get(id=location_id)
    # except Exception as err:
    #         return Response(
    #             {
    #                 'status' : False,
    #                 'status_code' : StatusCodes.LOCATION_NOT_FOUND_4017,
    #                 'response' : {
    #                 'message' : 'Location not found',
    #                 'error_message' : str(err),
    #             }
    #             }
    #         )
    
    
    service_obj = Service.objects.create(
        user = user,
        business =business_id,
        name = name,
        description = description,
        service_availible = service_availible,
        #location=location,
        #service_type = treatment_type,
        controls_time_slot=controls_time_slot,
        initial_deposit=initial_deposit,
        client_can_book=client_can_book,
        slot_availible_for_online=slot_availible_for_online,
        
        #enable_team_comissions =enable_team_comissions,
        enable_vouchers=enable_vouchers,
        
    )
    if enable_team_comissions is not None:
        service_obj.enable_team_comissions = True
    else:
        service_obj.enable_team_comissions = False
        
    service_obj.save()
    
    employees_error = []
    if is_package is not None:
        service_obj.is_package = True
        #service_obj.service_type = treatment_type
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
                    service_id=Service.objects.get(id=ser)
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
                service = service_obj,
                employee = employe
                )
            #service_obj.employee.add(employe)
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
        service_group = ServiceGroup.objects.get(id = staffgroup_id)
        service_group.services.add(service_obj)
        service_group.save()

    except Exception as err:
        employees_error.append(str(err))  
          
    if priceservice is not None:
        if type(priceservice) == str:
            priceservice = priceservice.replace("'" , '"')
            priceservice = json.loads(priceservice)
        else:
            pass
        for ser in priceservice:
            try:
                duration = ser['duration']
                price = ser['price']
                currency = ser['currency']
                
                try:
                    currency_id = Currency.objects.get(id = currency)
                except Exception as err:
                    pass
                
                price_service = PriceService.objects.create(
                    service = service_obj ,
                    currency = currency_id,
                    duration = duration,
                    price = price,
                )
            except Exception as err:
                employees_error.append(str(err))
        
    
    service_serializers= ServiceSerializer(service_obj, context={'request' : request})
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Service Created Successfully!',
                    'error_message' : None,
                    'employee_error' : employees_error,
                    'service' : service_serializers.data,
                    
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
        service = Service.objects.get(id=service_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Service ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    service.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Service deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_service(request):
    id = request.data.get('id', None)
    priceservice = request.data.get('priceservice', None)
    staffgroup_id = request.data.get('staffgroup_id',None)
    
    employeeslist=request.data.get('employee', None)
    service=request.data.get('service', None)
    location=request.data.get('location', None)
    
    if id is None: 
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.MISSING_FIELDS_4001,
            'status_code_text' : 'MISSING_FIELDS_4001',
            'response' : {
                'message' : 'Invalid Data!',
                'error_message' : 'Service ID are required.',
                'fields' : [
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
                'status' : False,
                'status_code_text' : 'INVALID_SERVICE_ID',
                'response' : {
                    'message' : 'Service Not Found',
                    'error_message' : str(err),
                }
            },
                status=status.HTTP_404_NOT_FOUND
        )
        
    error = []
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
                error.append(str(err))
    
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
                error.append(str(err))
    
    if employeeslist is not None:
        if type(employeeslist) == str:
            employeeslist = json.loads(employeeslist)
        elif type(employeeslist) == list:
            pass
        all_pending_services = EmployeeSelectedService.objects.filter(service=service_id).exclude(employee__in=employeeslist)
        for empl_service in all_pending_services:
            empl_service.delete()
            
        for empl_id in employeeslist:
            try:
                employe = Employee.objects.get(id=empl_id)
                employe_service, created = EmployeeSelectedService.objects.get_or_create(
                    service = service_id,
                    employee = employe
                )
                    
                #service_id.employee.add(employe)
            except Exception as err:
                error.append(str(err))
    try:
        print(staffgroup_id)
        all_prev_ser_grops = ServiceGroup.objects.filter(services=service_id)
        for i in all_prev_ser_grops:
            i.services.remove(service_id)
            i.save()

        service_group = ServiceGroup.objects.get(id = staffgroup_id)
        service_group.services.add(service_id)
        service_group.save()

    except Exception as err:
        error.append(str(err)) 
    
    
    if priceservice is not None:
        if type(priceservice) == str:
            priceservice = priceservice.replace("'" , '"')
            priceservice = json.loads(priceservice)
        else:
            pass
        for ser in priceservice:
            s_service_id = ser.get('id', None)
            duration = ser.get('duration', None)
            price = ser.get('price', None)
            currency = ser.get('currency', None)
            is_deleted = ser.get('is_deleted', None)
            try:
                currency_id = Currency.objects.get(id = currency)
            except Exception as err:
                pass
                
            if s_service_id is not None:
                try: 
                    price_service = PriceService.objects.get(id=ser['id'])
                    
                    if bool(is_deleted) == True:
                        price_service.delete()
                        continue
                    servic = Service.objects.get(id=ser['service'])
                    price_service.service = servic
                    price_service.duration = ser['duration']
                    price_service.price = ser['price']
                    price_service.currency = currency_id
                    price_service.save()
                    
                except Exception as err:
                    error.append(str(err))
                    print(err)
            else:
                if bool(is_deleted) == True:
                    pass
                else:
                    ser = Service.objects.get(id=id)
                    PriceService.objects.create(
                        service=ser,
                        duration = duration,
                        price=price,
                        currency = currency_id
                    )

    serializer= ServiceSerializer(service_id, context={'request' : request} , data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : ' Service updated successfully',
                    'error_message' : None,
                    'error': error,
                    'service' : serializer.data
                
                }
            },
            status=status.HTTP_200_OK
           )
    
    else: 
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
                'response' : {
                    'message' : 'Invialid Data',
                    'error_message' : str(serializer.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
   
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_servicegroup(request):
    user = request.user
    
    business = request.data.get('business', None)
    name = request.data.get('name', None)
    service = request.data.get('service', None)
    is_status = request.data.get('status', None)
    allow_client_to_select_team_member = request.data.get('allow_client_to_select_team_member', None)
    
    servicegroup_error = []
    if not all([business, name]):
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
                          'name',
                          'service'
                          
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business_id=Business.objects.get(id=business)
    except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Business not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    service_group = ServiceGroup.objects.create(
        user = user,
        business = business_id,
        name = name,
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
    serialized=ServiceGroupSerializer(service_group, context={'request' : request})
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Service Group Created!',
                    'error_message' : None,
                    'service_group' : serialized.data,
                    'servicegroup_errors' : servicegroup_error,
                }
            },
            status=status.HTTP_201_CREATED
        )
 
@api_view(['GET'])
@permission_classes([AllowAny])
def get_servicegroup(request):
    service_group = ServiceGroup.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = ServiceGroupSerializer(service_group,  many=True, context={'request' : request})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Service Group',
                'error_message' : None,
                'sales' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
     
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_servicegroup(request):
    service_id = request.data.get('id', None)
    if id is None: 
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
        service = ServiceGroup.objects.get(id=service_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Service ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    service.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'ServiceGroup deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
       
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_servicegroup(request):
    error = []
    service=request.data.get('service', None)
    id = request.data.get('id', None)
    
    is_status = request.data.get('status', None)
    allow_client_to_select_team_member = request.data.get('allow_client_to_select_team_member', None)
    
    if id is None: 
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.MISSING_FIELDS_4001,
            'status_code_text' : 'MISSING_FIELDS_4001',
            'response' : {
                'message' : 'Invalid Data!',
                'error_message' : 'Service ID are required.',
                'fields' : [
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
                'status' : False,
                'status_code_text' : 'INVALID_SERVICE_ID',
                'response' : {
                    'message' : 'ServiceGroup Not Found',
                    'error_message' : str(err),
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
    
    serializer= ServiceGroupSerializer(service_id, context={'request' : request} , data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : ' ServiceGroup updated successfully',
                    'error_message' : None,
                    'error': error,
                    'service' : serializer.data
                
                }
            },
            status=status.HTTP_200_OK
           )
    
    else: 
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
                'response' : {
                    'message' : 'Invalid Data',
                    'error_message' : str(serializer.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    # #pagination
    
    # paginator = CustomPagination()
    # paginator.page_size = 1
    # result_page = paginator.paginate_queryset(product_order, request)
    # serialized = ProductOrderSerializer(result_page,  many=True)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_sale_orders(request):
    
    
    data=[]
    checkout_order = Checkout.objects.filter(is_deleted=False)#.order_by('-created_at')
    serialized = CheckoutSerializer(checkout_order,  many=True, context={'request' : request})
    data.extend(serialized.data)
   
    
    appointment_checkout = AppointmentCheckout.objects.filter(appointment_service__appointment_status = 'Done')#.order_by('-created_at')
    serialized = AppointmentCheckoutSerializer(appointment_checkout, 
                                               many = True, 
                                               context={'request' : request
                            })
    data.extend(serialized.data)
    
    sorted_data = sorted(data, key=lambda x: x['created_at'], reverse=True)
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Sale Orders',
                'error_message' : None,
                'sales' : sorted_data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_sale_orders_pagination(request):
    location_id = request.GET.get('location', None)
    paginator = CustomPagination()
    paginator.page_size = 10
    
    checkout_order = Checkout.objects.filter(
        is_deleted=False,
        location__id = location_id,
        )
    
    #paginated_checkout_order = paginator.paginate_queryset(checkout_order, request)
    checkout_data = CheckoutSerializer(checkout_order, many=True, context={'request': request}).data
    
    appointment_checkout = AppointmentCheckout.objects.filter(
        appointment_service__appointment_status='Done',
        location__id = location_id,
        )
    #paginated_appointment_checkout = paginator.paginate_queryset(appointment_checkout, request)
    appointment_checkout_data = AppointmentCheckoutSerializer(appointment_checkout, many=True, context={'request': request}).data
    
    data_total = checkout_data + appointment_checkout_data
    
    paginated_appointment_checkout = paginator.paginate_queryset(data_total, request)
    
    sorted_data = sorted(paginated_appointment_checkout, key=lambda x: x['created_at'], reverse=True)
    
    return paginator.get_paginated_response(sorted_data, 'sales')
    
    # sale_data = paginator.get_paginated_response(sorted_data, 'sales')

    # return Response(
    #     {
    #         'status' : 200,
    #         'status_code' : '200',
    #         'response' : {
    #             'message' : 'All Sale Orders',
    #             'error_message' : None,
    #             'sales' : sale_data.data
    #         }
    #     },
    #     status=status.HTTP_200_OK
    # )
    

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
    appointment_checkout_data = AppointmentCheckoutSerializer(paginated_appointment_checkout, many=True, context={'request': request}).data
    
    data = checkout_data + appointment_checkout_data
    sorted_data = sorted(data, key=lambda x: x['created_at'], reverse=True)
    
    return paginator.get_paginated_response(sorted_data)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_orders(request):
    product_order = ProductOrder.objects.filter(is_deleted=False).order_by('-created_at')
    
    serialized = ProductOrderSerializer(product_order,  many=True,  context={'request' : request, })
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Product Orders',
                'error_message' : None,
                'orders' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_membership_orders(request):
    membership_order = MemberShipOrder.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = MemberShipOrderSerializer(membership_order,  many=True, context={'request' : request, })
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Membership Orders',
                'error_message' : None,
                'orders' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_service_orders(request):
    service_orders = ServiceOrder.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = ServiceOrderSerializer(service_orders,  many=True, context={'request' : request, })
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Service Orders',
                'error_message' : None,
                'orders' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_voucher_orders(request):
    voucher_orders = VoucherOrder.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = VoucherOrderSerializer(voucher_orders,  many=True, context={'request' : request, })
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Voucher Orders',
                'error_message' : None,
                'orders' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_total_revenue(request):
    data = {  
    'appointments_jan' : 0,
    'appointments_feb' : 0,
    'appointments_mar' : 0,
    'appointments_apr' : 0,
    'appointments_may' : 0,
    'appointments_jun' : 0,
    'appointments_july' : 0,
    'appointments_aug' : 0,
    'appointments_sep' : 0,
    'appointments_oct' : 0,
    'appointments_nov' : 0,
    'appointments_dec' : 0,
    
    'sale_jan' : 0,
    'sale_feb' : 0,
    'sale_mar' : 0,
    'sale_apr' : 0,
    'sale_may' : 0,
    'sale_jun' : 0,
    'sale_july' : 0,
    'sale_aug' : 0,
    'sale_sep' : 0,
    'sale_oct' : 0,
    'sale_nov' : 0,
    'sale_dec' : 0,
    }
    appointment = AppointmentCheckout.objects.filter(appointment_service__appointment_status = 'Paid')
    for ind, value in enumerate(appointment):
        create_at = str(value.created_at)
        
        matching = int(create_at.split(" ")[0].split("-")[1])
        if( matching == 0 ):
            
            data['appointments_jan'] +=1
            MONTHS[0]['appointments'] = data['appointments_jan']
            
        if( matching == 1 ):
            
            data['appointments_feb'] +=1
            MONTHS[1]['appointments'] = data['appointments_feb']
            
        if( matching == 2 ):
           
            data['appointments_mar'] +=1
            MONTHS[2]['appointments'] = data['appointments_mar']
            
        if( matching == 3 ):
            
            data['appointments_apr'] +=1
            MONTHS[3]['appointments'] = data['appointments_apr']
            
        if( matching == 4 ):
            
            data['appointments_may'] +=1
            MONTHS[4]['appointments'] = data['appointments_may']
            
        if( matching == 5 ):
            
            data['appointments_jun'] +=1
            MONTHS[5]['appointments'] = data['appointments_jun']
        if( matching == 6 ):
            
            data['appointments_july'] +=1
            MONTHS[6]['appointments'] = data['appointments_july']
            
        if( matching == 7 ):
            
            data['appointments_aug'] +=1
            MONTHS[7]['appointments'] = data['appointments_aug']
        if( matching == 8 ):
            
            data['appointments_sep'] +=1
            MONTHS[8]['appointments'] = data['appointments_sep']
        if( matching == 9 ):
            
            data['appointments_oct'] +=1
            MONTHS[9]['appointments'] = data['appointments_oct']
        if( matching == 10 ):
            
            data['appointments_nov'] +=1
            MONTHS[10]['appointments'] = data['appointments_nov']
        if( matching == 11 ):
            
            data['appointments_dec'] +=1
            MONTHS[11]['appointments'] = data['appointments_dec']
               
    orders = Order.objects.filter(is_deleted=False)
    for order in orders:
        create_at = str(order.created_at)
        
        matching = int(create_at.split(" ")[0].split("-")[1])
        if( matching == 0 ):
            
            data['sale_jan'] +=1
            MONTHS[0]['sales'] = data['sale_jan']
            
        if( matching == 1 ):
            
            data['sale_feb'] +=1
            MONTHS[1]['sales'] = data['sale_feb']
            
        if( matching == 2 ):
           
            data['sale_mar'] +=1
            MONTHS[2]['sales'] = data['sale_mar']
            
        if( matching == 3 ):
            
            data['sale_apr'] +=1
            MONTHS[3]['sales'] = data['sale_apr']
            
        if( matching == 4 ):
            
            data['sale_may'] +=1
            MONTHS[4]['sales'] = data['sale_may']
            
        if( matching == 5 ):
            
            data['sale_jun'] +=1
            MONTHS[5]['sales'] = data['sale_jun']
        if( matching == 6 ):
            
            data['sale_july'] +=1
            MONTHS[6]['sales'] = data['sale_july']
            
        if( matching == 7 ):
            
            data['sale_aug'] +=1
            MONTHS[7]['sales'] = data['sale_aug']
        if( matching == 8 ):
            
            data['sale_sep'] +=1
            MONTHS[8]['sales'] = data['sale_sep']
        if( matching == 9 ):
            
            data['sale_oct'] +=1
            MONTHS[9]['sales'] = data['sale_oct']
        if( matching == 10 ):
            
            data['sale_nov'] +=1
            MONTHS[10]['sales'] = data['sale_nov']
        if( matching == 11 ):
            
            data['sale_dec'] +=1
            MONTHS[11]['sales'] = data['sale_dec']
        
            
            # if value.total_price is not None:
            #     print('test')
            #     total += value.total_price
            # MONTHS[10]['price'] = total
            
        
        # data[ind] = {}
        # data[ind]['value'] = value

        # for app in appointment:
        
        #     create_at = str(app.created_at)
        #     if (create_at.split(" ")[0] == date ):
        #         appointments_count +=1
        #         if app.total_price is not None:
        #             total_revenue += app.total_price
    total = 0
    appointmemnt_sale = 0
    order_sale = 0
    orders_price = Order.objects.filter(is_deleted=False)
    for order in orders_price:
        order_sale +=1
        if order.total_price is not  None:
            total += order.total_price
    #orders_price = Order.objects.aggregate(Total= Sum('total_price'))
    
    price = AppointmentCheckout.objects.filter(appointment_service__appointment_status = 'Paid', )#appointment_service__appointment_status = 'Done')
    for order in price:
        appointmemnt_sale +=1
        if order.total_price is not None:
            total += order.total_price
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Total Revenue',
                'error_message' : None,
                'revenue' : total,
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
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
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
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Business Location Not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    serialized = BusinessAddressSerializer(location, context = {'request' : request, })
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'All Business Tax!',
                    'error_message' : None,
                    'tax' : serialized.data
                }
            },
            status=status.HTTP_201_CREATED
        )
    
        
        

@api_view(['GET'])
@permission_classes([AllowAny])
def get_sale_checkout(request): 
    checkout =Checkout.objects.all()
    serialized = CheckoutSerializer(checkout, many = True, context = {'request' : request, })
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Product Order Sale Created!',
                    'error_message' : None,
                    'sale' : serialized.data
                }
            },
            status=status.HTTP_201_CREATED
        )
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_sale_order(request):
    user = request.user
    
    sale_type = request.data.get('selection_type', None)
    client_id = request.data.get('client', None)
    sale_status = request.data.get('status', None)
    member_id = request.data.get('member', None)
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
    duration = request.data.get('duration', None)
    
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
     
    tip = request.data.get('tip', 0)
    total_price = request.data.get('total_price', None)
    minus_price = 0
    
    errors = []
    
    if not all([member_id , client_type, location_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                          'member', 
                          'selection_type',
                          'location'
                            ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        client = Client.objects.get(id = client_id)
    except Exception as err:
        client =  None
                
    try:
        member=Employee.objects.get(id = member_id)
    except Exception as err:
        return Response(
            {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
                    'response' : {
                    'message' : 'Employee not found',
                    'error_message' : str(err),
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
        
    # service_total_price = int(float(service_total_price))
    # product_total_price = int(float(product_total_price))
    # voucher_total_price = int(float(voucher_total_price))
    
    checkout = Checkout.objects.create(
        user = user,
        
        client = client, 
        location = business_address,
        member = member ,
        client_type = client_type,
        payment_type = payment_type,
        
        # service_commission = service_commission,
        # product_commission = product_commission,
        # voucher_commission = voucher_commission,   
        
        total_voucher_price = voucher_total_price,
        total_service_price = service_total_price,
        total_product_price = product_total_price,
        
        service_commission_type = service_commission_type,
        product_commission_type = product_commission_type,
        voucher_commission_type = voucher_commission_type ,  
        
        tip = tip,
    )
    if bool(is_promotion) == True:
        checkout.is_promotion = True
        checkout.save()
        
    # ExceptionRecord.objects.create(
    #             text = f' is_promotion condition {bool(is_promotion) == True} is_promotion {is_promotion}'
    #         )
    test = True
    
    if bool(is_promotion_availed) == True:
        for item in ids:
            price = item["price"]
            minus_price +=(price)
            #print(price)
        
    for id in ids:          
        sale_type = id['selection_type']
        service_id = id['id']
        quantity = id['quantity']
        price = id['price']        
        discount_price = id.get('discount_price', None)
        
        if discount_price is not None:
            price = int(discount_price) #* int(quantity)
        
        # if price > 0 and bool(is_promotion_availed) == True:
        #     minus_price += price
        #     ExceptionRecord.objects.create(
        #         text = f'price {price > 0} minus_price {minus_price}'
        #     )
        
        if price == 0 and bool(is_promotion_availed) == True:
            number = int(float(total_price))
            rem_price = number - minus_price
            price =  int(rem_price) / int(free_services_quantity)
            
            if test == True:
                checkout.total_service_price = int(float(total_price))
                checkout.save()
                test = False
                
        if sale_type == 'PRODUCT':
            try:
                product = Product.objects.get(id = service_id)
            except Exception as err:
                return Response(
                    {
                        'status' : False,
                        'status_code' : StatusCodes.PRODUCT_NOT_FOUND_4037,
                        'response' : {
                        'message' : 'Something Went Wrong',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
                
            try:
                transfer = ProductStock.objects.get(product__id=product.id, location = business_address.id)
                
                if transfer.available_quantity >= int(quantity):
                    stock_transfer = ProductOrderStockReport.objects.create(
                    report_choice = 'Sold',
                    product = product,
                    user = request.user,
                    location = business_address,
                    #quantity = int(quantity), 
                    before_quantity = transfer.available_quantity      
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
                admin_email = StockNotificationSetting.objects.get(business = str(business_address.business))
                if admin_email.notify_stock_turnover == True and transfer.available_quantity <= 5:
                    try:
                        thrd = Thread(target=ProductTurnover, args=[], kwargs={'product' : product,'product_stock': transfer, 'business_address':business_address.id ,'tenant' : request.tenant})
                        thrd.start()
                    except Exception as err:
                        ExceptionRecord.objects.create(
                            text = f' error in Turnover email sale{str(err)}'
                        )
            except:
                pass
            
            try:
                admin_email = StockNotificationSetting.objects.get(business = str(business_address.business))
                if admin_email.notify_for_lowest_stock == True and transfer.available_quantity <= 5:
                    try:
                        thrd = Thread(target=stock_lowest, args=[], kwargs={'product' : product,'product_stock': transfer, 'business_address':business_address.id ,'tenant' : request.tenant,'quantity': transfer.available_quantity})
                        thrd.start()
                    except Exception as err:
                        ExceptionRecord.objects.create(
                            text = f' error in Stock lowest email sale{str(err)}'
                        )
            except:
                pass
            

            product_order = ProductOrder.objects.create(
                user = user,
                client = client,
                product = product,
                #status = sale_status,
                checkout = checkout,
                member = member,
                location = business_address,
                tip = tip,
                total_price = total_price, 
                payment_type= payment_type,
                client_type = client_type,
                quantity = quantity,
                current_price = price,
            )
            product_order.sold_quantity += 1 # product_stock.sold_quantity
            product_order.save()
            checkout.product_commission = product_commission
            checkout.save()

        elif sale_type == 'SERVICE':
            try:
                service = Service.objects.get(id = service_id)
                service_price = PriceService.objects.filter(service = service_id).first()
                dur = service_price.duration
                # ExceptionRecord.objects.create(
                #     text = f'price {price} discount_price {discount_price}'
                # )
                
                service_order = ServiceOrder.objects.create(
                    user = user,
                    service = service,
                    duration= dur,
                    checkout = checkout,
                    
                    client = client,
                    member = member,
                    location = business_address,
                    tip = tip,
                    total_price = total_price, 
                    payment_type=payment_type,
                    client_type = client_type,
                    quantity = quantity,
                    current_price = price,
                    
                )
                checkout.service_commission = service_commission
                checkout.save()
            except Exception as err:
                return Response(
                    {
                        'status' : False,
                        'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
                        'response' : {
                        'message' : 'Service not found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        elif sale_type == 'MEMBERSHIP':
            try:
                membership = Membership.objects.get(id = service_id)
                validity = int(membership.valid_for.split(" ")[0])
                end_date_cal = membership.created_at +  timedelta(days= validity)
                start_date_cal = membership.created_at
                
                membership_order = MemberShipOrder.objects.create(
                    user= user,
                    
                    membership = membership,
                    start_date = start_date_cal,
                    end_date = end_date_cal,
                    #status = sale_status,
                    checkout = checkout,
                    client = client,
                    member = member,
                    tip = tip,
                    total_price = total_price, 
                    payment_type =payment_type,
                    client_type = client_type,
                    quantity = quantity,
                    location = business_address,
                    current_price = price,
                )
            except Exception as err:
                return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_MEMBERSHIP_ID_4040,
                    'response' : {
                    'message' : 'Membership not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
            
        elif sale_type == 'VOUCHER':  
              
            #for vouchers in ids:  
            try:
                days = 0
                voucher = Vouchers.objects.get(id = service_id)#str(vouchers))
                test = voucher.validity.split(" ")[1]
                
                if test == 'Days':
                    day = voucher.validity.split(" ")[0]
                    day = int(day)
                    days = day  
                    
                elif test == 'Months':
                    day = voucher.validity.split(" ")[0]
                    data = int(day)
                    days = data *  30
                    
                                        
                elif test == 'Years':
                    day = voucher.validity.split(" ")[0]
                    day = int(day)
                    days = day * 360
                print(days)
                end_date_cal = voucher.created_at +  timedelta(days=days)
                start_date_cal = voucher.created_at
                
                voucher_order =VoucherOrder.objects.create(
                    user = user,
                    
                    voucher = voucher,
                    start_date = start_date_cal,
                    end_date = end_date_cal,
                    #status = sale_status,
                    checkout = checkout,
                    client = client,
                    member = member,
                    tip = tip,
                    total_price = total_price, 
                    payment_type =payment_type,
                    client_type = client_type,
                    quantity = quantity,
                    location = business_address,
                    current_price = price,

                )
                checkout.voucher_commission = voucher_commission
                checkout.save()
            except Exception as err:
                return Response(
                    {
                        'status' : False,
                        'status_code' : StatusCodes.INVALID_VOUCHER_ID_4041,
                        'response' : {
                        'message' : 'Voucher not found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    try:
        thrd = Thread(target=StaffSaleEmail, args=[], kwargs={'ids' : ids, 'location': business_address.address_name ,'tenant' : request.tenant, 'member': member, 'invoice': checkout.id, 'client': client})
        thrd.start()
    except Exception as err:
        ExceptionRecord.objects.create(
                text = f' error in email sale{str(err)}'
            )
    
    serialized = CheckoutSerializer(checkout, context = {'request' : request, })
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Product Order Sale Created!',
                    'error_message' : errors,
                    'sale' : serialized.data,
                }
            },
            status=status.HTTP_201_CREATED
        )