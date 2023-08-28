"""
This is the common file used to declare choices for various models etc.
"""

from django.db import models
from datetime import time
import pytz

class EmployeeDailyInsightChoices(models.TextChoices):

    MORNING = 'M', 'Morning'
    AFTERNOON = 'A', 'Afternoon'
    EVENING = 'E', 'Evening'
    OTHER = 'O', 'Other'

EMPLOYEE_MORNING_TIME = {
    'lower': time(9,0, 0, tzinfo=pytz.UTC),
    'upper': time(12, 0, 0, tzinfo=pytz.UTC)
}

EMPLOYEE_AFTERNOON_TIME = {
    'lower': time(12, 0, 0, tzinfo=pytz.UTC),
    'upper': time(18, 0, 0, tzinfo=pytz.UTC)
}

EMPLOYEE_EVENING_TIME = {
    'lower': time(18, 0, 0, tzinfo=pytz.UTC),
    'upper': time(22, 0, 0, tzinfo=pytz.UTC)
}


