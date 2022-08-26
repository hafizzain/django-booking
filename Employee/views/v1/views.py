from django.shortcuts import render
from Employee.models import( Employee , EmployeeProfessionalInfo ,
                        EmployeePermissionSetting,  EmployeeModulePermission
                        , EmployeeMarketingPermission , StaffGroup 
                        , StaffGroupModulePermission
                        )
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from Employee.serializers import( EmployeSerializer , EmployeInformationsSerializer
                          , EmployPermissionSerializer,  EmployeModulesSerializer
                          ,  EmployeeMarketingSerializers, StaffGroupSerializers , 
                          StaffermisionSerializers
                          
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
    # sourcery skip: avoid-builtin-shadow
    user = request.user     
    
    full_name= request.data.get('full_name', None)
    employee_id= request.data.get('employee_id', None)
    email= request.data.get('email', None)
    image = request.data.get('image', None)
    
    mobile_number= request.data.get('mobile_number', None)    
    dob= request.data.get('dob', None)
    gender = request.data.get('gender' , None)
    

    postal_code= request.data.get('postal_code' , None)
    address= request.data.get('address' , None)
    joining_date = request.data.get('joining_date', None)
    to_present = request.data.get('to_present', None)
    ending_date= request.data.get('ending_date',None)
    
    
    #UserInformation
    designation = request.data.get('designation', None)
    income_type = request.data.get('income_type', None)
    salary = request.data.get('salary', None)
    services = request.data.get('services', None)
    
    #EmployeePermissionSetting
    allow_calendar_booking= request.data.get('allow_calendar_booking', False)
    access_calendar= request.data.get('access_calendar', False)
    change_calendar_color= request.data.get('change_calendar_color',False)
    
    
    #EmployeeModulePermission
    access_reports=request.data.get('access_reports', False)
    access_sales= request.data.get('access_sales', False)
    access_inventory= request.data.get('access_inventory' , False)
    access_expenses= request.data.get('access_expenses', False)
    access_products= request.data.get('access_products', False)
    
    #EmployeeMarketingPermission
    access_voucher=request.data.get('access_voucher', False)
    access_member_discount= request.data.get('access_member_discount', False)
    access_invite_friend=request.data.get('access_invite_friend' , False)
    access_loyalty_points=request.data.get('access_loyalty_points' , False)
    access_gift_cards=request.data.get('access_gift_cards' , False)
    
    business_id= request.data.get('business', None)    
    country_id = request.data.get('country', None)   
    state_id = request.data.get('state', None)         
    city_id = request.data.get('city', None)
   
    if not all([
        business_id, full_name, image ,employee_id, email, mobile_number, dob ,gender, country_id , state_id ,city_id ,postal_code ,address ,joining_date, to_present, ending_date ]): 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        
                        'business_id',
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
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    business=Business.objects.get(id=business_id)
    try:
       country = Country.objects.get(id=country_id)
    except Country.DoesNotExist:
       country = None   
        
    try:
       state= State.objects.get(id=state_id)
    except State.DoesNotExist:
        state = None
    
    try:
        city = City.objects.get(id=city_id)
    except City.DoesNotExist:
        city = None    
    
    employee= Employee.objects.create(
        # id=id,
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
        to_present = to_present,
        ending_date= ending_date,
    )
        
    #EmployeInformations
    employeinformations = EmployeeProfessionalInfo.objects.create(
        employee=employee,
        designation= designation,
        income_type= income_type,
        salary= salary,
        #services= services,
    )
    EmployeInformations= EmployeInformationsSerializer(employeinformations)
    
    #EmployeePermissionSetting
    employeePermission = EmployeePermissionSetting.objects.create(
        employee = employee,
        allow_calendar_booking =allow_calendar_booking, 
        access_calendar= access_calendar,
        change_calendar_color = change_calendar_color
    )
    employeePerSetting= EmployPermissionSerializer(employeePermission)
    
    #EmployeeModulePermission
    employeModulePermission = EmployeeModulePermission.objects.create(
        employee=employee,
        access_reports=access_reports,
        access_sales=access_sales,
        access_inventory=access_inventory,
        access_expenses=access_expenses,
        access_products=access_products,       
        
    )
    ModulesSerializer= EmployeModulesSerializer(employeModulePermission)
    
    #EmployeeMarketingSerializers
    EmployeeMarketing = EmployeeMarketingPermission.objects.create(
        employee= employee,
        access_voucher=access_voucher,
        access_member_discount= access_member_discount,
        access_invite_friend= access_invite_friend,
        access_loyalty_points= access_loyalty_points,
        access_gift_cards= access_gift_cards,
        
    )
    serialized = EmployeSerializer(employee , context={'request' : request})
    return Response(
        {
            'status' : True,
            'status_code' : 201,
            'response' : {
                'message' : 'Employees Added!',
                'error_message' : None,
                'employees' : serialized.data
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
        id = request.data.get('id')
        employee = Employee.objects.get(id=id)
        try:
           
            serializer =EmployeSerializer(employee, data=request.data, partial=True)
            
            Employe_Informations= EmployeeProfessionalInfo.objects.get(employee=employee)
            serializer_info= EmployeInformationsSerializer(Employe_Informations,  data=request.data, partial=True)
            if serializer_info.is_valid():
               serializer_info.save()
            else:
                return Response(
            {
                'status' : False,
                'status_code' : 400,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : str(serializer_info.errors),
                    'product' : serializer_info.data
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
            
            permission= EmployeePermissionSetting.objects.get(employee=employee)
            serializer_permision= EmployPermissionSerializer(permission,  data=request.data, partial=True)
            if serializer_permision.is_valid():
               serializer_permision.save()
            else:
                return Response(
            {
                'status' : False,
                'status_code' : 400,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : str(serializer_permision.errors),
                    'product' : serializer_permision.data
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
            
            Module_Permission= EmployeeModulePermission.objects.get(employee=employee)
            serializer_Module = EmployeModulesSerializer(Module_Permission,  data=request.data, partial=True)
            if serializer_Module.is_valid():
               serializer_Module.save()
            else:
                return Response(
            {
                'status' : False,
                'status_code' : 400,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : str(serializer_Module.errors),
                    'product' : serializer_Module.data
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
                 
            Marketing_Permission= EmployeeMarketingPermission.objects.get(employee=employee)
            serializer_Marketing= EmployeeMarketingSerializers(Marketing_Permission,  data=request.data, partial=True)
            if serializer_Marketing.is_valid():
                serializer_Marketing.save()
            else:
                return Response(
            {
                'status' : False,
                'status_code' : 400,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : str(serializer_Marketing.errors),
                    'product' : serializer_Marketing.data
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
            
            if serializer.is_valid():
                serializer.save()
                return Response({"error":False,"data":serializer.data}, status=status.HTTP_200_OK)
            return  Response(
            {
                'status' : False,
                'status_code' : 400,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : str(serializer.errors),
                    'product' : serializer.data
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

        except Exception as e:
            return Response({"error":repr(e)},status=status.HTTP_400_BAD_REQUEST)
    
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_staff(request):
        user = request.user     
        business_id= request.data.get('business', None)
        
        name = request.data.get('name', None)
        employee_id = request.data.get('employees', None)
        
        is_active= request.data.get('is_active' , False)
        
        if not all([ business_id, name, employee_id ]):
              return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                          'business_id',
                          'name',
                          'employee_id',
                          
                            ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        business=Business.objects.get(id=business_id)
        employees= Employee.objects.get(id=employee_id)
        
        staff_group= StaffGroup.objects.create(
            user=user,
            business= business, 
            name= name,
            employees= employees
        
        )
    #     serialized = StaffGroupSerializers(
    #     staff_group, 
    #     many=True, 
    #     context={'employee': employees}
    # ).data

      
        serialized = StaffGroupSerializers(staff_group, many=True)
   
        return Response(
        {
            'status' : True,
            'status_code' : 201,
            'response' : {
                'message' : 'Staff Group a!',
                'error_message' : None,
                'brand' : serialized.data
            }
        },
        status=status.HTTP_201_CREATED
    )
        
        

