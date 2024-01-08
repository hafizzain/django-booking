from datetime import datetime, timedelta

from Employee.models import Employee, LeaveManagements
from rest_framework.response import Response
from rest_framework import status


def annual_vacation_check(vacation_type=None, employee=None):
    if vacation_type == 'annual':
        now = datetime.now()
        employee_id = Employee.objects.get(id=employee, is_deleted=False)
        created_at = employee_id.created_at
        employee_leave_management_obj = LeaveManagements.objects.get(employee_id=employee)
        required_months = employee_leave_management_obj.number_of_months
        required_months = int(required_months)
        months_difference = (now.year - created_at.year) * 12 + now.month - created_at.month
        months_difference = int(months_difference)
        if required_months > months_difference:
            return Response(
                {
                    'status': 400,
                    'status_code': '400',
                    'response': {
                        'message': 'Annual leave requests available after {required_months}'.format(
                            required_months=required_months),
                        'error_message': None,
                    }
                },
                status=status.HTTP_200_OK
            )


def check_available_vacation_type(vacation_type=None, employee=None, from_date=None, to_date=None):
    value = 0
    available_value=0
    employee_leave_management_obj = LeaveManagements.objects.get(employee_id=employee)
    if vacation_type == 'medical':
        value = employee_leave_management_obj.medical_leave
    if vacation_type == 'annual':
        value = employee_leave_management_obj.annual_leave
    if vacation_type == 'casual':
        value = employee_leave_management_obj.casual_leave
    from_date = datetime.strptime(from_date, "%Y-%m-%d")
    to_date = datetime.strptime(to_date, "%Y-%m-%d")
    diff = to_date - from_date
    days = int(diff.days)
    available_value = int(value)
    if days > available_value:
        return Response(
            {
                'status': 400,
                'status_code': '400',
                'response': {
                    'message': 'Requests exceed',
                    'error_message': None,
                }
            },
            status=status.HTTP_200_OK
        )
