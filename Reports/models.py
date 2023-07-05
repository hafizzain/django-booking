from django.db import models
from django.utils.timezone import now
from uuid import uuid4
from Authentication.models import User
from Client.models import Client
from Business.models import BusinessAddress
from Invoices.models import SaleInvoice

# Create your models here.


class DiscountPromotionSalesReport(models.Model):

    CHECKOUT_TYPES = (
        ('Sale', 'Sale'),
        ('Appointment', 'Appointment')
    )

    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)

    checkout_id = models.CharField(max_length=900, default='')
    checkout_type = models.CharField(max_length=20, default='Sale', choices=CHECKOUT_TYPES)
    invoice = models.ForeignKey(SaleInvoice, on_delete=models.SET_NULL, related_name='invoice_discount_sales', null=True, blank=True)

    promotion_id = models.CharField(max_length=900, default='')
    promotion_type = models.CharField(max_length=900, default='')
    promotion_name = models.CharField(max_length=900, default='')

    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='user_discount_sales', null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name='client_discount_sales', null=True, blank=True)
    location = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, related_name='location_discount_sales', null=True, blank=True)
    quantity = models.PositiveBigIntegerField(default= 0)
    gst = models.PositiveBigIntegerField(default = 0)
    total_price = models.DecimalField(default = 0 , max_digits=10, decimal_places=5)
    discount_percentage = models.FloatField(default= 0)
    discount_price = models.FloatField(default= 0)

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return str(self.id)
