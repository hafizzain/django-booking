from django.db import models
from django.db.models import F, Sum
from django.db.models.functions import Coalesce

class AppointmentCheckoutManager(models.QuerySet):

    def with_total_tax(self):
        return self.annotate(
            total_tax=Coalesce(
                Sum(F('gst_price') + F('gst_price1'))
            )
        )