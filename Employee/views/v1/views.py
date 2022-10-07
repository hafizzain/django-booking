from tkinter import N
from django.shortcuts import render
from Employee.models import( Employee , EmployeeProfessionalInfo ,
                        EmployeePermissionSetting,  EmployeeModulePermission
                        , EmployeeMarketingPermission , StaffGroup 
                        , StaffGroupModulePermission, Attendance
                        ,Payroll, CommissionSchemeSetting, Asset, AssetDocument
                        )
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from Employee.serializers import( EmployeSerializer , EmployeInformationsSerializer
                          , EmployPermissionSerializer,  EmployeModulesSerializer
                          ,  EmployeeMarketingSerializers, StaffGroupSerializers , 
                          StaffpermisionSerializers , AttendanceSerializers
                          ,PayrollSerializers,singleEmployeeSerializer , CommissionSerializer
                          , AssetSerializer, WorkingScheduleSerializer
                        
                          
                                 )
from Service.models import Service
from rest_framework import status
from Business.models import Business
from Utility.models import Country, State, City
from Authentication.models import User
from NStyle.Constants import StatusCodes
import json
from Utility.models import NstyleFile
from django.db.models import Q
import csv




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_employee(request):
    employee_csv = request.data.get('file', None)
    user= request.user
    business_id = request.data.get('business', None)

    file = NstyleFile.objects.create(
        file = employee_csv
    )
    with open( file.file.path , 'r', encoding='utf-8') as imp_file:
        for index, row in enumerate(imp_file):
            if index == 0:
                continue
            
            row = row.split(',')
            row = row
            if len(row) < 10:
                print(len(row))
                continue
                #pass
            name= row[0].strip('"')
            designation= row[1].strip('"')
           
            email=row[2].strip('"')
            income_type= row[3].strip('"')
            salary= row[4].strip('"')
            address= row[5].strip('"')
            gender= row[6].strip('"')
            country= row[7].strip('"')
            city= row[8].strip('"')
            state= row[9].strip('"').replace('\n', '').strip('"')
            #employee_id = row[10]
            print(city)
            
            try:
                business=Business.objects.get(id=business_id )
            except Exception as err:
                return Response(
                    {
                'status' : True,
                'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text' :'BUSINESS_NOT_FOUND_4015' ,
                'response' : {
                    'message' : 'Business not found!',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
            try:
                country = Country.objects.get(name__icontains=country)
                state= State.objects.get(name__icontains=state)
                city = City.objects.get(name__icontains=city)
            except Exception as err:
                return Response(
                    {
                'status' : True,
                'status_code' : StatusCodes.INVALID_COUNTRY_STATE_CITY_4021,
                'status_code_text' :'INVALID_COUNTRY_STATE_CITY_4021' ,
                'response' : {
                    'message' : 'Invalid Country, State, City not found!',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

            
            employee= Employee.objects.create(
                user = user,
                business = business,
                full_name= name,
                email= email,
                address=address,
                gender=gender,
                country= country, 
                state = state,
                city = city,
            )
            
            EmployeeProfessionalInfo.objects.create(
                employee = employee,
                designation = designation,
                income_type = income_type,
                salary = salary,
            )
            
            EmployeePermissionSetting.objects.create(
                employee = employee,
                allow_calendar_booking = True,
                access_calendar = False,
                change_calendar_color = False,
            )
            
            EmployeeModulePermission.objects.create(
                employee = employee,
                access_reports = False,
                access_sales = False,
                access_inventory = False,
                access_expenses = False, 
                access_products = False,
            )
            
            EmployeeMarketingPermission.objects.create(
                employee = employee,
                access_voucher = False,
                access_member_discount = False,
                access_invite_friend = False,
                access_loyalty_points = False,
                access_gift_cards = False
            )
        
    file.delete()
    return Response({'Status' : 'Success'})
        

# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def search_employee(request):
    text = request.GET.get('text', None)

    if text is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Fields are required.',
                    'fields' : [
                        'text',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    search_employee = Employee.objects.filter(
        Q(full_name__icontains=text)|
        Q(employee_id__icontains=text) |
        Q(email__icontains=text)|
        Q(mobile_number__icontains=text)|
        Q(gender__icontains=text)|
        Q(employee_professional_details__designation__icontains=text)|
        Q(employee_professional_details__income_type__icontains=text) 
    )
    serialized = singleEmployeeSerializer(search_employee, many=True, context={'request':request})
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'All Search Products!',
                'error_message' : None,
                'count' : len(serialized.data),
                'Employees' : serialized.data,
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_Employees(request):
    all_employe= Employee.objects.filter(is_deleted=False, is_blocked=False).order_by('-created_at')
    serialized = singleEmployeeSerializer(all_employe,  many=True, context={'request' : request} )
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Employee',
                'error_message' : None,
                'employees' : serialized.data
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
        employee_id = Employee.objects.get(id=employee_id)
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
    seralized = EmployeSerializer(employee_id, context={'request' : request})
    data = dict()
    data.update(seralized.data)
    try:
        data.update(data['permissions'])
        del data['permissions']
        data.update(data['module_permissions'])
        del data['module_permissions']
        data.update(data['employee_info'])
        del data['employee_info']
        data.update(data['marketing_permissions'])
        del data['marketing_permissions']
    except Exception as err:
        print(err)
        None
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Business languages',
                'error_message' : None,
                'Employee' : data
            }
        },
        status=status.HTTP_200_OK
    )

    
@api_view(['GET'])
@permission_classes([AllowAny])
def working_schedule(request):
    data=[]
    all_employe= Employee.objects.filter(is_deleted=False, is_blocked=False).order_by('-created_at')
    serialized = WorkingScheduleSerializer(all_employe,  many=True, context={'request' : request} )
    data.append(serialized.data)
   
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Employee',
                'error_message' : None,
                'employees' : data
            }
        },
        status=status.HTTP_200_OK
    )
    
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
   
    tenant_name ='NS'
    return_loop = True
    while return_loop:
        if 0 < count <= 9 : 
            count = f'000{count}'
        elif 9 < count <= 99 :
            count = f'00{count}'
        elif 99 < count <= 999:
            count = f'0{count}'
        new_id =f'{tenant_name}-EMP-{count}'
        
        try:
            Employee.objects.get(employee_id=new_id)
            count += 1
        except:
            return_loop = False
            break
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Generated ID',
                'error_message' : None,
                'id' : new_id
            }
        },
        status=status.HTTP_200_OK
    )
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_employee(request):
    user = request.user     
    
    full_name= request.data.get('full_name', None)
    employee_id= request.data.get('employee_id', None)
    
    email= request.data.get('email', None)
    image = request.data.get('image', None)
    business_id= request.data.get('business', None)  
    mobile_number= request.data.get('mobile_number', None)    
    dob= request.data.get('dob', None)
    gender = request.data.get('gender' , 'Male')
    
    postal_code= request.data.get('postal_code' , None)
    address= request.data.get('address' , None)
    joining_date = request.data.get('joining_date', None)
    to_present = request.data.get('to_present', False)
    ending_date= request.data.get('ending_date',None)
    is_active = request.data.get('is_active',None)    
    
    #UserInformation
    designation = request.data.get('designation', None)
    income_type = request.data.get('income_type', 'Hourly_Rate')
    salary = request.data.get('salary', None) 
    
    end_time= request.data.get('end_time',None)
    start_time = request.data.get('start_time', None)
    working_days = request.data.get('working_days',None)
    level = request.data.get('level',None)
    
    start_time = request.data.get('start_time',None)
    end_time = request.data.get('end_time',None)
    
    services_id = request.data.get('services', None)   
     
    country = request.data.get('country', None)   
    state = request.data.get('state', None)         
    city = request.data.get('city', None)
   
    if not all([
         business_id, full_name ,employee_id, email, country, state, city ,gender  ,address , designation, income_type, salary, level ]): #or ( not to_present and ending_date is None):
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
                        'employee_id',
                        'full_name',
                        'email',
                        'gender', 
                        'country',
                        'state',  
                        'address' ,
                        'designation',
                        'income_type',
                        'salary',
                        'level',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    if len(salary) > 7:
        return Response(
            {
                'status' : True,
                'status_code' : StatusCodes.INVALID_LENGTH_4030,
                'status_code_text' :'INVALID_LENGTH_4030' ,
                'response' : {
                    'message' : 'Length not Valid!',
                    'error_message' : 'Salary length to be 6 Integer',
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        business=Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status' : True,
                'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text' :'BUSINESS_NOT_FOUND_4015' ,
                'response' : {
                    'message' : 'Business not found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        country = Country.objects.get(id=country)
        state= State.objects.get(id=state)
        city = City.objects.get(id=city)
    except Exception as err:
        return Response(
            {
                'status' : True,
                'status_code' : StatusCodes.INVALID_COUNTRY_STATE_CITY_4021,
                'status_code_text' :'INVALID_COUNTRY_STATE_CITY_4021' ,
                'response' : {
                    'message' : 'Invalid Country, State, City not found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    employee= Employee.objects.create(
        user=user,
        business=business,
        full_name = full_name,
        image= image,
        employee_id= employee_id,
        email= email,
        mobile_number= mobile_number,
        dob=dob,
        gender= gender,
        country= country,
        state = state,
        city = city,
        postal_code = postal_code,
        address=address,
        joining_date= joining_date,
    )
    if not to_present :
        pass
    else:
        employee.to_present = True 
    if is_active is not None:
        employee.is_active =True
    else:
        employee.is_active = False 
    employee.save()
    data = {}

    errors =[]

    employee_p_info = EmployeeProfessionalInfo.objects.create(employee=employee, start_time = start_time , end_time = end_time, salary=salary, designation = designation)
    employee_mp = EmployeeModulePermission.objects.create(employee=employee)
    employee_p_setting = EmployeePermissionSetting.objects.create(employee = employee)
    employee_marketing = EmployeeMarketingPermission.objects.create(employee= employee)
    
    ser_error=[] 
    
    employee_p_info.monday = True if 'monday' in request.data else False
    employee_p_info.tuesday = True if 'tuesday' in request.data else False
    employee_p_info.wednesday = True if 'wednesday' in request.data else False
    employee_p_info.thursday = True if 'thursday' in request.data else False
    employee_p_info.friday = True if 'friday' in request.data else False
    employee_p_info.saturday = True if 'saturday' in request.data else False
    employee_p_info.sunday = True if 'sunday' in request.data else False
    
    if type(working_days) == str:
            working_days = json.loads(working_days)

    elif type(working_days) == list:
            pass
    if type(services_id) == str:
            services_id = json.loads(services_id)
            print('str')

    elif type(services_id) == list:
            pass
        
    for ser in services_id:
            try:
                service = Service.objects.get(id=ser)  
                print(type(service))
                print(service)
                employee_p_info.services.add(service)
            except Exception as err:
                print(str(err))
    employee_p_info.save()
    
    serialized = EmployeInformationsSerializer(employee_p_info, data=request.data)
    if serialized.is_valid():
        serialized.save()
        data.update(serialized.data)

    serialized = EmployPermissionSerializer(employee_p_setting, data=request.data)
    if serialized.is_valid():
        serialized.save()
        data.update(serialized.data)

    serialized = EmployeModulesSerializer(employee_mp, data=request.data)
    if serialized.is_valid():
        serialized.save()
        data.update(serialized.data)

    serialized = EmployeeMarketingSerializers(employee_marketing, data=request.data)
    if serialized.is_valid():
        serialized.save()
        data.update(serialized.data)
    employee_serialized = EmployeSerializer(employee , context={'request' : request})
    data.update(employee_serialized.data)


    return Response(
        {
            'status' : True,
            'status_code' : 201,
            'response' : {
                'message' : 'Employees Added!',
                'error_message' : None,
                'employees' : data
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
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
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
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Employee ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    employee.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Employee deleted successful',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_employee(request): 
    # sourcery skip: avoid-builtin-shadow
        id = request.data.get('id', None)
        is_active = request.data.get('is_active' ,None)
        services_id = request.data.get('services', None)   

        if id is None:
            return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'User id is required',
                    'fields' : [
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
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
                    'status_code_text' : 'INVALID_NOT_FOUND_EMPLOYEE_ID_4022',
                          'response' : {
                        'message' : 'Employee Not Found',
                        'error_message' : str(err),
                    }
                },
                   status=status.HTTP_404_NOT_FOUND
              )
        data={}
        image=request.data.get('image',None)
        if image is not None:
            employee.image=image
            
        if is_active is not None:
            employee.is_active =True
        else:
            employee.is_active = False 
        employee.save()
        serializer = EmployeSerializer(employee, data=request.data, partial=True, context={'request' : request})
        if serializer.is_valid():
           serializer.save()
           data.update(serializer.data)
        else: 
             return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
                'response' : {
                    'message' : 'Invialid Data',
                    'error_message' : str(serializer.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
        

        Employe_Informations= EmployeeProfessionalInfo.objects.get(employee=employee)
        if type(services_id) == str:
            services_id = json.loads(services_id)
            print('str')

        elif type(services_id) == list:
            pass
        
        for ser in services_id:
            
            try:
                service = Service.objects.get(id=ser)  
                Employe_Informations.services.add(service)
            except Exception as err:
                print(str(err))
        Employe_Informations.save()
        serializer_info= EmployeInformationsSerializer(Employe_Informations,  data= request.data, partial=True)
        if serializer_info.is_valid():
                serializer_info.save()
                data.update(serializer_info.data)
        else:
         return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_EMPLOYEE_INFORMATION_4026,
                'response' : {
                    'message' : 'Invalid Data',
                    'error_message' : str(serializer_info.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
     )
         
        ps_data = {}
        ps_data['allow_calendar_booking'] = True if request.data.get('allow_calendar_booking', None) is not None else False
        ps_data['access_calendar'] = True if request.data.get('access_calendar', None) is not None else False
        ps_data['change_calendar_color'] = True if request.data.get('change_calendar_color', None) is not None else False

        permission= EmployeePermissionSetting.objects.get(employee=employee)
        serializer_permision= EmployPermissionSerializer(permission,  data=ps_data, partial=True)
        if serializer_permision.is_valid():
               serializer_permision.save()
               data.update(serializer_permision.data)
        else:
                return Response(
            {
                'status' : False,
                'status_code' :StatusCodes.INVALID_EMPLOYEE_PERMISSION_4027,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : str(serializer_permision.errors),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        md_data = {}
        md_data['access_reports'] = True if request.data.get('access_reports', None) is not None else False
        md_data['access_sales'] = True if request.data.get('access_sales', None) is not None else False
        md_data['access_inventory'] = True if request.data.get('access_inventory', None) is not None else False
        md_data['access_expenses'] = True if request.data.get('access_expenses', None) is not None else False
        md_data['access_products'] = True if request.data.get('access_products', None) is not None else False
    
        Module_Permission= EmployeeModulePermission.objects.get(employee=employee)
        serializer_Module = EmployeModulesSerializer(Module_Permission,  data=md_data, partial=True)
        if serializer_Module.is_valid():
               serializer_Module.save()
               data.update(serializer_Module.data)
               
        else:
                return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_EMPLOYEE_PERMISSION_4027,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : str(serializer_Module.errors),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
                
        mp_data = {}
        mp_data['access_voucher'] = True if request.data.get('access_voucher', None) is not None else False
        mp_data['access_member_discount'] = True if request.data.get('access_member_discount', None) is not None else False
        mp_data['access_invite_friend'] = True if request.data.get('access_invite_friend', None) is not None else False
        mp_data['access_loyalty_points'] = True if request.data.get('access_loyalty_points', None) is not None else False
        mp_data['access_gift_cards'] = True if request.data.get('access_gift_cards', None) is not None else False
        
        Marketing_Permission= EmployeeMarketingPermission.objects.get(employee=employee)
        serializer_Marketing= EmployeeMarketingSerializers(Marketing_Permission,  data=mp_data, partial=True)
        if serializer_Marketing.is_valid():
                serializer_Marketing.save()
                data.update(serializer_Marketing.data)
        else:
              return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_EMPLOYEE_PERMISSION_4027,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : str(serializer_Marketing.errors),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : ' Employee updated successfully',
                    'error_message' : None,
                    'Employee' : data
                }
            },
            status=status.HTTP_200_OK
           )

@api_view(['GET'])
@permission_classes([AllowAny])
def delete_all_employees(request):
    all_employees = Employee.objects.all()

    for empl in all_employees:
        empl.delete()
    return Response({'deleted' : True})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_staff_group(request):
    
        user = request.user     
        business_id= request.data.get('business', None)
        
        name = request.data.get('name', None)
        employees = request.data.get('employees', None)
        
        is_active= request.data.get('is_active' , None)
        
        access_reports=request.data.get('access_reports', True)
        access_sales=request.data.get('access_sales', False)
        access_inventory=request.data.get('access_inventory' , False)
        access_expenses=request.data.get('access_expenses' , True)
        access_products= request.data.get('access_products' , False)
        
        
        if not all([ business_id, name, employees ]):
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
        if is_active is not None:
           #     is_active= json.loads(is_active)
           is_active = True
        else: 
              is_active = False
                
        staff_group= StaffGroup.objects.create(
            user=user,
            business= business, 
            name= name,
            is_active=is_active,
        
        )
        #StaffGroupModulePermission
        staff_module_permission= StaffGroupModulePermission.objects.create(
            staff_group=staff_group,
            access_reports=access_reports,
            access_sales=access_sales,
            access_inventory=access_inventory,
            access_expenses=access_expenses,
            access_products=access_products,
        )
        #staff_permission_serializers =  StaffpermisionSerializers(staff_module_permission)
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
        staff_group.save()
        serialized = StaffGroupSerializers(staff_group, context={'request' : request})
       
        return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Staff Group Create!',
                    'error_message' : None,
                    'StaffGroup' : serialized.data,
                    'staff_errors' : employees_error,
                }
            },
            status=status.HTTP_201_CREATED
        ) 
 
@api_view(['GET'])
@permission_classes([AllowAny])
def get_staff_group(request):
    all_staff_group= StaffGroup.objects.all().order_by('-created_at')
    serialized = StaffGroupSerializers(all_staff_group, many=True, context={'request' : request})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Staff Group',
                'error_message' : None,
                'employees' : serialized.data
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
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required.',
                    'fields' : [
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
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Employee ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    employee.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Staff Group deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_staff_group(request):
    staff_id = request.data.get('staff_id', None)
    employees_error = []
    if staff_id is None: 
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.MISSING_FIELDS_4001,
            'status_code_text' : 'MISSING_FIELDS_4001',
            'response' : {
                'message' : 'Invalid Data!',
                'error_message' : 'Staff ID are required.',
                'fields' : [
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
                'status' : False,
                'status_code' : StatusCodes.INVALID_STAFF_GROUP_4028,
                'status_code_text' : 'INVALID_STAFF_GROUP_4028',
                'response' : {
                    'message' : 'Staff Group Not Found',
                    'error_message' : str(err),
                }
            },
                status=status.HTTP_404_NOT_FOUND
        )
    data={}
    try:
       staff_gp_permissions = StaffGroupModulePermission.objects.get(staff_group=staff_group)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_EMPLOYEE_INFORMATION_4026,
                'response' : {
                    'message' : 'Invalid Data',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
     )
    
    employees=request.data.get('employees', None)
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
        
    permission_serializer =StaffpermisionSerializers(staff_gp_permissions, data=request.data, partial=True, context={'request' : request})
    if permission_serializer.is_valid():
        permission_serializer.save()
        data.update(permission_serializer.data)
    else:
         return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_EMPLOYEE_INFORMATION_4026,
                'response' : {
                    'message' : 'Invalid Data',
                    'error_message' : str(permission_serializer.errors),
                }
            },
            status=status.HTTP_404_NOT_FOUND
     )
    serializer = StaffGroupSerializers(staff_group, data=request.data, partial=True, context={'request' : request})
    if serializer.is_valid():
        serializer.save()
        data.update(serializer.data)
    else:
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Staff Group Serializer Invalid',
                'error_message' : str(serializer.errors),
            }
        },
        status=status.HTTP_404_NOT_FOUND
        ) 

    
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Update Staff Group Successfully',
                'error_message' : None,
                'StaffGroupUpdate' : data
            }
        },
        status=status.HTTP_200_OK
        )
    

@api_view(['GET'])
@permission_classes([AllowAny])
def get_attendence(request):
    all_attendence= Attendance.objects.all()
    serialized = AttendanceSerializers(all_attendence, many=True)
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Attendance',
                'error_message' : None,
                'attendance' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )

    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_attendence(request):
    user = request.user     
    business = request.data.get('business', None)
    employees = request.data.get('employees', None)
    is_active= request.data.get('is_active' , False)
    in_time= request.data.get('in_time', None)
    
    if not all([ business, employees , in_time  ]):
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
                          'employees',
                          'in_time', 
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
    try:
        employee_id=Employee.objects.get(id=employees)
    except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
                    'response' : {
                    'message' : 'Employee not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    attendence_employe=Attendance.objects.create(
        user=user,
        business= business_id,
        employee=employee_id,
        in_time= in_time,
        is_active=is_active,
    )
    
    attendece_serializers=AttendanceSerializers(attendence_employe)
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Attendence Created Successfully!',
                    'error_message' : None,
                    'StaffGroup' : attendece_serializers.data,
                }
            },
            status=status.HTTP_201_CREATED
        ) 
 
 
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_attendence(request):
    attendence_id = request.data.get('attendence_id', None)
    if attendence_id is None: 
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.MISSING_FIELDS_4001,
            'status_code_text' : 'MISSING_FIELDS_4001',
            'response' : {
                'message' : 'Invalid Data!',
                'error_message' : 'Attendence ID are required.',
                'fields' : [
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
                'status' : False,
                'status_code' : StatusCodes.INVALID_ATTENDENCE_ID_OR_NOT_FOUND_4029,
                'status_code_text' : 'INVALID_ATTENDENCE_ID_OR_NOT_FOUND_4029',
                'response' : {
                    'message' : 'Attendence Not Found',
                    'error_message' : str(err),
                }
            },
                status=status.HTTP_404_NOT_FOUND
        )
    serializer = AttendanceSerializers(attendence, data=request.data, partial=True)
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
                'message' : 'Update Attendence Successfully',
                'error_message' : None,
                'StaffGroupUpdate' : serializer.data
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
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
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
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Attendance ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    attendence.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Attendance deleted successful',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_payrolls(request):
    all_payroll= Payroll.objects.all()
    serialized = PayrollSerializers(all_payroll, many=True)
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Payroll',
                'error_message' : None,
                'payroll' : serialized.data
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
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
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
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Payroll ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    payroll.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Payroll deleted successful',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payroll(request):
    user = request.user
    
    business = request.data.get('business', None)
    employees = request.data.get('employees', None)
    name = request.data.get('name', None)
    Total_hours= request.data.get('Total_hours', None)
    
    if not all([ business, employees , name , Total_hours ]):
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
                          'employees',
                          'name', 
                          'Total_hours'
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
    try:
        employee_id=Employee.objects.get(id=employees)
    except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
                    'response' : {
                    'message' : 'Employee not found',
                    'error_message' : str(err),
                }
                }
            )
            
    payroll= Payroll.objects.create(
        user= user,
        business= business_id,
        employee=employee_id,
        name= name,
        Total_hours=Total_hours
        
    )
    
    payroll_serializers= PayrollSerializers(payroll)
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Payroll Created Successfully!',
                    'error_message' : None,
                    'StaffGroup' : payroll_serializers.data,
                }
            },
            status=status.HTTP_201_CREATED
        ) 
    
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_commission (request):
    business = request.GET.get('business', None)
    if business is None:
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required.',
                    'fields' : [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
       
    try:
             business=Business.objects.get(id=business)
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
       
    commission , created =  CommissionSchemeSetting.objects.get_or_create(
        business=business,
        user=business.user,
        )
    serializer = CommissionSerializer(commission)
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Commission',
                'error_message' : None,
                'commission' : serializer.data
            }
        },
        status=status.HTTP_200_OK
    )
   
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_commision(request):
    commission_id = request.data.get('commission_id', None)
    
    service_price_before_membership_discount= request.data.get('service_price_before_membership_discount',None)
    sale_price_including_tax= request.data.get('sale_price_including_tax',None)
    sale_price_before_discount= request.data.get('sale_price_before_discount' , None)
    
    if commission_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
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
                'status' : False,
                'status_code' : StatusCodes.INVALID_COMMISSION_ID_4034,
                'status_code_text' : 'INVALID_COMMISSION_ID_4034',
                'response' : {
                    'message' : 'Attendence Not Found',
                    'error_message' : str(err),
                }
            },
                status=status.HTTP_404_NOT_FOUND
        )
    if sale_price_before_discount is not None:
        sale_price_before_discount = True
    else:
        sale_price_before_discount = False
    if sale_price_including_tax is not None:
        sale_price_including_tax = True
    else:
        sale_price_including_tax = False
    if service_price_before_membership_discount is not None:
        service_price_before_membership_discount= True
    else:
        service_price_before_membership_discount= False
        
    commission.sale_price_including_tax=sale_price_including_tax
    commission.service_price_before_membership_discount=service_price_before_membership_discount
    commission.sale_price_before_discount=sale_price_before_discount
    commission.save()
        
    serializer = CommissionSerializer(commission, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Commission Serializer Invalid',
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
                'message' : 'Update Commission Successfully',
                'error_message' : None,
                'commission' : serializer.data
            }
        },
        status=status.HTTP_200_OK
        )
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_asset(request):
    user = request.user
    business_id = request.data.get('business', None)
    
    name = request.data.get('name', None)
    employee_id = request.data.get('employee', None)
    given_date = request.data.get('given_date',None)
    return_date = request.data.get('return_date',None)
    
    is_active= request.data.get('is_active' ,None)
    document =request.FILES.getlist('document',  None)
    
    if not all([ business_id, name, employee_id, given_date, document ]):
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
                          'employee',
                          'given_date', 
                          'document',
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
    if is_active is not None:
        is_active = True
    else: 
        is_active = False
        
    try:
        employee = Employee.objects.get(id=employee_id)
    except Exception as err:
        return Response(
             {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_NOT_FOUND_EMPLOYEE_ID_4022,
                    'status_code_text' : 'INVALID_NOT_FOUND_EMPLOYEE_ID_4022',
                          'response' : {
                        'message' : 'Employee Not Found',
                        'error_message' : str(err),
                    }
                },
                   status=status.HTTP_404_NOT_FOUND
              )
    
    asset= Asset.objects.create(
        user= user,
        business= business,
        employee=employee,
        name= name,
        given_date = given_date,
        return_date =return_date,
        is_active =is_active
    )
    if document is not None:
        for doc in document:
            doc = AssetDocument.objects.create(
                asset = asset,
                document = doc
            )
    serializers= AssetSerializer(asset)
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Asset Created Successfully!',
                    'error_message' : None,
                    'asset' : serializers.data,
                }
            },
            status=status.HTTP_201_CREATED
        ) 
        
        
@api_view(['GET'])
@permission_classes([AllowAny])
def get_asset(request):
    all_asset= Asset.objects.all().order_by('created_at')
    serialized = AssetSerializer(all_asset, many=True, context={'request' : request})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Assets',
                'error_message' : None,
                'asset' : serialized.data
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
        asset = Asset.objects.get(id=asset_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Asset ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    asset.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Asset deleted successful',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_asset(request):
    asset_id = request.data.get('id', None)
    if asset_id is None: 
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
        asset = Asset.objects.get(id=asset_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Asset ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = AssetSerializer(asset, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Asset Serializer Invalid',
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
                'message' : 'Update Asset Successfully',
                'error_message' : None,
                'asset' : serializer.data
            }
        },
        status=status.HTTP_200_OK
        )