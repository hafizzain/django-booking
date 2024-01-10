from rest_framework import serializers
from HRM.models import *
from Employee.models import Employee, EmployeDailySchedule

class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'
        
    
    def validate(self, attrs):
        start_date = attrs.get('start_date', None)
        end_date = attrs.get('end_date', None)
        location = attrs.get('location', None)

        if start_date is not None:
            # Check if a holiday already exists for the start_date
            start_date_check = Holiday.objects.filter(start_date=start_date, location=location).exists()
            if start_date_check:
                raise serializers.ValidationError({'message': "Holiday already set for this date."})

        # Check if there is any holiday overlapping with the date range
        if start_date is not None and end_date is not None:
            holiday_check = Holiday.objects.filter(start_date__lte=end_date, end_date__gte=start_date, location=location).exists()
            if holiday_check:
                raise serializers.ValidationError({'message': "Holiday already set for this date range."})

        return attrs
    
    def create(self, validated_data):
        employee_schedule_ids = []
        employee_schedule_id = None
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        location = validated_data['location']
        all_employees = Employee.objects \
                        .select_related('user', 'business','country', 'state', 'city') \
                        .prefetch_related('location') \
                        .filter(location=location)
                                        
        for employee in all_employees: 
            employee_schedule_id = EmployeDailySchedule.objects \
                        .create(is_holiday=True,
                                start_time=start_date,
                                end_time=end_date,
                                employee_id = employee.id,
                                date=end_date,
                                from_date=start_date,
                                )
            employee_schedule_ids.append(employee_schedule_id.id)
        # validated_data['employee_schedule_id'] = employee_schedule_id.id
        holiday = Holiday.objects.create(start_date=start_date ,end_date=end_date,location=location,business_id=validated_data.get('business_id'),user_id=validated_data.get('user_id'),name=validated_data.get('name'),note=validated_data.get('note'))
        for employee_schedule_id in employee_schedule_ids:
            holiday.employee_schedule_id=employee_schedule_ids
        return holiday
    