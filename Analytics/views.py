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
        serializer_data = list(self.serializer_class(employees, many=True).data)

        MORNING = "Morning"
        AFTERNOON = "Afternoon"
        EVENING = "Evening"
        EMP_MIN_BOOKINGS = 5

        for emp in serializer_data:

            morning = emp['morning_count']
            afternoon = emp['afternoon_count']
            evening = emp['evening_count']

            # declaring messages hint1 and hint2
            emp['overall_hint'] = {
                'message':'',
                'hint1':'',
                'hint2':''
            }

            cal_sum = sum([morning, afternoon, evening])

            if cal_sum > 0:
                
                # Condition 1
                if morning == afternoon == evening == EMP_MIN_BOOKINGS:
                    emp['overall_hint']['message'] = f"Bookings for {emp['full_name']} are steady all day."
                
                # Condition 2
                elif (morning < EMP_MIN_BOOKINGS) and (afternoon < EMP_MIN_BOOKINGS) and (evening < EMP_MIN_BOOKINGS):
                    emp['overall_hint']['message'] = f"{emp['full_name']} has a few bookings in every shift."
                    
                else:
                    # Condition 3
                    if morning < afternoon and afternoon < evening:
                        emp['hint1'] = MORNING
                        emp['hint2'] = AFTERNOON
                    # Condition 4
                    elif afternoon < evening and evening < morning:
                        emp['hint1'] = AFTERNOON
                        emp['hint2'] = EVENING
                    # Condition 5
                    elif evening < morning and morning < afternoon:
                        emp['hint1'] = EVENING
                        emp['hint2'] = MORNING
            else:
                # Condition 6
                emp['overall_hint']['message'] = "Employee is not working good"

        return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Employee Shift Insights',
                'error_message' : None,
                'data' : serializer_data,
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