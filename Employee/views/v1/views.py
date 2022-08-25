from django.shortcuts import render
from Employee.models import( Employee , EmployeeProfessionalInfo ,
                        EmployeePermissionSetting,  EmployeeModulePermission
                        , EmployeeMarketingPermission
                        )
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from Employee.serializers import( EmployeSerializer , EmployeInformationsSerializer
                          , EmployPermissionSerializer,  EmployeModulesSerializer
                          ,  EmployeeMarketingSerializers
                                 
                                 
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
    id = request.data.get('id' , None)
    user = request.user 
    
    business_id= request.data.get('business', None)
    business=Business.objects.get(id=business_id)
    print(business)
    
    
    full_name= request.data.get('full_name', None)
    employee_id= request.data.get('employee_id', None)
    email= request.data.get('email', None)
    
    
    mobile_number= request.data.get('mobile_number', None)
    email_verified= request.data.get('is_email_verified', False)
    mobile_verified= request.data.get('is_mobile_verified', False)
    
    dob= request.data.get('dob', None)
    gender = request.data.get('gender' , None)
    
    country_id = request.data.get('country', None)
    try:
       country = Country.objects.get(id=country_id)
    except Country.DoesNotExist:
       country = None 
    state_id = request.data.get('state', None)
    try:
       state= State.objects.get(id=state_id)
    except State.DoesNotExist:
        state = None
        
    city_id = request.data.get('city', None)
    try:
        city = City.objects.get(id=city_id)
    except City.DoesNotExist:
        city = None    
    postal_code= request.data.get('postal_code' , None)
    address= request.data.get('address' , None)
    joining_date = request.data.get('joining_date', None)
    to_present = request.data.get('to_present', None)
    ending_date= request.data.get('ending_date',None)
    
    is_deleted= request.data.get('is_deleted' , None)
    is_blocked=request.data.get('is_blocked', None)
    created_at = request.data.get('created_at', None)
    updated_at = request.data.get('updated_at', None)
    
    #UserInformation
    designation = request.data.get('designation')
    income_type = request.data.get('income_type')
    salary = request.data.get('salary')
    services = request.data.get('services')
    
    #EmployeePermissionSetting
    allow_calendar_booking= request.data.get('allow_calendar_booking')
    access_calendar= request.data.get('access_calendar')
    change_calendar_color= request.data.get('change_calendar_color')
    
    
    #EmployeeModulePermission
    access_reports=request.data.get('access_reports')
    access_sales= request.data.get('access_sales')
    access_inventory= request.data.get('access_inventory')
    access_expenses= request.data.get('access_expenses')
    access_products= request.data.get('access_products')
    
    #EmployeeMarketingPermission
    access_voucher=request.data.get('access_voucher')
    access_member_discount= request.data.get('access_member_discount')
    access_invite_friend=request.data.get('access_invite_friend')
    access_loyalty_points=request.data.get('access_loyalty_points')
    access_gift_cards=request.data.get('access_gift_cards')
    
    
    if not all([
        business_id, full_name ,employee_id, email, mobile_number, dob ,gender, country , state ,city ,postal_code ,address ,joining_date, to_present, ending_date ]): 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'business id',
                        'full Name',
                        'employee id',
                        'email',
                        'mobile number', 
                        'Date of birth', 
                        'Gender', 
                        'Country', 
                        'State', 
                        'city', 
                        'postal code', 
                        'address' ,
                        'joining_date', 
                        'to_present', 
                        'ending_date'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
            
    
    employee= Employee.objects.create(
        # id=id,
        user=user,
        business=business,
        full_name = full_name,
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
    
    serialized = EmployeSerializer(employee)
    
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