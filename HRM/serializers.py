from rest_framework import serializers
from HRM.models import *
from Employee.models import Employee, EmployeDailySchedule
from datetime import datetime
class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'
    
    def create(self, validated_data):
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        # start_date = datetime.strptime(start_date, "%Y-%m-%d")
        # end_date = datetime.strptime(end_date, "%Y-%m-%d")
        all_employees = Employee.objects.all()
        for employee in all_employees: 
            employee_schedule_id = EmployeDailySchedule.objects \
                        .create(is_holiday=True,
                                start_time=start_date,
                                end_time=end_date,
                                employee_id = employee.id,
                                date=end_date)
        return True
        
    