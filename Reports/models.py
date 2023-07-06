from django.db import models
from django.utils.timezone import now
from uuid import uuid4
from Authentication.models import User
from Client.models import Client
from Business.models import BusinessAddress
from Invoices.models import SaleInvoice
from Sale.Constants.Promotion import get_promotions
from Order.models import Checkout, Order, ServiceOrder, ProductOrder
from Appointment.models import AppointmentCheckout, AppointmentService
from Service.models import PriceService
from Product.models import CurrencyRetailPrice
# Create your models here.



def get_ItemPrice(this_instance, orders):
    o1 = 0
    d1 = 0
    d2 = 0
    f1 = 0

    for order in orders:
        price = order.discount_price or order.total_price
        
        if price > 0:
            if order.discount_price:
                d1 += float(order.discount_price) * float(order.quantity)
                d2 += float(order.total_price) * float(order.quantity)

            o1 += float(order.total_price) * float(order.quantity)
        else:
            try:
                item = ServiceOrder.objects.get(id = order.id)
            except:
                try:
                    item = ProductOrder.objects.get(id = order.id)
                except:
                    pass
                else:
                    retail_prices = CurrencyRetailPrice.objects.filter(
                        product = item.product,
                        currency = this_instance.location.currency
                    ).order_by('created_at')
                    if len(retail_prices) > 0:
                        retail_price = retail_prices[0].retail_price
                        f1 += float(retail_price) * float(order.quantity)
                        o1 += float(retail_price) * float(order.quantity)

            else:
                service_prices = PriceService.objects.filter(service = item.service, duration = item.duration, currency = this_instance.location.currency)
                if len(service_prices) > 0:
                    service_price = service_prices[0].price
                    f1 += float(service_price) * float(order.quantity)
                    o1 += float(service_price) * float(order.quantity)

    discounted_prices = d1 + (o1 - d2 - f1)
    return [o1, discounted_prices]

def get_Appointment_ItemPrice(this_instance, orders):
    o1 = 0
    d1 = 0
    d2 = 0
    f1 = 0

    for order in orders:
        price = order.discount_price or order.price
        
        if price > 0:
            if order.discount_price:
                d1 += float(order.discount_price)
                d2 += float(order.price)

            o1 += float(order.price)
        else:
            service_prices = PriceService.objects.filter(service = order.service, duration = order.duration, currency = this_instance.location.currency)
            if len(service_prices) > 0:
                service_price = service_prices[0].price
                f1 += float(service_price)
                o1 += float(service_price)

    discounted_prices = d1 + (o1 - d2 - f1)
    return [o1, discounted_prices]


def get_fixed_prices(this_instance, orders):
    original_price = 0
    discounted_prices = 0

    for order in orders:
        
        discounted_prices += float(order.total_price) * float(order.quantity)
        try:
            item = ServiceOrder.objects.get(id = order.id)
        except:
            try:
                item = ProductOrder.objects.get(id = order.id)
            except:
                pass
            else:
                retail_prices = CurrencyRetailPrice.objects.filter(
                    product = item.product,
                    currency = this_instance.location.currency
                ).order_by('created_at')
                if len(retail_prices) > 0:
                    retail_price = retail_prices[0].retail_price
                    original_price += float(retail_price) * float(order.quantity)

        else:
            service_prices = PriceService.objects.filter(service = item.service, duration = item.duration, currency = this_instance.location.currency)
            if len(service_prices) > 0:
                service_price = service_prices[0].price
                original_price += float(service_price) * float(order.quantity)

    return [original_price, discounted_prices]


def get_Appointment_fixed_prices(this_instance, orders):
    original_price = 0
    discounted_prices = 0

    for order in orders:
        
        discounted_prices += float(order.price)
       
        service_prices = PriceService.objects.filter(service = order.service, duration = order.duration, currency = this_instance.location.currency)
        if len(service_prices) > 0:
            service_price = service_prices[0].price
            original_price += float(service_price)

    return [original_price, discounted_prices]



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

        app_checkout = AppointmentCheckout.objects.get(
            id = self.checkout_id
        )

        orders = AppointmentService.objects.filter(
            appointment = app_checkout.appointment
        )

            
        if self.promotion_type == 'Purchase Discount':
            original_prices, discounted_prices = get_Appointment_ItemPrice(self, orders)

        elif self.promotion_type == 'Spend_Some_Amount':
            original_prices, discounted_prices = get_Appointment_ItemPrice(self, orders)

        elif self.promotion_type == 'Mentioned_Number_Service':
            original_prices, discounted_prices = get_Appointment_ItemPrice(self, orders)

        elif self.promotion_type == 'Fixed_Price_Service':
            original_prices, discounted_prices = get_Appointment_fixed_prices(self, orders)

        elif self.promotion_type == 'Bundle_Fixed_Service':
            original_prices, discounted_prices = get_Appointment_fixed_prices(self, orders)

        elif self.promotion_type == 'Retail_and_Get_Service':
            pass

        else:
            for order in orders:
                if order.discount_price:
                    discounted_prices += float(order.discount_price)

                original_prices += float(order.total_price)

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

            
        if self.promotion_type == 'Purchase Discount':
            original_prices, discounted_prices = get_ItemPrice(self, orders)

        elif self.promotion_type == 'Spend_Some_Amount':
            original_prices, discounted_prices = get_ItemPrice(self, orders)

        elif self.promotion_type == 'Mentioned_Number_Service':
            original_prices, discounted_prices = get_ItemPrice(self, orders)

        elif self.promotion_type == 'Fixed_Price_Service':
            original_prices, discounted_prices = get_fixed_prices(self, orders)

        elif self.promotion_type == 'Bundle_Fixed_Service':
            original_prices, discounted_prices = get_fixed_prices(self, orders)

        elif self.promotion_type == 'Retail_and_Get_Service':
            original_prices, discounted_prices = get_ItemPrice(self, orders)

        else:
            for order in orders:
                if order.discount_price:
                    discounted_prices += float(order.discount_price) * float(order.quantity)
                original_prices += float(order.total_price) * float(order.quantity)

        return {
            'original_prices' : original_prices,
            'discounted_prices' : discounted_prices,
        }
    
    def set_gst_price(self):
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
            self.set_gst_price()

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
