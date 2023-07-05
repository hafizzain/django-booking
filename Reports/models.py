from django.db import models
from django.utils.timezone import now
from uuid import uuid4
from Authentication.models import User
from Client.models import Client
from Business.models import BusinessAddress
from Invoices.models import SaleInvoice
from Sale.Constants.Promotion import get_promotions
from Order.models import Checkout, Order
from Appointment.models import AppointmentCheckout

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
    original_price = models.DecimalField(default = 0 , max_digits=10, decimal_places=5)
    discount_percentage = models.FloatField(default= 0)
    discount_price = models.FloatField(default= 0)

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return str(self.id)
    
    def get_appointment_prices(self):
        original_prices = 0
        discounted_prices = 0

        return {
            'original_prices' : original_prices,
            'discounted_prices' : discounted_prices,
        }


    def get_sale_prices(self):
        original_prices = 0
        discounted_prices = 0

        orders = Order.objects.filter(
            checkout__id = self.checkout_id
        )

        for order in orders:
            if order.discount_price:
                discounted_prices += float(order.discount_price) * float(order.quantity)

            original_prices += float(order.total_price) * float(order.quantity)

        return {
            'original_prices' : original_prices,
            'discounted_prices' : discounted_prices,
        }
    
    def assign_gst_price(self):
        if self.checkout_type == 'Sale':
            checkout = Checkout.objects.get(id = self.checkout_id)
            self.gst = checkout.tax_amount

        elif self.checkout_type == 'Appointment':
            checkout = AppointmentCheckout.objects.get(id = self.checkout_id)
            self.gst = checkout.gst_price
        
    def save(self, *args, **kwargs):
        if not self.promotion_name:
            promotion = get_promotions(
                promotion_type = self.promotion_type,
                promotion_id = self.promotion_id
            )
            
            if promotion:
                self.promotion_name = promotion['promotion_name']

        if not self.gst:
            self.assign_gst_price()

        if not self.original_price:
            if self.checkout_type == 'Sale':
                prices = self.get_sale_prices()
            elif self.checkout_type == 'Appointment':
                prices = self.get_appointment_prices()

            else:
                prices = {'original_prices' : 0, 'discounted_prices' : 0}
            
            self.original_price = prices.get('original_prices', 0)
            self.discount_price = prices.get('discounted_prices', 0)
        
        self.is_active = True

        super(DiscountPromotionSalesReport, self).save(*args, **kwargs)
