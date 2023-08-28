import json
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from Employee.models import Employee
from Business.models import BusinessAddress


from Employee.serializers import EmployeeDailyInsightSerializer


class EmployeeDailyInsightsView(APIView):

    serializer_class = EmployeeDailyInsightSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        business_address_id = request.query_params.get('business_address_id')
        emplopyee_ids = request.query_params.get('employees', None)
        emplopyee_ids = self.get_employee_ids(emplopyee_ids)

        business_address = BusinessAddress.objects.get(id=business_address_id)
        
        insight_filter = Q(employee_daily_insights__business_address=business_address)
        employees = Employee.objects.with_daily_booking_insights(emplopyee_ids, insight_filter)
        serializer = self.serializer_class(employees, many=True)
        return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Employee Shift Insights',
                'error_message' : None,
                'data' : serializer.data,
            }
        },
        status=status.HTTP_200_OK
    )
    

    def get_employee_ids(self, employee_ids):
        if type(employee_ids) == str:
            employee_ids = employee_ids.replace("'", '"')
            employee_ids = json.loads(employee_ids)
        elif type(employee_ids) == list:
            pass
    
        employee_ids = [emp['id'] for emp in employee_ids]
        return employee_ids