from rest_framework import serializers
from HRM.models import *
from Employee.models import Employee, EmployeDailySchedule
from datetime import date, timedelta, datetime
from django.db import transaction


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'

    # def validate(self, attrs):
    #     start_date = attrs.get('start_date', None)
    #     end_date = attrs.get('end_date', None)
    #     location = attrs.get('location', None)
    #
    #     if start_date is not None:
    #         # Check if a holiday already exists for the start_date
    #         start_date_check = Holiday.objects.filter(start_date=start_date, location=location).exists()
    #         if start_date_check:
    #             raise serializers.ValidationError({'message': "Holiday already set for this date."})
    #
    #     # Check if there is any holiday overlapping with the date range
    #     if start_date is not None and end_date is not None:
    #         holiday_check = Holiday.objects.filter(start_date__lte=end_date,
    #                                                end_date__gte=start_date,
    #                                                location=location).exists()
    #         if holiday_check:
    #             raise serializers.ValidationError({'message': "Holiday already set for this date range."})
    #
    #     return attrs

    def create(self, validated_data):
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        location = validated_data['location']
        all_employees = Employee.objects \
            .select_related('user', 'business', 'country', 'state', 'city') \
            .prefetch_related('location') \
            .filter(location=location)
        try:
            # pass
            if start_date  and end_date:
                # pass
                from_date = start_date
                to_date = end_date
                diff = to_date - from_date
                days = int(diff.days)
                for i in range(days + 1):
                    if  i ==0:
                        current_date = from_date
                    else:
                        current_date = from_date + timedelta(days=i)
                    for emp in all_employees:
                        working_sch = EmployeDailySchedule.objects.filter(employee_id=emp.id, date=current_date).first()
                        if working_sch:
                            working_sch.is_vacation = False
                            working_sch.is_weekend=False
                            working_sch.is_holiday=True
                            working_sch.date = current_date
                            working_sch.from_date = current_date
                            working_sch.is_weekend=False
                            working_sch.is_vacation=False
                            working_sch.is_working_schedule=False
                            working_sch.save()
                        else:
                             EmployeDailySchedule.objects.create(
                                employee_id=emp.id,
                                date=current_date,
                                from_date=current_date,
                                to_date=to_date,
                                vacation_status=None,
                                is_weekend = False,
                                is_holiday=True,
                                is_working_schedule=False,
                                is_vacation=False
                            )
            if start_date is not None and end_date is None:
                from_date = start_date
                to_date = from_date
                diff = to_date - from_date
                days = int(diff.days)
                for i in range(days + 1):
                    if i == 0:
                        current_date = from_date
                    else:
                        current_date = from_date + timedelta(days=i)
                    for emp in all_employees:
                        working_sch = EmployeDailySchedule.objects.filter(employee_id=emp.id, date=current_date).first()
                        if working_sch:
                            working_sch.is_vacation = False
                            working_sch.is_weekend = False
                            working_sch.is_holiday = True
                            working_sch.date = current_date
                            working_sch.from_date = current_date
                            working_sch.is_weekend = False
                            working_sch.is_vacation = False
                            working_sch.is_working_schedule = False
                            working_sch.save()
                        else:
                            EmployeDailySchedule.objects.create(
                                employee_id=emp.id,
                                date=current_date,
                                from_date=current_date,
                                to_date=to_date,
                                vacation_status=None,
                                is_weekend=False,
                                is_holiday=True,
                                is_working_schedule=False,
                                is_vacation=False
                            )

            # if start_date is not None:
            #     days = 1
            #     for i in range(days + 1):
            #         current_date = from_date + timedelta(days=i)
            #         working_sch = EmployeDailySchedule.objects.filter(employee=employee_id, date=current_date).first()
            #         if working_sch:
            #             working_sch.is_vacation = True
            #             empl_vacation.save()
            #             working_sch.vacation = empl_vacation
            #             working_sch.from_date = current_date
            #             working_sch.save()
            #         else:
            #             working_schedule = EmployeDailySchedule.objects.create(
            #                 user=user,
            #                 business=business,
            #                 employee=employee_id,
            #                 day=day,
            #                 start_time=start_time,
            #                 end_time=end_time,
            #                 start_time_shift=start_time_shift,
            #                 end_time_shift=end_time_shift,
            #                 date=current_date,
            #                 from_date=current_date,
            #                 to_date=to_date,
            #                 note=note,
            #                 vacation_status='pending'
            #             )
            #
            #             if is_vacation is not None:
            #                 working_schedule.is_vacation = True
            #                 empl_vacation.save()
            #                 working_schedule.vacation = empl_vacation
            #             else:
            #                 working_schedule.is_vacation = False
            #
            #             working_schedule.is_leave = is_leave if is_leave is not None else False
            #             working_schedule.is_off = is_off if is_off is not None else False
            #             working_schedule.save()

        except Exception as ex:
            ex=str(ex)
            raise serializers.ValidationError(ex)

        # for employee in all_employees:
        #
        #             EmployeDailySchedule.objects.create(
        #                 start_time=None,
        #                 end_time=None,
        #                 is_holiday=True,
        #                 employee_id=employee.id,
        #                 date=current_date,
        #                 from_date=current_date,
        #                 note='arbabs note',
        #                 is_vacation=False,
        #                 is_weekend=False,
        #                 is_working_schedule=False
        #             )
        #         else:
        #             employee_schedule = EmployeDailySchedule(
        #                 start_time=None,
        #                 end_time=None,
        #                 is_holiday=True,
        #                 employee_id=employee.id,
        #                 date=current_date,
        #                 from_date=current_date,
        #                 note='arbabs note',
        #                 is_vacation=False,
        #                 is_weekend=False
        #             )
        try:
         holiday = Holiday.objects.create(**validated_data)
        except Exception as e:
            e=str(e)
            raise serializers.ValidationError(e)
        return holiday
