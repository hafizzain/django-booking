import imp
import re
from django.shortcuts import render

from rest_framework import status
from Business.models import Business
from Client.models import Client, Membership, Vouchers
from Order.models import MemberShipOrder, ProductOrder, ServiceOrder, VoucherOrder
from Utility.models import Country, State, City
from Authentication.models import User
from NStyle.Constants import StatusCodes
import json

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from Employee.models import Employee, EmployeeSelectedService
from Business.models import BusinessAddress
from Service.models import Service

from Product.models import Product

from Sale.serializers import MemberShipOrderSerializer, ProductOrderSerializer, ServiceOrderSerializer, ServiceSerializer, VoucherOrderSerializer



@api_view(['GET'])
@permission_classes([AllowAny])
def get_service(request):
    service= Service.objects.filter(is_deleted=False, is_blocked=False).order_by('-created_at')
    serialized = ServiceSerializer(service,  many=True, )
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
    treatment_type = request.data.get('treatment_type',None)
    service = request.data.get('service', None)
    
    description = request.data.get('description',None)
    employee = request.data.get('employee', None)
    location_id = request.data.get('location', None)
    
    price = request.data.get('price', None)
    duration = request.data.get('duration', None)
    
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
        #location=location,
        price=price,
        duration=duration,
        
        controls_time_slot=controls_time_slot,
        initial_deposit=initial_deposit,
        client_can_book=client_can_book,
        slot_availible_for_online=slot_availible_for_online,
        
        enable_team_comissions =enable_team_comissions,
        enable_vouchers=enable_vouchers,
        
    )
    employees_error = []
    if is_package is not None:
        service_obj.is_package = True
        service_obj.service_type = treatment_type
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
                service_obj.employee.add(employe)
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
    
    
    
    
    
    payroll_serializers= ServiceSerializer(service_obj)
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Service Created Successfully!',
                    'error_message' : None,
                    'employee_error' : employees_error,
                    'service' : payroll_serializers.data,
                    
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
    
    employeeslist=request.data.get('employee', None)
    service=request.data.get('service', None)
    location=request.data.get('location', None)
    
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
                
    # try:
    #             test = '1689071a-1ddc-4191-95d5-16e16f2b2188'
    #             employe = Employee.objects.get(id=test)
    #             service_id.employee.add(employe)
    # except Exception as err:
    #             error.append(str(err))
    
    
    if employeeslist is not None:
        if type(employeeslist) == str:
            employeeslist = json.loads(employeeslist)
        elif type(employeeslist) == list:
            pass
        print(type(employeeslist))
        service_id.employee.clear()
        all_pending_services = EmployeeSelectedService.objects.filter(service=service_id).exclude(employee__in=employeeslist)
        for empl_service in all_pending_services:
            empl_service.delete()
            
        for empl_id in employeeslist:
            try:
                employe = Employee.objects.get(id=usr)
                employe_service, created = EmployeeSelectedService.objects.get_or_create(
                    service = service_id,
                    employee = employe
                )
                    
                service_id.employee.add(employe)
            except Exception as err:
                error.append(str(err))
    service_id.save()
    
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
        
        
@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_orders(request):
    product_order = ProductOrder.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = ProductOrderSerializer(product_order,  many=True)
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
    serialized = MemberShipOrderSerializer(membership_order,  many=True)
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
    serialized = ServiceOrderSerializer(service_orders,  many=True)
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
    serialized = VoucherOrderSerializer(voucher_orders,  many=True)
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
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_sale_order(request):
    user = request.user
    
    sale_type = request.data.get('sale_type', None)
    client_id = request.data.get('client', None)
    sale_status = request.data.get('status', None)
    member_id = request.data.get('member', None)
    location_id = request.data.get('location', None)
    payment_type = request.data.get('payment_type', None)
    client_type = request.data.get('client_type', None)
    
    product_id = request.data.get('product', None)
    
    #Order Service
    service_id = request.data.get('service', None)
    duration = request.data.get('duration', None)
    
    #Order Membership
    membership_id = request.data.get('membership', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    
    #Order Voucher
    voucher_id = request.data.get('voucher', None)
     
    tip = request.data.get('tip', None)
    total_price = request.data.get('total_price', None)
    
    errors = []
    
    if not all([client_id, member_id ]):
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
                          'member', 
                            ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        client = Client.objects.get(id = client_id)
    except Exception as err:
        return Response(
            {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_CLIENT_4032,
                    'response' : {
                    'message' : 'Client not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        
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
        # return Response(
        #     {
        #             'status' : False,
        #             # 'error_message' : str(err),
        #             'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
        #             'response' : {
        #             'message' : 'Business not found',
        #         }
        #     },
        #     status=status.HTTP_400_BAD_REQUEST
        # )
    if sale_type == 'PRODUCT':
        
        if type(product_id) == str:
            product_id = json.loads(product_id)

        elif type(product_id) == list:
            pass
        
        for pro in product_id:
        
            try:
                product = Product.objects.get(id = pro)
                product_stock = product.product_stock.all().first()
                print(product_stock)
                if product_stock.available_quantity == 0:
                    return Response(
                    {
                        'status' : False,
                        #'status_code' : StatusCodes.PRODUCT_NOT_FOUND_4037,
                        'response' : {
                        'message' : 'product_stock  not Avaiable',
                        'error_message' : "available_quantity",
                        }
                    },
                status=status.HTTP_400_BAD_REQUEST
                )
                    
                product_stock.available_quantity -=1
                    
                product_stock.sold_quantity += 1
                print(product_stock)
                product_stock.save()
                product_order = ProductOrder.objects.create(
                    user = user,
                    client = client,
                    product = product,
                    status = sale_status,
                    member = member,
                    location = business_address,
                    tip = tip,
                    total_price = total_price, 
                    payment_type= payment_type,
                    client_type = client_type,
                    
                    
                )
            except Exception as err:
                return Response(
                    {
                        'status' : False,
                        'status_code' : StatusCodes.PRODUCT_NOT_FOUND_4037,
                        'response' : {
                        'message' : 'Product not found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serialized = ProductOrderSerializer(product_order)
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
    
    elif sale_type == 'SERVICE':
        
        if type(service_id) == str:
            service_id = json.loads(service_id)

        elif type(service_id) == list:
            pass
        
        for servics in service_id:
            try:
                service = Service.objects.get(id = servics)
                service_order = ServiceOrder.objects.create(
                    user = user,
                    service = service,
                    duration= duration,
                    
                    client = client,
                    member = member,
                    location = business_address,
                    tip = tip,
                    total_price = total_price, 
                    payment_type=payment_type,
                    client_type = client_type

                    
                )
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
        
        serialized = ServiceOrderSerializer(service_order)
        return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Service Order Sale Created!',
                    'error_message' : None,
                    'sale' : serialized.data
                }
            },
            status=status.HTTP_201_CREATED
        )
        
    elif sale_type == 'MEMBERSHIP':
        if type(membership_id) == str:
            membership_id = json.loads(membership_id)

        elif type(membership_id) == list:
            pass
        
        for membership in membership_id:
            try:
                membership = Membership.objects.get(id = membership)
                membership_order = MemberShipOrder.objects.create(
                    user= user,
                    
                    membership = membership,
                    start_date = start_date,
                    end_date = end_date,
                    status = sale_status,
                    
                    client = client,
                    member = member,
                    tip = tip,
                    total_price = total_price, 
                    payment_type =payment_type,
                    client_type = client_type

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
            
        
        serialized = MemberShipOrderSerializer(membership_order)
        return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Membership Order Sale Created!',
                    'error_message' : None,
                    'sale' : serialized.data
                }
            },
            status=status.HTTP_201_CREATED
        )
        
    elif sale_type == 'VOUCHER':
        
        if type(voucher_id) == str:
            voucher_id = json.loads(voucher_id)

        elif type(voucher_id) == list:
            pass
        
        for vouchers in voucher_id:  
            try:
                voucher = Vouchers.objects.get(id = vouchers)
                voucher_order =VoucherOrder.objects.create(
                    user = user,
                    
                    voucher = voucher,
                    start_date = start_date,
                    end_date = end_date,
                    status = sale_status,
                    
                    client = client,
                    member = member,
                    tip = tip,
                    total_price = total_price, 
                    payment_type =payment_type,
                    client_type = client_type

                )
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
        
        serialized = VoucherOrderSerializer(voucher_order)
        return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Voucher Order Sale Created!',
                    'error_message' : None,
                    'sale' : serialized.data
                }
            },
            status=status.HTTP_201_CREATED
        )
    else:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'sale_type fields missing choice one',
                    'fields' : [
                          'PRODUCT',
                          'SERVICE', 
                          'MEMBERSHIP', 
                          'VOUCHER', 
                            ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )