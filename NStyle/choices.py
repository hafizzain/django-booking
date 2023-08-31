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

EMPLOYEE_MORNING_TIME = {
    'lower': time(6,0, 0),
    'upper': time(14, 0, 0)
}

EMPLOYEE_AFTERNOON_TIME = {
    'lower': time(14, 0, 0),
    'upper': time(22, 0, 0)
}

EMPLOYEE_EVENING_TIME = {
    'lower': time(22, 0, 0),
    'upper': time(6, 0, 0)
}


