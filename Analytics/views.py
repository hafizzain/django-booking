import json
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from Employee.models import Employee
from Business.models import BusinessAddress


from .serializers import EmployeeDailyInsightsSerializer


class EmployeeDailyInsightsView(APIView):

    serializer_class = EmployeeDailyInsightsSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        business_address_id = request.query_params.get('business_address_id')
        emplopyee_ids = request.query_params.get('employees', None)
        emplopyee_ids = self.get_employee_ids(emplopyee_ids)

        business_address = BusinessAddress.objects.get(id=business_address_id)
        
        insight_filter = Q(business_address=business_address)
        employees = Employee.objects.with_daily_booking_insights(emplopyee_ids, insight_filter)
        serializer = self.serializer_class(employees, many=True)
        return serializer.data
    

    def get_employee_ids(self, employee_ids):
        if type(employee_ids) == str:
            employee_ids = employee_ids.replace("'", '"')
            employee_ids = json.loads(employee_ids)
        elif type(employee_ids) == list:
            pass
    
        employee_ids = [emp['id'] for emp in employee_ids]
        return employee_ids