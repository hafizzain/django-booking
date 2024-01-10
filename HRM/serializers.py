from rest_framework import serializers
from HRM.models import *
from Employee.models import Employee, EmployeDailySchedule

class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'
    
    def create(self, validated_data):
        employee_schedule = None
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        
        #get all employees on specific location
        all_employees = Employee.objects \
                        .select_related('user', 'business','country', 'state', 'city') \
                        .prefetch_related('location') \
                        .filter(location=validated_data['location'])
        
        #create holiday schedule for all employees                            
        for employee in all_employees: 
            employee_schedule = EmployeDailySchedule.objects \
                        .create(is_holiday=True,
                                start_time=start_date,
                                end_time=end_date,
                                employee_id = employee.id,
                                date=end_date)
                        
        validated_data['employee_schedule'] = employee_schedule.id
        holiday = Holiday.objects.create(**validated_data)
        return holiday
        
    