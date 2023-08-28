from uuid import uuid4
from django.db import models

from Authentication.models import User
from Employee.models import Employee
from Business.models import Business, BusinessAddress
from Service.models import Service
from Appointment.models import Appointment, AppointmentService

from NStyle.choices import (EmployeeDailyInsightChoices, EMPLOYEE_MORNING_TIME, EMPLOYEE_AFTERNOON_TIME,
                            EMPLOYEE_EVENING_TIME)


class EmployeeBookingDailyInsights(models.Model):
    # Foreign Keys
    id = models.UUIDField(default=uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='employee_daily_insights')
    employee = models.ForeignKey(Employee, blank=True, null=True, on_delete=models.CASCADE, related_name='employee_daily_insights')
    business = models.ForeignKey(Business, blank=True, null=True, on_delete=models.CASCADE, related_name='employee_daily_insights')
    service = models.ForeignKey(Service, blank=True, null=True, on_delete=models.CASCADE, related_name='employee_daily_insights')
    appointment = models.ForeignKey(Appointment, blank=True, null=True, on_delete=models.CASCADE, related_name='employee_daily_insights')
    business_address = models.ForeignKey(BusinessAddress, blank=True, null=True, on_delete=models.CASCADE, related_name='employee_daily_insights')
    appointment_service = models.ForeignKey(AppointmentService, blank=True, null=True, on_delete=models.CASCADE, related_name='employee_daily_insights')

    """
        - EmployeeDailyInsightChoices.choices =  MORNING, AFTERNOON, EVENING
        - we will use created_at to extract time and populate day_time_choice based on that
        - we will filter out with a particular choice and aggregate( COUNT ) the objects
        - while getting employee records.
    """
    day_time_choice = models.CharField(max_length=2, choices=EmployeeDailyInsightChoices.choices, null=True, blank=True)

    # time_stamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.employee.full_name}-{self.day_time_choice}"


    def set_employee_time(self):

        # setting employee appointment daily time here in save method
        if not self.day_time_choice:
            created_at_time = self.created_at.time()
            if created_at_time >= EMPLOYEE_MORNING_TIME['lower'] and \
               created_at_time < EMPLOYEE_MORNING_TIME['upper']:
                self.day_time_choice = EmployeeDailyInsightChoices.MORNING
            elif created_at_time >= EMPLOYEE_AFTERNOON_TIME['lower'] and \
                 created_at_time < EMPLOYEE_AFTERNOON_TIME['upper']:
                self.day_time_choice = EmployeeDailyInsightChoices.AFTERNOON
            elif created_at_time >= EMPLOYEE_EVENING_TIME['lower'] and \
                 created_at_time < EMPLOYEE_EVENING_TIME['upper']:
                self.day_time_choice = EmployeeDailyInsightChoices.EVENING
            else:
                self.day_time_choice = EmployeeDailyInsightChoices.OTHER
        
        self.save()