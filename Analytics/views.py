import json
from datetime import date, timedelta
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
        _start_date = str(request.query_params.get('start_date')).split('-')
        _end_date = str(request.query_params.get('end_date')).split('-')
        business_address_id = request.query_params.get('business_address_id')
        emplopyee_ids = request.query_params.get('employees', None)
        emplopyee_ids = self.get_employee_ids(emplopyee_ids)


        start_date = date(int(_start_date[0]), int(_start_date[1]), int(_start_date[2]))
        end_date = date(int(_end_date[0]),int(_end_date[1]), int(_end_date[2]))

        #debugging
        end_date += timedelta(days=1)

        business_address = BusinessAddress.objects.get(id=business_address_id)
        
        # adding business address and date to filter
        insight_filter = Q(employee_daily_insights__business_address=business_address) & \
                         Q(employee_daily_insights__created_at__range=(start_date, end_date)) | \
                         Q(employee_daily_insights__updated_at__range=(start_date, end_date))
        
        employees = Employee.objects.with_daily_booking_insights(emplopyee_ids, insight_filter)
        serializer_data = list(self.serializer_class(employees,
                                                     many=True,
                                                     context={'request' : request}).data)

        MORNING = "Morning"
        AFTERNOON = "Afternoon"
        EVENING = "Evening"
        EMP_MIN_BOOKINGS = 5

        for emp in serializer_data:

            morning = emp['morning_count']
            afternoon = emp['afternoon_count']
            evening = emp['evening_count']
            emp_name = emp['full_name']
            # declaring messages hint1 and hint2

            cal_sum = sum([morning, afternoon, evening])

            # Early exit from the various conditions
            if cal_sum > 0:
                
                # Condition 1 - Employee is doing great.
                if morning == afternoon == evening == EMP_MIN_BOOKINGS:
                    emp['overall_hint'] = f"Bookings for {emp_name} are steady all day."
                
                # Condition 2 - Employee have few bookings in every shift
                elif (morning < EMP_MIN_BOOKINGS) and \
                     (afternoon < EMP_MIN_BOOKINGS) and \
                     (evening < EMP_MIN_BOOKINGS):
                    
                    emp['overall_hint'] = f"{emp_name} has few bookings in every shift."
                # Other conditions on which we are sennding overall hint about employee
                else:
                    
                    if morning < afternoon:
                        if afternoon < evening:
                            if evening >= EMP_MIN_BOOKINGS and afternoon < EMP_MIN_BOOKINGS:
                                emp['overall_hint'] = f"{emp_name} should busy in the {MORNING} and {AFTERNOON}."
                            else:
                                emp['overall_hint'] = f"{emp_name} should busy in the {MORNING}."
                        elif afternoon > evening:
                            if afternoon >= EMP_MIN_BOOKINGS and evening < EMP_MIN_BOOKINGS:
                                emp['overall_hint'] = f"{emp_name} should busy in the {MORNING} and {EVENING}."
                            else:
                                emp['overall_hint'] = f"{emp_name} should busy in the {MORNING}."
                    
                    if afternoon < evening:
                        if evening < morning:
                            if morning >= EMP_MIN_BOOKINGS and evening < EMP_MIN_BOOKINGS:
                                emp['overall_hint'] = f"{emp_name} should busy in the {AFTERNOON} and {EVENING}."
                            else:
                                emp['overall_hint'] = f"{emp_name} should busy in the {AFTERNOON}."
                        elif evening > morning:
                            if evening >= EMP_MIN_BOOKINGS and morning < EMP_MIN_BOOKINGS:
                                emp['overall_hint'] = f"{emp_name} should busy in the {MORNING} and {AFTERNOON}."
                            else:
                                emp['overall_hint'] = f"{emp_name} should busy in the {AFTERNOON}."

                    if evening < morning:
                        if morning < afternoon:
                            if afternoon >=EMP_MIN_BOOKINGS and morning < EMP_MIN_BOOKINGS:
                                emp['overall_hint'] = f"{emp_name} should busy in the {MORNING} and {EVENING}."
                            else:
                                emp['overall_hint'] = f"{emp_name} should busy in the {EVENING}."
                        elif morning > afternoon:
                            if morning >= EMP_MIN_BOOKINGS and afternoon < EMP_MIN_BOOKINGS:
                                emp['overall_hint'] = f"{emp_name} should busy in the {AFTERNOON} and {EVENING}."
                            else:
                                emp['overall_hint'] = f"{emp_name} should busy in the {EVENING}."

            else:
                # Condition 6 - Employee have zero bookinngs all day.
                emp['overall_hint'] = f"{emp_name} is free all day."

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