from datetime import datetime, timedelta

from Employee.models import Employee, LeaveManagements
from rest_framework.response import Response
from rest_framework import status

def annual_vacation_check(vacation_type=None, employee=None):
    if vacation_type == 'annual':
        now = datetime.now()
        employee_id = Employee.objects.get(id=employee, is_deleted=False)
        created_at = employee_id.created_at
        required_months = LeaveManagements.objects.get(employee_id=employee_id.id)
        required_months = required_months.number_of_months
        required_months = int(required_months)
        months_difference = (now.year - created_at.year) * 12 + now.month - created_at.month
        months_difference = int(months_difference)
        if months_difference < required_months:
            return Response(
                {
                    'status': 400,
                    'status_code': '400',
                    'response': {
                        'message': 'You can not create annual vacation right now ',
                        'error_message': None,
                    }
                },
                status=status.HTTP_200_OK
            )
