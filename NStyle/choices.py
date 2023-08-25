"""
This is the common file used to declare choices for various models etc.
"""

from django.db import models
from datetime import time


class EmployeeDailyInsightChoices(models.TextChoices):

    MORNING = 'M', 'Morning'
    AFTERNOON = 'A', 'Afternoon'
    EVENING = 'E', 'Evening'

MORNING_TIME = {
    'lower': time()
}


