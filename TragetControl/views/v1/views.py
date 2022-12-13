from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from Employee.models import Employee
from NStyle.Constants import StatusCodes
from rest_framework import status
from Business.models import Business
from TragetControl.models import StaffTarget



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_employee(request):
    user= request.user
    business = request.data.get('business', None)
    employee = request.data.get('employee', None)
    
    month = request.data.get('month', None)
    service_target = request.data.get('service_target', None)
    retail_target = request.data.get('retail_target', None)
    
    if not all([business,employee,month, service_target, retail_target]):
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
                          'month', 
                          'service_target',
                          'retail_target',
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
        
    staff_target = StaffTarget.objects.create(
        user = user,
        business = business_id,
        employee = employee_id,
        month = month,
        service_target = service_target,
        retail_target = retail_target,
    )
    