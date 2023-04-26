from datetime import datetime, timedelta
import random
import string
from time import strptime
from django.shortcuts import render
from Employee.models import( CategoryCommission, EmployeDailySchedule, Employee , EmployeeProfessionalInfo ,
                        EmployeePermissionSetting,  EmployeeModulePermission
                        , EmployeeMarketingPermission, EmployeeSelectedService, SallarySlipPayrol , StaffGroup 
                        , StaffGroupModulePermission, Attendance
                        ,Payroll, CommissionSchemeSetting, Asset, AssetDocument, Vacation
                        )
from Tenants.models import EmployeeTenantDetail, Tenant
from django_tenants.utils import tenant_context
from Utility.Constants.Data.PermissionsValues import ALL_PERMISSIONS, PERMISSIONS_MODEL_FIELDS
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from Employee.serializers import( EmployeSerializer , EmployeInformationsSerializer
                          , EmployPermissionSerializer,  EmployeModulesSerializer, EmployeeInformationSerializer
                          ,  EmployeeMarketingSerializers, Payroll_Working_device_attendence_ScheduleSerializer, Payroll_Working_deviceScheduleSerializer, Payroll_WorkingScheduleSerializer, SallarySlipPayrolSerializers, ScheduleSerializer, SingleEmployeeInformationSerializer, StaffGroupSerializers , 
                          StaffpermisionSerializers , AttendanceSerializers
                          ,PayrollSerializers, UserEmployeeSerializer, VacationSerializer,singleEmployeeSerializer , CommissionSerializer
                          , AssetSerializer, WorkingScheduleSerializer,NewScheduleSerializer,NewVacationSerializer,NewAbsenceSerializer,
                        
                          
                                 )
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
from django.db.models import Q
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
        

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_attendance(request):
    attendence_csv = request.data.get('file', None)
    business_id = request.data.get('business', None)
    user= request.user
    
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
    file = NstyleFile.objects.create(
        file = attendence_csv
    )
    with open( file.file.path , 'r', encoding='utf-8') as imp_file:
        for index, row in enumerate(imp_file):
            if index == 0:
                continue
            #row =  row.replace("'", '"')
            row = row.split(',')
            row = row
            if len(row) < 4:
                continue
                #pass
            emp_name= row[0].strip('"')
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
            in_time = row[1].strip('"')
            out_time = row[2].strip('"')
            status_att = row[3].strip('"')
            
            create_attendence = Attendance.objects.create(
                user = user,
                business = business,
                employee = employee_id,
                in_time = in_time,
                out_time = out_time,
                #is_active = status_att,
                
            )
            if status_att.strip() ==  'Active':
                create_attendence.is_active =True
                create_attendence.save()
            else :
                create_attendence.is_active = False
                create_attendence.save()
            # if out_time == strptime('%H:%M:%S') :
            #     print('enter')
            #     create_attendence.out_time =out_time
            #     create_attendence.save()
            # else:
            #     create_attendence.out_time =None
            #     create_attendence.save()

            #print(f'Added Product {create_attendence} ... {employee_id} ')

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

        staff = None
    seralized = EmployeSerializer(employee_id,  context={'request' : request,})
    
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
def single_employee_schedule(request): 
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
    serializer = WorkingScheduleSerializer(employee_id)
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Single Employee',
                'error_message' : None,
                'employee' : serializer.data
            }
        },
        status=status.HTTP_200_OK
    )
    

@api_view(['GET'])
@permission_classes([AllowAny])
def working_schedule(request):
    all_employe= Employee.objects.filter(is_deleted=False, is_blocked=False).order_by('-created_at')
    serialized = WorkingScheduleSerializer(all_employe,  many=True, context={'request' : request,} )
   
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
@permission_classes([IsAuthenticated])
def generate_id(request):
    tenant_name = request.tenant_name
    tenant_name = tenant_name.split('-')
    tenant_name = [word[0] for word in tenant_name]
    print(tenant_name)
    ''.join(tenant_name)
    count = Employee.objects.all().count()
    count += 1
   
    #tenant_name ='NS'
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
@permission_classes([AllowAny])
def check_email_employees(request): 
    email = request.data.get('email', None)

    if not all([email]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Employee id are required',
                    'fields' : [
                        'email',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    with tenant_context(Tenant.objects.get(schema_name = 'public')):
        try:
            employe = User.objects.get(email__icontains = email)
            return Response(
                {
                    'status' : False,
                    'status_code' : 200,
                    'status_code_text' : '200',
                    'response' : {
                        'message' : f'User Already exist with this {email}!',
                        'error_message' : None,
                        'employee' : True
                    }
                },
                status=status.HTTP_200_OK
            )
        except Exception as err:
            pass
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Single Employee',
                'error_message' : None,
                'employee' : False
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
    tenant_id= request.data.get('tenant_id', None)
    domain= request.data.get('domain', None)
    
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
    
    #end_time= request.data.get('end_time',None)
    #start_time = request.data.get('start_time', None)
    working_days = request.data.get('working_days',None)
    staff_id = request.data.get('staff_group', None)
    #level = request.data.get('level',None)
    
    #start_time = request.data.get('start_time',None)
    #end_time = request.data.get('end_time',None)
    maximum_discount = request.data.get('maximum_discount',None)
    
    services_id = request.data.get('services', None)   
     
    location = request.data.get('location', None)
    country = request.data.get('country', None)   
    state = request.data.get('state', None)         
    city = request.data.get('city', None)
    


    if not all([
         business_id, full_name ,employee_id, country, gender  ,address , designation, income_type, salary ]): #or ( not to_present and ending_date is None):
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
                        'address' ,
                        'designation',
                        'income_type',
                        'salary',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    if email is not None:
        with tenant_context(Tenant.objects.get(schema_name = 'public')):
            try:
                employe = User.objects.get(email__icontains = email)
                return Response(
                    {
                        'status' : False,
                        'status_code' : 404,
                        'status_code_text' : '404',
                        'response' : {
                            'message' : f'User Already exist with this {email}!',
                            'error_message' : None,
                        }
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as err:
                pass
    
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
    employees_error = []
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
        
    try:
        state= State.objects.get(id=state)
    except:
        state = None
    try:
        city= City.objects.get(id=city)
    except:
        city = None
    try:
        staff = StaffGroup.objects.get(id=staff_id)
    except Exception as err:
        staff = None
        
    employee= Employee.objects.create(
        user=user,
        business=business,
        full_name = full_name,
        image= image,
        employee_id= employee_id,
        mobile_number= mobile_number,
        dob=dob,
        gender= gender,
        country= country,
        state = state,
        city = city,
        postal_code = postal_code,
        address=address,
        joining_date= joining_date,
        ending_date=ending_date,
    )
    if not to_present :
        pass
    else:
        employee.to_present = True 
    if is_active is not None:
        employee.is_active =True
    else:
        employee.is_active = False 
    
    if email is not None:
        employee.email= email
    employee.save()
    data = {}

    errors =[]

    if staff is not None:
        try:
            staff.employees.add(employee)
            #data.update(staff)
        except:
            pass
    
    employee_p_info = EmployeeProfessionalInfo.objects.create(
            employee=employee,
            # start_time = start_time , end_time = end_time, 
            maximum_discount = maximum_discount,
            salary=salary, 
            designation = designation,
            income_type = income_type,
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
        for services in services_id :
            try:
                if services['service'] is not None:
                    ser = Service.objects.get(id=services['service'])
                
                    EmployeeSelectedService.objects.get_or_create(
                        employee = employee,
                        service = ser,
                        level = services['level']
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
    
    employee_serialized = EmployeSerializer(employee , context={'request' : request, })
    data.update(employee_serialized.data)

    template = 'Employee'
    if email is not None:
        try:
            try:
                username = email.split('@')[0]
                try:
                    user_check = User.objects.get(username = username)
                except Exception as err:
                    #data.append(f'username user is client errors {str(err)}')
                    pass
                else:
                    username = f'{username} {len(User.objects.all())}'

            except Exception as err:
                pass

            user = User.objects.create(
                first_name = full_name,
                username = username,
                email = email ,
                is_email_verified = True,
                is_active = True,
                mobile_number = mobile_number,
            )
            account_type = AccountType.objects.create(
                    user = user,
                    account_type = 'Employee'
                )
        except Exception as err:
            pass        
    # stop_thread = False
    try:
        thrd = Thread(target=add_employee, args=[full_name, email , mobile_number, template, business.business_name, tenant_id, domain, user])
        thrd.start()
        # stop_thread = True
        # if thrd.is_alive():
        #     thrd._stop()
    except Exception as err:
        employees_error.append(str(err))
    
    return Response(
        {
            'status' : True,
            'status_code' : 201,
            'response' : {
                'message' : 'Employee Added Successfully!',
                'error_message' : None,
                'employee_error':employees_error,
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
        
    try:
        staff_group = StaffGroup.objects.get(employees = employee)
        #print(staff_group)
        staff_group.employees.remove(employee)
        #print(staff_group.employees.remove(employee))
        staff_group.save()
    except:
        pass
    
    employee.is_deleted = True
    employee.save()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Employee deleted successfully',
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
    staff_id = request.data.get('staff_group', None) 
    location = request.data.get('location', None) 
    
    country = request.data.get('country', None) 
    city = request.data.get('city', None) 
    state = request.data.get('state', None) 
    
    working_days = []
    
    Errors = []
    
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
        
    data={}
    image=request.data.get('image',None)
    phone_number=request.data.get('mobile_number',None)
    
    
    if phone_number is not None:
        employee.mobile_number = phone_number
    else :
        employee.mobile_number = None
    if image is not None:
        employee.image=image
        
    if is_active is not None:
        employee.is_active =True
    else:
        employee.is_active = False 
    employee.save()
    
    if country is not None:
        try:
            country= Country.objects.get(id=country)
            employee.country = country
            employee.save()
        except:
            country = None
            
    if state is not None:
        try:
            state= State.objects.get(id=state)
            employee.state = state
            employee.save()
        except:
            state = None
            
    if city is not None:
        try:
            city= City.objects.get(id=city)
            employee.city = city
            employee.save()
        except:
            city = None

    Employe_Informations= EmployeeProfessionalInfo.objects.get(employee=employee)
    
    Employe_Informations.monday = True if 'monday' in request.data else False
    Employe_Informations.tuesday = True if 'tuesday' in request.data else False
    Employe_Informations.wednesday = True if 'wednesday' in request.data else False
    Employe_Informations.thursday = True if 'thursday' in request.data else False
    Employe_Informations.friday = True if 'friday' in request.data else False
    Employe_Informations.saturday = True if 'saturday' in request.data else False
    Employe_Informations.sunday = True if 'sunday' in request.data else False
    
    
    if services_id is not None:
        if type(services_id) == str:
            services_id = services_id.replace("'" , '"')
            services_id = json.loads(services_id)
        else:
            pass
        for services in services_id:
            #get('id', None)
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
    # try:
    #     empl_permission = EmployePermission.objects.get(employee=employee)
        
    #     for permit in ALL_PERMISSIONS:
              
    #         value = request.data.get(permit, None)
    #         PERMISSIONS_MODEL_FIELDS[permit](empl_permission).clear()
            
    #         if value is not None:
    #             if type(value) == str:
    #                 value = json.loads(value)
    #                 for opt in value:
    #                     try:
    #                         option = GlobalPermissionChoices.objects.get(text=opt)
    #                         PERMISSIONS_MODEL_FIELDS[permit](empl_permission).add(option)
    #                     except:
    #                         pass

    #     empl_permission.save()
    
    # except Exception as err:
    #     Errors.append(err)
    
    try:
        empl_permission, created = EmployePermission.objects.get_or_create(employee=employee)
    
        for permit in ALL_PERMISSIONS:
            value = request.data.get(permit, None)
                
            if value is not None:
                #PERMISSIONS_MODEL_FIELDS[permit](empl_permission).clear()
                try:
                    value = json.loads(value)
                except (TypeError, json.JSONDecodeError, AttributeError) as e:
                    print(f"Error parsing value '{value}' for permit '{permit}': {e}")
                else:
                    for opt in value:
                        try:
                            option = GlobalPermissionChoices.objects.get(text=opt)
                            PERMISSIONS_MODEL_FIELDS[permit](empl_permission).add(option)
                        except GlobalPermissionChoices.DoesNotExist:
                            pass
                        
        #empl_permission.save()
        
    except (TypeError, json.JSONDecodeError, AttributeError) as err: #Exception as err:
        Errors.append(err)

    if location is not None:
        try:
            employee.location.clear()
            address=  BusinessAddress.objects.get(id = str(location))
            employee.location.add(address)
        except Exception as err:
            Errors.append(err)
            print(err)

    serializer = EmployeSerializer(employee, data=request.data, partial=True, context={'request' : request,})
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
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : ' Employee updated successfully',
                'error_message' : Errors,
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
def import_staff_group(request): 
    user = request.user
    staff_csv = request.data.get('file', None)
    business_id = request.data.get('business', None)
    
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
    
    file = NstyleFile.objects.create(
        file = staff_csv
    )
    with open( file.file.path , 'r', encoding='utf-8') as imp_file:
        for index, row in enumerate(imp_file):
            if index == 0:
                continue
            row = row.split(',')
            row = row
            
            if len(row) < 2:
                continue
            name = row[0].strip('"')
            active=row[1].replace('\n', '').strip('"')
            
            if active == 'Active':
                active = True
            else:
                active = False
                
                
            staff_group= StaffGroup.objects.create(
                user=user,
                business= business, 
                name= name,
                is_active=active,
            )
            
    file.delete()
    return Response({'Status' : 'Success'})
            

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
        # staff_module_permission= StaffGroupModulePermission.objects.create(
        #     staff_group=staff_group,
        #     access_reports=access_reports,
        #     access_sales=access_sales,
        #     access_inventory=access_inventory,
        #     access_expenses=access_expenses,
        #     access_products=access_products,
        # )
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
        serialized = StaffGroupSerializers(staff_group, context={'request' : request})
       
       

        data = dict()
        data.update(serialized.data)
        try:
            data.update(data['staff_permission'])
            del data['staff_permission']
        except Exception as err:
            print(err)
        return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Staff Group Create!',
                    'error_message' : None,
                    'StaffGroup' : data,
                    'staff_errors' : employees_error,
                }
            },
            status=status.HTTP_201_CREATED
        ) 
 
@api_view(['GET'])
@permission_classes([AllowAny])
def get_staff_group(request):
    all_staff_group= StaffGroup.objects.filter(employees__is_deleted=False).order_by('-created_at').distinct()
    serialized = StaffGroupSerializers(all_staff_group, many=True, context={'request' : request})
    
    data = serialized.data
    # new_data = []
    # for row in data:
    #     let_obj = {}
    #     let_obj.update(row)
    #     let_obj.update(row['staff_permission'])
    #     del let_obj['staff_permission']
    #     new_data.append(let_obj)
    
    # data = {}
    # data.update(serialized.data)
    
    # try:
    #     data.update(data['staff_permission'])
    #     del data['staff_permission']
    # except Exception as err:
    #     print(f'dict {err}')
    #     None   
         
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Staff Group',
                'error_message' : None,
                'staff_group' : data
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
    serializer = StaffGroupSerializers(staff_group, data=request.data, partial=True, context={'request' : request})
    if serializer.is_valid():
        serializer.save()
        #data.update(serializer.data)
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
                'StaffGroupUpdate' : serializer.data
            }
        },
        status=status.HTTP_200_OK
        )
    

@api_view(['GET'])
@permission_classes([AllowAny])
def get_attendence(request):
    # all_attendence= Attendance.objects.all()
    # serialized = AttendanceSerializers(all_attendence, many=True, context={'request' : request})
    
    
    all_employe= Employee.objects.filter(is_deleted=False, is_blocked=False).order_by('-created_at')
    serialized = Payroll_WorkingScheduleSerializer(all_employe,  many=True, context={'request' : request,} )
    
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
@api_view(['GET'])
@permission_classes([AllowAny])
def get_attendence_device(request):
    employee_id = request.GET.get('employee_id', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

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
    
    all_employe= Employee.objects.get(id = employee_id.id, is_deleted=False, is_blocked=False)#.order_by('-created_at')
    serialized = Payroll_Working_device_attendence_ScheduleSerializer(all_employe, context={
                        'request' : request, 
                        'range_start': start_date, 
                        'range_end': end_date, 
            })
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
    out_time= request.data.get('out_time', None)
    
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
        out_time = out_time,
        is_active=is_active,
    )
    
    attendece_serializers=AttendanceSerializers(attendence_employe, context={'request' : request})
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Attendence Created Successfully!',
                    'error_message' : None,
                    'attendence' : attendece_serializers.data,
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
def create_sallaryslip(request):
    user = request.user
    
    business = request.data.get('business', None)
    employees = request.data.get('employees', None)
    month = request.data.get('month', None)
    year = request.data.get('year', None)
 
    if not all([ business, employees , month ]):
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
    received_data = f'{month} {year}'
    
    month = datetime.datetime.strptime(received_data, "%B %Y").month
    year = datetime.datetime.strptime(received_data, "%B %Y").year
    date_obj = datetime.date(year=year, month=month, day=1)
    
    payroll= SallarySlipPayrol.objects.create(
        user= user,
        business= business_id,
        employee=employee_id,
        month = date_obj        
    )    
    payroll_serializers= SallarySlipPayrolSerializers(payroll)
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Sallary Slip Created Successfully!',
                    'error_message' : None,
                    'StaffGroup' : payroll_serializers.data,
                }
            },
            status=status.HTTP_201_CREATED
        ) 

@api_view(['GET'])
@permission_classes([AllowAny])
def get_payrol_working(request):
    all_employe= Employee.objects.filter(is_deleted=False, is_blocked=False).order_by('-created_at')
    serialized = Payroll_WorkingScheduleSerializer(all_employe,  many=True, context={'request' : request,} )
   
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
def get_payrol_working_device(request):
    employee_id = request.GET.get('employee_id', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

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
    all_employe= Employee.objects.get(id = employee_id.id, is_deleted=False, is_blocked=False)#.order_by('-created_at')
    serialized = Payroll_Working_deviceScheduleSerializer(all_employe, context={
                        'request' : request, 
                        'range_start': start_date, 
                        'range_end': end_date, 
            })
   
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
def create_commission(request):
    user = request.user
    business_id = request.data.get('business', None)
    
    employee = request.data.get('employee', None)
    commission_cycle = request.data.get('commission_cycle', None)
    
    service_comission = request.data.get('service_comission', None)
    product_comission = request.data.get('product_comission', None)
    voucher_comission = request.data.get('voucher_comission', None)
    
    if not all([business_id,employee ]):
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
                          'employee'
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
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    try:
        employee_id=Employee.objects.get(id=employee)
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
    
    commission_setting =CommissionSchemeSetting.objects.create(
        user = user,
        business = business ,
        employee = employee_id,
        commission_cycle = commission_cycle,
    )
    
    if service_comission is not None:
        if type(service_comission) == str:
            #service_comission = service_comission.replace("'" , '"')
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
                    commission =  commission_setting,
                    from_value =from_value,
                    to_value = to_value,
                    commission_percentage = commission_per,
                    symbol = symbol,
                    category_comission = 'Service',
                )
            except Exception as err:
                ExceptionRecord.objects.create(
                    text = f'Service data {str(err)}'
                )
        
    if product_comission is not None:
        if type(product_comission) == str:
            #product_comission = product_comission.replace("'" , '"')
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
                    commission =  commission_setting,
                    from_value = from_value,
                    to_value = to_value,
                    commission_percentage = commission_per,
                    symbol = symbol,
                    category_comission = 'Retail',
                )
            except Exception as err:
                ExceptionRecord.objects.create(
                    text = f'Retail data {str(err)}'
                )
        
    if voucher_comission is not None:
        
        if type(voucher_comission) == str:
            #voucher_comission = voucher_comission.replace("'" , '"')
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
                    commission =  commission_setting,
                    from_value = from_value,
                    to_value = to_value,
                    commission_percentage = commission_per,
                    symbol = symbol,
                    category_comission = 'Voucher',
                )           
            except Exception as err:
                ExceptionRecord.objects.create(
                    text = f'Both data {str(err)}'
                )
            
    serializers= CommissionSerializer(commission_setting, context={'request' : request})
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Commission Created Successfully!',
                    'error_message' : None,
                    'commission' : serializers.data,
                }
            },
            status=status.HTTP_201_CREATED
        ) 
    
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_commission(request): 
    # business = request.GET.get('business', None)
    # if business is None:
    #    return Response(
    #         {
    #             'status' : False,
    #             'status_code' : StatusCodes.MISSING_FIELDS_4001,
    #             'status_code_text' : 'MISSING_FIELDS_4001',
    #             'response' : {
    #                 'message' : 'Invalid Data!',
    #                 'error_message' : 'fields are required.',
    #                 'fields' : [
    #                     'business',
    #                 ]
    #             }
    #         },
    #         status=status.HTTP_400_BAD_REQUEST
    #     )
       
    # try:
    #     business=Business.objects.get(id=business)
    # except Exception as err:
    #     return Response(
    #         {
    #                 'status' : False,
    #                 'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
    #                 'response' : {
    #                 'message' : 'Business not found',
    #                 'error_message' : str(err),
    #             }
    #         }
    #     )
       
    # commission , created =  CommissionSchemeSetting.objects.get_or_create(
    #     business=business,
    #     user=business.user,
    #     )
    commission = CommissionSchemeSetting.objects.all().order_by('-created_at')   
    serializer = CommissionSerializer(commission, many = True, context={'request' : request})
    
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

@api_view(['GET'])
@permission_classes([AllowAny])
def get_employee_commission(request): 
    employe_id = request.GET.get('id', None)
    
    if not all([employe_id ]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                          'id'
                            ]
                    }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        employe = Employee.objects.get(id = str(employe_id))
    except Exception as err:
        pass
    try:
        commission = CommissionSchemeSetting.objects.get(employee = employe)
        serializer = CommissionSerializer(commission, context={'request' : request})
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'response' : {
                    'message' : 'Commission Scheme Setting',
                    'error_message' : f'error {str(err) } employee id {employe}',
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All  Employee Commission',
                'error_message' : None,
                'commission' : serializer.data
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
        commission = CommissionSchemeSetting.objects.get(id=commission_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Commission ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    commission.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Commission deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )

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
                    commision_ser= CategoryCommission.objects.get(id=id)
                    if bool(isDeleted) == True:
                        commision_ser.delete()
                        pass
                    
                    commision_ser.from_value = from_value
                    commision_ser.to_value = to_value
                    commision_ser.commission_percentage = commission_per
                    commision_ser.symbol = symbol
                    commision_ser.save()           
                    
                except Exception as err:
                    pass
            else:
                CategoryCommission.objects.create(
                    commission =  commission,
                    from_value = from_value,
                    to_value = to_value,
                    commission_percentage = commission_per,
                    symbol = symbol,
                    category_comission = 'Service',
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
                    commision_ser= CategoryCommission.objects.get(id=id)
                    if bool(isDeleted) == True:
                        commision_ser.delete()
                        pass
                    
                    commision_ser.from_value = from_value
                    commision_ser.to_value = to_value
                    commision_ser.commission_percentage = commission_per
                    commision_ser.symbol = symbol
                    commision_ser.save()           
                    
                except Exception as err:
                    pass
            else:
                CategoryCommission.objects.create(
                    commission =  commission,
                    from_value = from_value,
                    to_value = to_value,
                    commission_percentage = commission_per,
                    symbol = symbol,
                    category_comission = 'Retail',
                )
                
    if voucher_comission is not None:
        if type(voucher_comission) == str:
            voucher_comission = voucher_comission.replace("'" , '"')
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
                    commision_ser= CategoryCommission.objects.get(id=id)
                    if bool(isDeleted) == True:
                        commision_ser.delete()
                        pass
                    
                    commision_ser.from_value = from_value
                    commision_ser.to_value = to_value
                    commision_ser.commission_percentage = commission_per
                    commision_ser.symbol = symbol
                    commision_ser.save()           
                    
                except Exception as err:
                    print(str(err))
            else:
                CategoryCommission.objects.create(
                    commission =  commission,
                    from_value = from_value,
                    to_value = to_value,
                    commission_percentage = commission_per,
                    symbol = symbol,
                    category_comission = 'Voucher',
                )    
    try:
        employee_id=Employee.objects.get(id=employee)
        commission.employee = employee_id
        commission.save()
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
        
    serializer = CommissionSerializer(commission, data=request.data, partial=True,  context={'request' : request})
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
    serializers= AssetSerializer(asset, context={'request' : request})
    
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
    staff_id = request.data.get('staff_id', None)
    document = request.data.get('document', None)
    is_active = request.data.get('is_active', None)
    
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
            asset = asset,
            document = document
        )
    serializer = AssetSerializer(asset, data=request.data, partial=True, context={'request' : request})
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_vacation(request):
    user = request.user
    business_id = request.data.get('business', None)
    
    employee = request.data.get('employee', None)
    from_date = request.data.get('from_date', None)
    to_date = request.data.get('to_date', None)
    note = request.data.get('note', None)
    
    if not all([business_id,employee ]):
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
        employee_id=Employee.objects.get(id=employee)
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
    vacation = Vacation.objects.create(
        user = user,
        business = business ,
        employee = employee_id,
        
        from_date =from_date,
        to_date = to_date,
        note = note,
    )
    
    serializers= VacationSerializer(vacation, context={'request' : request})
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Vacation Created Successfully!',
                    'error_message' : None,
                    'vacation' : serializers.data,
                }
            },
            status=status.HTTP_201_CREATED
        ) 
    
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_vacation(request):
    vacation = Vacation.objects.all().order_by('-created_at')   
    serializer = VacationSerializer(vacation, many = True,context={'request' : request})
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Vacation',
                'error_message' : None,
                'vacation' : serializer.data
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_vacation(request):
    vacation_id = request.data.get('id', None)
    if vacation_id is None: 
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
        vacation = Vacation.objects.get(id=vacation_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Vacation ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    vacation.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Vacation deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_vacation(request):
    vacation_id = request.data.get('vacation_id', None)
    employee = request.data.get('employee', None)
    note = request.data.get('note', None)
    
    if vacation_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'vacation_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        vacation = Vacation.objects.get(id = vacation_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code_text' : 'INVALID_VACATION_ID',
                'response' : {
                    'message' : 'Vacation Not Found',
                    'error_message' : str(err),
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
    serializer = VacationSerializer(vacation, data=request.data, partial=True,context={'request' : request})
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Vacation Serializer Invalid',
                'error_message' : serializer.errors,
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
                'message' : 'Vacation Update Successfully',
                'error_message' : None,
                'vacation' : serializer.data
            }
        },
        status=status.HTTP_200_OK
        )
    
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
    to_date = request.data.get('to_date', None)
    note = request.data.get('note', None)

    is_vacation = request.data.get('is_vacation', None)
    
    is_leave = request.data.get('is_leave', None)
    is_off = request.data.get('is_off', None)
    
    if not all([business_id,employee ]):
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
        employee_id=Employee.objects.get(id=employee, is_deleted = False)
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
    
    # from_date ='2023-01-04'
    # to_date ='2023-01-06'
    
    from_date = datetime.strptime(from_date, "%Y-%m-%d")
    to_date = datetime.strptime(to_date, "%Y-%m-%d")
    diff = to_date - from_date 
    #print(diff.days)
    working_sch = None
    days = int(diff.days)

    empl_vacation = Vacation(
        business = business,
        employee = employee_id,
        from_date = from_date,
        to_date = to_date,
        note = note
    )
    if days > 0 :
        for i, value in enumerate(range(days+1)):
            if i == 0:
                from_date = from_date + timedelta(days=i)
            else:
                from_date = from_date + timedelta(days=1)
            try:
                working_sch = EmployeDailySchedule.objects.get(
                    employee = employee_id,   
                    date = from_date
                )
            except Exception as err:
                pass
            
            if working_sch is not None:
                #date_obj = datetime.fromisoformat(from_date)
                
                working_sch.is_vacation = True
                empl_vacation.save()
                working_sch.vacation = empl_vacation
                working_sch.from_date = from_date
                working_sch.save()
                working_sch = None
                
            else:   
                working_schedule = EmployeDailySchedule.objects.create(
                    user = user,
                    business = business ,
                    employee = employee_id,
                    day = day,
                    start_time = start_time,
                    end_time = end_time,
                    start_time_shift = start_time_shift,
                    end_time_shift = end_time_shift,
                    
                    date = from_date,
                    from_date =from_date,
                    to_date = to_date,
                    note = note,
                    
                )    
                if is_vacation is not None:
                    working_schedule.is_vacation = True
                    empl_vacation.save()
                    working_schedule.vacation = empl_vacation
                else:
                    working_schedule.is_vacation = False
                    
                if is_leave is not None:
                    working_schedule.is_leave = True
                else:
                    working_schedule.is_leave = False
                if is_off is not None:
                    working_schedule.is_off = True
                else:
                    working_schedule.is_off = False
                
                working_schedule.save()
            
    all_employe= EmployeDailySchedule.objects.all().order_by('created_at')
    serialized = ScheduleSerializer(all_employe, many=True, context={'request' : request})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Schedule',
                'error_message' : None,
                'schedule' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
        
    # serializers= ScheduleSerializer(working_schedule, context={'request' : request})
    
    # return Response(
    #         {
    #             'status' : True,
    #             'status_code' : 201,
    #             'response' : {
    #                 'message' : 'Working Schedule Created Successfully!',
    #                 'error_message' : None,
    #                 'schedule' : serializers.data,
    #             }
    #         },
    #         status=status.HTTP_201_CREATED
    #     ) 



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
    to_date = request.data.get('to_date', None)
    note = request.data.get('note', None)

    is_vacation = request.data.get('is_vacation', None)
    
    is_leave = request.data.get('is_leave', None)
    is_off = request.data.get('is_off', None)
    
    if not all([business_id,employee ]):
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
        employee_id=Employee.objects.get(id=employee, is_deleted = False)
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
    
    # from_date ='2023-01-04'
    # to_date ='2023-01-06'
    
    from_date = datetime.strptime(from_date, "%Y-%m-%d")
    to_date = datetime.strptime(to_date, "%Y-%m-%d")
    diff = to_date - from_date 
    #print(diff.days)
    working_sch = None
    days = int(diff.days)

    empl_absence = Vacation(
        business = business,
        employee = employee_id,
        from_date = from_date,
        to_date = to_date,
        note = note,
        holiday_type = 'Absence'
    )
    if days > 0 :
        for i, value in enumerate(range(days+1)):
            if i == 0:
                from_date = from_date + timedelta(days=i)
            else:
                from_date = from_date + timedelta(days=1)
            try:
                working_sch = EmployeDailySchedule.objects.get(
                    employee = employee_id,   
                    date = from_date.strftime('%Y-%m-%d')
                )
            except Exception as err:
                pass
            
            if working_sch is not None:
                #date_obj = datetime.fromisoformat(from_date)
                
                working_sch.is_leave = True
                empl_absence.save()
                # working_sch.is_leave = empl_absence
                working_sch.from_date = from_date.strftime('%Y-%m-%d')
                working_sch.save()
                # working_sch = None
                
            else:   
                working_schedule = EmployeDailySchedule.objects.create(
                    user = user,
                    business = business ,
                    employee = employee_id,
                    day = day,
                    start_time = start_time,
                    end_time = end_time,
                    start_time_shift = start_time_shift,
                    end_time_shift = end_time_shift,
                    
                    date = from_date,
                    from_date =from_date.strftime('%Y-%m-%d'),
                    to_date = to_date.strftime('%Y-%m-%d'),
                    note = note,
                    
                )    
                if is_vacation is not None:
                    working_schedule.is_vacation = True
                else:
                    working_schedule.is_vacation = False
                    
                if is_leave is not None:
                    working_schedule.is_leave = True
                    empl_absence.save()
                    working_schedule.vacation = empl_absence
                else:
                    working_schedule.is_leave = False

                if is_off is not None:
                    working_schedule.is_off = True
                else:
                    working_schedule.is_off = False
                
                working_schedule.save()
            
    # all_employe= EmployeDailySchedule.objects.all().order_by('created_at')
    serialized = NewAbsenceSerializer(empl_absence, context={'request' : request})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Absense Schedule',
                'error_message' : None,
                'schedule' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
        
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_workingschedule(request):
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

    is_vacation = request.data.get('is_vacation', None)
    
    is_leave = request.data.get('is_leave', None)
    is_off = request.data.get('is_off', None)
    # is_absense = request.data.get('is_leave', None)
    
    if not all([business_id,employee ]):
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
        employee_id=Employee.objects.get(id=employee, is_deleted = False)
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
            
    working_schedule = EmployeDailySchedule.objects.create(
        user = user,
        business = business ,
        employee = employee_id,
        day = day,
        
        start_time = start_time,
        end_time = end_time,
        start_time_shift = start_time_shift,
        end_time_shift = end_time_shift,
        
        from_date =from_date,
        to_date = to_date,
        note = note,
        
        date = date,
        
    )    
    if is_vacation is not None:
        working_schedule.is_vacation = True
    else:
        working_schedule.is_vacation = False
        
    if is_leave is not None:
        working_schedule.is_leave = True
    else:
        working_schedule.is_leave = False
    if is_off is not None:
        working_schedule.is_off = True
    else:
        working_schedule.is_off = False
    
    # if is_absense is not None:
    #     working_schedule.is_leave = True
    # else:
    #     working_schedule.is_leave = False

    working_schedule.save()
    serializers= ScheduleSerializer(working_schedule, context={'request' : request})
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Working Schedule Created Successfully!',
                    'error_message' : None,
                    'schedule' : serializers.data,
                }
            },
            status=status.HTTP_201_CREATED
        ) 

# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_workingschedule(request):
#     all_employe= EmployeDailySchedule.objects.all().order_by('created_at')
#     serialized = NewScheduleSerializer(all_employe, many=True, context={'request' : request})
#     return Response(
#         {
#             'status' : 200,
#             'status_code' : '200',
#             'response' : {
#                 'message' : 'All Schedule',
#                 'error_message' : None,
#                 'schedule' : serialized.data
#             }
#         },
#         status=status.HTTP_200_OK
#     )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_vacations(request):
    # employee_id = request.data.get('employee', None)
    location = request.GET.get('location', None)

    if not all([location]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Missing Fields',
                    'fields' : [
                        'location',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # try: 
    #     employee = Employee.objects.get(id=employee_id, is_deleted=False)
    # except Exception as err:
    #     return Response(
    #             {
    #                 'status' : False,
    #                 'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
    #                 'status_code_text' : 'INVALID_EMPLOYEE_4025',
    #                 'response' : {
    #                     'message' : 'Employee Not Found',
    #                     'error_message' : str(err),
    #                 }
    #             },
    #             status=status.HTTP_404_NOT_FOUND
    #         )
    try:
        location =  BusinessAddress.objects.get(id =location)
    except Exception as err:
        return Response(
            {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                    'response' : {
                        'message' : 'location is Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
        )
    
    # employee= Employee.objects.get(id = employee_id.id, is_deleted=False, is_blocked=False)

    allvacations = Vacation.objects.filter(
        # employee = employee, 
        employee__location = location,
        is_active = True,  
        
    )
    
    serialized = NewVacationSerializer(allvacations, many=True, context={'request' : request})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Schedule',
                'error_message' : None,
                'vacations' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_absence(request):
    location = request.GET.get('location', None)

    if not all([location]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Missing Fields',
                    'fields' : [
                        'location',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # try: 
    #     employee = Employee.objects.get(id=employee_id, is_deleted=False)
    # except Exception as err:
    #     return Response(
    #             {
    #                 'status' : False,
    #                 'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
    #                 'status_code_text' : 'INVALID_EMPLOYEE_4025',
    #                 'response' : {
    #                     'message' : 'Employee Not Found',
    #                     'error_message' : str(err),
    #                 }
    #             },
    #             status=status.HTTP_404_NOT_FOUND
    #         )
    try:
        location =  BusinessAddress.objects.get(id =location)
    except Exception as err:
        return Response(
            {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'status_code_text' : 'BUSINESS_NOT_FOUND_4015',
                    'response' : {
                        'message' : 'location is Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
        )
    
    # employee= Employee.objects.get(id = employee_id.id, is_deleted=False, is_blocked=False)

    allvacations = Vacation.objects.filter(
        # employee = employee, 
        employee__location = location,
        holiday_type ='Absence',
        is_active = True, 
        
    )
    
    serialized = NewAbsenceSerializer(allvacations, many=True, context={'request' : request})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Absence Schedule',
                'error_message' : None,
                'absences' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_workingschedule(request):
    schedule_id = request.data.get('id', None)
    if schedule_id is None: 
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
        schedule = EmployeDailySchedule.objects.get(id=schedule_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Schedule ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    schedule.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Schedule deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )  


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_absence(request):
    schedule_id = request.data.get('id', None)
    if schedule_id is None: 
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
        schedule = EmployeDailySchedule.objects.get(id=schedule_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Absense Schedule ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    schedule.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Absense Schedule deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )  


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_absence(request): 
    schedule_id = request.data.get('schedule_id', None)
    employee = request.data.get('employee', None)
    
    if schedule_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'schedule_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        schedule = EmployeDailySchedule.objects.get(id = schedule_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code_text' : 'INVALID_SCHEDULE_ID',
                'response' : {
                    'message' : 'Absense Schedule Not Found',
                    'error_message' : str(err),
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
    serializer = ScheduleSerializer(schedule, data=request.data, partial=True,context={'request' : request})
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Schedule Serializer Invalid',
                'error_message' : serializer.errors,
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
                'message' : 'Schedule Updated Successfully',
                'error_message' : None,
                'schedule' : serializer.data
            }
        },
        status=status.HTTP_200_OK
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_workingschedule(request): 
    schedule_id = request.data.get('schedule_id', None)
    employee = request.data.get('employee', None)
    
    if schedule_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'schedule_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        schedule = EmployeDailySchedule.objects.get(id = schedule_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code_text' : 'INVALID_SCHEDULE_ID',
                'response' : {
                    'message' : 'Schedule Not Found',
                    'error_message' : str(err),
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
    serializer = ScheduleSerializer(schedule, data=request.data, partial=True,context={'request' : request})
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Schedule Serializer Invalid',
                'error_message' : serializer.errors,
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
                'message' : 'Schedule Updated Successfully',
                'error_message' : None,
                'schedule' : serializer.data
            }
        },
        status=status.HTTP_200_OK
        )

    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_employe_account(request):
    employee_id = request.data.get('employee_id', None)
    tenant_id = request.data.get('tenant_id', None)
    password = request.data.get('password', None)
    
    data = []
    
    if not all([employee_id,tenant_id, password]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'employee_id',
                        'tenant_id',
                        'password',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        employe = Employee.objects.get(id = employee_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'status_code_text' : 'Invalid Data',
                'response' : {
                    'message' : 'Invalid employee Id',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )  
    try:
        tenant_id = Tenant.objects.get(id = tenant_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'status_code_text' : 'Invalid Data',
                'response' : {
                    'message' : 'Invalid Tenat Id',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )  
    
    try:
        username = employe.email.split('@')[0]
        try:
            user_check = User.objects.get(username = username)
        except Exception as err:
            #data.append(f'username user is client errors {str(err)}')
            pass
        else:
            username = f'{username} {len(User.objects.all())}'
            data.append(f'username user is {username}')
    except Exception as err:
        data.append(f'Employee errors {str(err)}')
    
    user = User.objects.create(
                first_name = str(employe.full_name),
                username = username,
                email = str(employe.email),
                is_email_verified = True,
                is_active = True,
                mobile_number = str(employe.mobile_number),
            )
    account_type = AccountType.objects.create(
            user = user,
            account_type = 'Employee'
        )
    user.set_password(password)
    user.save()
    
    with tenant_context(Tenant.objects.get(schema_name = 'public')):
        try:
            username = employe.email.split('@')[0]
            try:
                user_check = User.objects.get(username = username)
            except Exception as err:   
                #data.append(f'username user is client errors {str(err)}')
                pass
            else:
                username = f'{username} {len(User.objects.all())}'
                data.append(f'username user is {username}')
        except Exception as err:
            data.append(f'Employee errors {str(err)}')
        user = User.objects.create(
                first_name = str(employe.full_name),
                username = username,
                email = str(employe.email),
                is_email_verified = True,
                is_active = True,
                mobile_number = str(employe.mobile_number),
            )        
        user_client = EmployeeTenantDetail.objects.create(
            user = user,
            tenant = tenant_id,
            is_tenant_staff = True
        )
        account_type = AccountType.objects.create(
            user = user,
            account_type = 'Employee'
        )
        user.set_password(password)
        user.save()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : 'Saved Data',
            'response' : {
                'message' : 'Successfully Employee Created',
                'error_message' : None,
                'errors': data,
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def employee_login(request):
    email = request.data.get('email', None)
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    tenant_id = request.data.get('tenant_id', None)
    
    data = []
    
    if not all([email, password]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
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
            user_account_type__account_type = 'Employee'
        )
        
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_CREDENTIALS_4013,
                'status_code_text' : 'INVALID_CREDENTIALS_4013',
                'response' : {
                    'message' : 'User does not exist with this email',
                    'error_message' : str(err),
                    'fields' : ['email']
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        employee_tenant = EmployeeTenantDetail.objects.get(user__username = user_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 200,
                'response' : {
                    'message' : 'Authenticated',
                    'data' : f'{str(err)} {str(user_id.id)} {str(user_id)} {user_id} {data}'
                }
            },
            status=status.HTTP_200_OK
        )
        
    with tenant_context(employee_tenant.tenant):
        user_id = User.objects.get(
            email=email,
            is_deleted=False,
            #user_account_type__account_type = 'Employee'
        )
        user = authenticate(username=user_id.username, password=password)
        if user is None:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_CREDENTIALS_4013,
                    'status_code_text' : 'INVALID_CREDENTIALS_4013',
                    'response' : {
                        'message' : 'Incorrect Password',
                        'fields' : 'Password' #f'password {user_id.username} pass {password}'
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            token = Token.objects.get(user=user)
        except Token.DoesNotExist:
           token = Token.objects.create(user=user)
            
        serialized = UserEmployeeSerializer(user, context = {'tenant': employee_tenant.tenant, 'token': token.key })
    
    return Response(
            {
                'status' : False,
                'status_code' : 200,
                'response' : {
                    'message' : 'Authenticated',
                    'data' : serialized.data
                }
            },
            status=status.HTTP_200_OK
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def resend_password(request):
    email = request.data.get('email', None)
    password = request.data.get('password', None)
    old_password = request.data.get('old_password', None)

    if not email or not password :
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
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
            #user_account_type__account_type = 'Employee'
        )
        
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_CREDENTIALS_4013,
                'status_code_text' : 'INVALID_CREDENTIALS_4013',
                'response' : {
                    'message' : 'User does not exist with this email',
                    'error_message' : str(err),
                    'fields' : ['email']
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        employee_tenant = EmployeeTenantDetail.objects.get(user__username = user_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 200,
                'response' : {
                    'message' : 'Authenticated',
                    'data' : str(err),
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
                'status' : False,
                'status_code' : StatusCodes.INVALID_CREDENTIALS_4013,
                'status_code_text' : 'INVALID_CREDENTIALS_4013',
                'response' : {
                    'message' : 'User does not exist with this email',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        ) 
        if not len(password) < 8:
            if old_password is not None:
                #if old_password == user.password:
                if user.check_password(old_password):
                #raise serializers.ValidationError("Old password does't match.")
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
        
        
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get('email', None)
    code_for = 'Email'
    
    try:
        user_id = User.objects.get(
            email=email,
            is_deleted=False,
            #user_account_type__account_type = 'Employee'
        )
        
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_CREDENTIALS_4013,
                'status_code_text' : 'INVALID_CREDENTIALS_4013',
                'response' : {
                    'message' : 'User does not exist with this email',
                    'error_message' : str(err),
                    'fields' : ['email']
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        employee_tenant = EmployeeTenantDetail.objects.get(user__username = user_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 200,
                'response' : {
                    'message' : 'Authenticated',
                    'data' : str(err),
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
        
        html_file = render_to_string("otp_email.html", {'user_name': user.username,'otp': otp.code, 'email':user.email})
        text_content = strip_tags(html_file)
    
        email = EmailMultiAlternatives(
            'Email Verification OTP',
            text_content,
            settings.EMAIL_HOST_USER,
            to = [user.email]
        )
        
        email.attach_alternative(html_file, "text/html")
        email.send()
    return Response({'success': True,
                     'message': 'Verification code has been sent to your provided Email'},
                    status=status.HTTP_200_OK)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    email = request.data.get('email', None)
    code = request.data.get('code', None)
    
    if not all([code, email]) :
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
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
            #user_account_type__account_type = 'Employee'
        )
        
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_CREDENTIALS_4013,
                'status_code_text' : 'INVALID_CREDENTIALS_4013',
                'response' : {
                    'message' : 'User does not exist with this email',
                    'error_message' : str(err),
                    'fields' : ['email']
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        employee_tenant = EmployeeTenantDetail.objects.get(user__username = user_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 200,
                'response' : {
                    'message' : 'Authenticated',
                    'data' : str(err),
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
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_OTP_4006,
                    'status_code_text' : 'INVALID_OTP_4006',
                    'response' : {
                        'message' : 'OTP does not correct',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Email Verify ',
                'error' : None   
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
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Employee id are required',
                    'fields' : [
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
    
    serialized = SingleEmployeeInformationSerializer(employee_id, context={'request' : request} )
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Employee',
                'error_message' : None,
                'employees' : serialized.data
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
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Employee id are required',
                    'fields' : [
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
    #all_employe= Employee.objects.get(is_deleted=False, is_blocked=False).order_by('-created_at')
    serialized = WorkingScheduleSerializer(employee_id, context={'request' : request,} )
   
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

@api_view(['POST'])
@permission_classes([AllowAny])
def set_password(request):
    user_id = request.data.get('user_id', None) 
    password = request.data.get('password', None)
        
    try:
        user = User.objects.get(id = str(user_id))
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code_text' : 'INVALID_USER_ID',
                    'response' : {
                        'message' : 'User Not Found',
                        'error_message' : str(err),
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
    with tenant_context(Tenant.objects.get(schema_name = 'public')):
        try:
            user = User.objects.get(email = user.email)
        except Exception as err:
            return Response(
                    {
                        'status' : False,
                        'status_code_text' : 'INVALID_USER_EMAIL',
                        'response' : {
                            'message' : 'User Not Found',
                            'error_message' : str(err),
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
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Password Set Successfully!',
                'error_message' : None,
            }
        },
        status=status.HTTP_200_OK
    )
            