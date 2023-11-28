from django.db import models
from django.db.models import F, Sum, FloatField, Case, When, Value
from django.db.models.functions import Coalesce

class AppointmentCheckoutManager(models.QuerySet):

    def with_total_tax_and_price(self):
        return self.annotate(
            total_tax=Coalesce(
                Sum(F('gst_price') + F('gst_price1')),
                0.0,
                output_field=FloatField()
            ),
            final_price=Coalesce(
                    Case(
                        When(appointment_service__is_redeemed=True, then="appointment_service__redeemed_price"),
                        When(appointment_service__discount_price__isnull=False, then="appointment_service__discount_price"),
                        When(appointment_service__price__isnull=False, then="appointment_service__price"),
                        default="appointment_service__total_price"
                    ),
                    0.0,
                    output_field=FloatField()
            )).annotate(
                final_total_price = Coalesce(Sum('final_price'), 0.0, output_field=FloatField())
        ).annotate(
            tax_and_price_total=Coalesce(F('final_total_price') + F('total_tax'), 0.0, output_field=FloatField())
        )