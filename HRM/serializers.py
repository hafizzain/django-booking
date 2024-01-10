from rest_framework import serializers
from HRM.models import *
from Employee.models import Employee, EmployeDailySchedule

class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'
        
    
    def validate(self, attrs):
        start_date = attrs.get('start_date',None)
        end_date = attrs.get('end_date',None)
        start_date_check = Holiday.objects.filter(start_date=start_date).exists()
        if start_date_check:
            raise serializers.ValidationError({'message':"Holiday already set for this date."})
        if start_date is not None and end_date is not None:
            holiday_check = Holiday.objects.filter(start_date__gte=start_date, end_date__lte=end_date).exists()
            if holiday_check:
                raise serializers.ValidationError({'message':"Holiday already set for this date."})
        return attrs
    
    def create(self, validated_data):
        employee_schedule_id = None
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        all_employees = Employee.objects \
                        .select_related('user', 'business','country', 'state', 'city') \
                        .prefetch_related('location') \
                        .filter(location=validated_data['location'])
                                        
        for employee in all_employees: 
            employee_schedule_id = EmployeDailySchedule.objects \
                        .create(is_holiday=True,
                                start_time=start_date,
                                end_time=end_date,
                                employee_id = employee.id,
                                date=end_date,
                                from_date= start_date,
                                )
        validated_data['employee_schedule_id'] = employee_schedule_id.id
        holiday = Holiday.objects.create(**validated_data)
        return holiday
    