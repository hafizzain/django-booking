from django.shortcuts import render
from Employee.models import( Employee , EmployeeProfessionalInfo ,
                        EmployeePermissionSetting,  EmployeeModulePermission
                        , EmployeeMarketingPermission , StaffGroup 
                        , StaffGroupModulePermission, Attendance
                        )
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from Employee.serializers import( EmployeSerializer , EmployeInformationsSerializer
                          , EmployPermissionSerializer,  EmployeModulesSerializer
                          ,  EmployeeMarketingSerializers, StaffGroupSerializers , 
                          StaffpermisionSerializers , AttendanceSerializers
                          
                                 )
from rest_framework import status
from Business.models import Business
from Utility.models import Country, State, City
from Authentication.models import User
from NStyle.Constants import StatusCodes



# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def get_Employees(request):
    all_employe= Employee.objects.all()
    serialized = EmployeSerializer(all_employe, many=True)
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
@permission_classes([IsAuthenticated])
def create_employee(request):
    user = request.user     
    
    full_name= request.data.get('full_name', None)
    employee_id= request.data.get('employee_id', None)
    email= request.data.get('email', None)
    image = request.data.get('image', None)
    
    mobile_number= request.data.get('mobile_number', None)    
    dob= request.data.get('dob', None)
    gender = request.data.get('gender' , 'Male')
    
    postal_code= request.data.get('postal_code' , None)
    address= request.data.get('address' , None)
    joining_date = request.data.get('joining_date', None)
    to_present = request.data.get('to_present', False)
    ending_date= request.data.get('ending_date',None)
    
    
    #UserInformation
    designation = request.data.get('designation', None)
    income_type = request.data.get('income_type', 'Hourly_Rate')
    salary = request.data.get('salary', None)
    # services = request.data.get('services', None)
    
    # #EmployeePermissionSetting
    # allow_calendar_booking= request.data.get('allow_calendar_booking', False)
    # access_calendar= request.data.get('access_calendar', False)
    # change_calendar_color= request.data.get('change_calendar_color',False)
    
    
    # #EmployeeModulePermission
    # access_reports=request.data.get('access_reports', False)
    # access_sales= request.data.get('access_sales', False)
    # access_inventory= request.data.get('access_inventory' , False)
    # access_expenses= request.data.get('access_expenses', False)
    # access_products= request.data.get('access_products', False)
    
    # #EmployeeMarketingPermission
    # access_voucher=request.data.get('access_voucher', False)
    # access_member_discount= request.data.get('access_member_discount', False)
    # access_invite_friend=request.data.get('access_invite_friend' , False)
    # access_loyalty_points=request.data.get('access_loyalty_points' , False)
    # access_gift_cards=request.data.get('access_gift_cards' , False)
    
    business_id= request.data.get('business', None)    
    country_id = request.data.get('country', None)   
    state_id = request.data.get('state', None)         
    city_id = request.data.get('city', None)
   
    if not all([
        business_id, full_name, image ,employee_id, email, mobile_number, dob ,gender, country_id , state_id ,city_id ,postal_code ,address ,joining_date, designation, income_type, salary ]) or ( not to_present and ending_date is None): 
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
                        'image',
                        'email',
                        'mobile_number', 
                        'dob', 
                        'gender', 
                        'country',
                        'state', 
                        'postal_code', 
                        'address' ,
                        'joining_date', 
                        'to_present', 
                        'ending_date',  
                        'designation',
                        'income_type',
                        'salary',
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
        country = Country.objects.get(id=country_id)
        state= State.objects.get(id=state_id)
        city = City.objects.get(id=city_id)
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
        is_active=True
    )
    if not to_present :
        # employee.ending_date = ending_date
        pass
    else:
        employee.to_present = True 
    employee.save()
    data = {}
    employee_serialized = EmployeSerializer(employee , context={'request' : request})
    data.update(employee_serialized.data)

    errors =[]

    employee_p_info = EmployeeProfessionalInfo.objects.create(employee=employee)
    employee_mp = EmployeeModulePermission.objects.create(employee=employee)
    employee_p_setting = EmployeePermissionSetting.objects.create(employee = employee)
    employee_marketing = EmployeeMarketingPermission.objects.create(employee= employee)
    
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
        serializer = EmployeSerializer(employee, data=request.data, partial=True)
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
        serializer_info= EmployeInformationsSerializer(Employe_Informations,  data=request.data, partial=True)
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
         
        permission= EmployeePermissionSetting.objects.get(employee=employee)
        serializer_permision= EmployPermissionSerializer(permission,  data=request.data, partial=True)
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
                
    
        Module_Permission= EmployeeModulePermission.objects.get(employee=employee)
        serializer_Module = EmployeModulesSerializer(Module_Permission,  data=request.data, partial=True)
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
        Marketing_Permission= EmployeeMarketingPermission.objects.get(employee=employee)
        serializer_Marketing= EmployeeMarketingSerializers(Marketing_Permission,  data=request.data, partial=True)
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
                    'message' : 'Update Employee Successfully',
                    'error_message' : None,
                    'Employee' : data
                }
            },
            status=status.HTTP_200_OK
           )
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_staff_group(request):
    
        user = request.user     
        business_id= request.data.get('business', None)
        
        name = request.data.get('name', None)
        employees = request.data.get('employees', None)
        
        is_active= request.data.get('is_active' , False)
        
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
          
                
        staff_group= StaffGroup.objects.create(
            user=user,
            business= business, 
            name= name,
        
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
            import json
            employees = json.loads(employees)
        elif type(employees) == list:
            pass
        
        for usr in employees:
            try:
               employe = Employee.objects.get(id=usr)  
               staff_group.employees.add(employe)
            except Exception as err:
                employees_error.append(str(err))
        staff_group.save()
        serialized = StaffGroupSerializers(staff_group)
       
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
    all_staff_group= StaffGroup.objects.all()
    serialized = StaffGroupSerializers(all_staff_group, many=True)
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
                'message' : 'Staff Group deleted successful',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_staff_group(request):
    staff_id = request.data.get('staff_id', None)
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
    serializer = StaffGroupSerializers(staff_group, data=request.data, partial=True)
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
                'error_message' : str(err),
            }
        },
        status=status.HTTP_404_NOT_FOUND
        ) 
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
    permission_serializer =StaffpermisionSerializers(staff_gp_permissions, data=request.data, partial=True)
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
                }
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