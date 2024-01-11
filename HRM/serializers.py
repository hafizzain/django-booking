from rest_framework import serializers
from HRM.models import *
from Employee.models import Employee, EmployeDailySchedule
from datetime import date, timedelta, datetime
from django.db import transaction


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
            holiday_check = Holiday.objects.filter(start_date__lte=end_date,
                                                    end_date__gte=start_date,
                                                    location=location).exists()
            if holiday_check:
                raise serializers.ValidationError({'message': "Holiday already set for this date range."})

        return attrs
    
    def create(self, validated_data):
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        location = validated_data['location']
        all_employees = Employee.objects \
                        .select_related('user', 'business','country', 'state', 'city') \
                        .prefetch_related('location') \
                        .filter(location=location)
                                        
        current_date = start_date
        employee_schedules = []
        if end_date is None:
            end_date = datetime.now().date()
        if end_date is not  None:
            end_date = datetime.now().date()
        while current_date.date() <= end_date:
            for employee in all_employees:
                employee_schedule_to_del = EmployeDailySchedule.objects.filter(
                    employee_id=employee.id,
                    # date=current_date,
                    # from_date=current_date,
                )
                if employee_schedule_to_del:
                    employee_schedule_to_del.delete()
                employee_schedule = EmployeDailySchedule(
                    start_time=None,
                    end_time=None,
                    is_holiday=True,
                    employee_id=employee.id,
                    date=current_date,
                    from_date=current_date,
                    note='holiday note'
                )
                employee_schedules.append(employee_schedule)
            current_date += timedelta(days=1)
        # Use bulk_create to insert all EmployeeDailySchedule objects in a single query
        with transaction.atomic():
            EmployeDailySchedule.objects.bulk_create(employee_schedules)
        holiday = Holiday.objects.create(**validated_data)
        
        return holiday
    