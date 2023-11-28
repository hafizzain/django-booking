from django.db import models
from django.db.models import F, Sum, FloatField, Case, When, Value, Subquery, OuterRef
from django.db.models.functions import Coalesce

from .models import AppointmentService

class AppointmentCheckoutManager(models.QuerySet):

    def with_total_tax_and_price(self):
        return self.annotate(
            total_tax=Coalesce(
                Sum(F('gst_price') + F('gst_price1')),
                0.0,
                output_field=FloatField()
            ),
            final_price=Subquery(AppointmentService.objects.filter(appointment=OuterRef('appointment')).aggregate(
                Coalesce(
                    Case(
                        When(is_redeemed=True, then="redeemed_price"),
                        When(discount_price__isnull=False, then="discount_price"),
                        When(price__isnull=False, then="price"),
                        default="total_price"
                    ),
                    0.0,
                    output_field=FloatField()
                    )
                )
            )
        ).annotate(
                final_total_price = Coalesce(Sum('final_price'), 0.0, output_field=FloatField())
        )
        # ).annotate(
        #     tax_and_price_total=Coalesce(F('final_total_price') + F('total_tax'), 0.0, output_field=FloatField())
        # )))