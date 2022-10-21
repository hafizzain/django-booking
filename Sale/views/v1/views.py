from ast import Str
import imp
from django.shortcuts import render

from rest_framework import status
from Business.models import Business
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

from Sale.serializers import ServiceSerializer


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
    slot_availible_for_online = request.data.get('controls_time_slot', None)
    
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
        for usr in employeeslist:
            try:
               
                employe = Employee.objects.get(id=usr)
                
                employe_service = EmployeeSelectedService.objects.get(employee = employe)
                # try:
                #     employe_service.employee
                # except EmployeeSelectedService.DoesNotExist:
                    
                
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