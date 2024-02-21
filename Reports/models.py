import uuid

from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from uuid import uuid4
from Authentication.models import User
from Client.models import Client
from Business.models import BusinessAddress
from Invoices.models import SaleInvoice
from Promotions.models import Coupon
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
                item = ServiceOrder.objects.get(id=order.id)
            except:
                try:
                    item = ProductOrder.objects.get(id=order.id)
                except:
                    pass
                else:
                    retail_prices = CurrencyRetailPrice.objects.filter(
                        product=item.product,
                        currency=this_instance.location.currency).order_by('created_at')
                    if len(retail_prices) > 0:
                        retail_price = retail_prices[0].retail_price
                        f1 += float(retail_price) * float(order.quantity)
                        o1 += float(retail_price) * float(order.quantity)

            else:
                service_prices = PriceService.objects.filter(service=item.service, duration=item.duration,
                                                             currency=this_instance.location.currency).order_by(
                    '-created_at')
                service_price = 0
                if len(service_prices) > 0:
                    service_price = service_prices[0].price
                else:
                    service_prices = PriceService.objects.filter(service=item.service,
                                                                 currency=this_instance.location.currency).order_by(
                        '-created_at')
                    if len(service_prices) > 0:
                        service_price = service_prices[0].price
                if service_price:
                    f1 += float(service_price) * float(order.quantity)
                    o1 += float(service_price) * float(order.quantity)

    discounted_prices = d1 + (o1 - d2 - f1)
    return [o1, discounted_prices]




def get_Appointment_ItemPrice(this_instance, orders):
    o1 = 0  # 50 + 340
    d1 = 0  # 272
    d2 = 0  # 340
    f1 = 0

    # 272 + (390 - 340 - 0)

    for order in orders:
        price = order.discount_price or order.price

        if price > 0:
            if order.discount_price:
                d1 += float(order.discount_price)

                service_prices = PriceService.objects.filter(service=order.service, duration=order.duration,
                                                             currency=this_instance.location.currency).order_by(
                    '-created_at')
                if len(service_prices) > 0:
                    service_price = service_prices[0].price
                    o1 += float(service_price)
                    d2 += float(service_price)
            else:
                o1 += float(order.price)
        else:
            service_prices = PriceService.objects.filter(service=order.service, duration=order.duration,
                                                         currency=this_instance.location.currency).order_by(
                '-created_at')
            service_price = 0
            if len(service_prices) > 0:
                service_price = service_prices[0].price
            else:
                service_prices = PriceService.objects.filter(service=order.service,
                                                             currency=this_instance.location.currency).order_by(
                    '-created_at')
                if len(service_prices) > 0:
                    service_price = service_prices[0].price

            if service_price:
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
            item = ServiceOrder.objects.get(id=order.id)
        except:
            try:
                item = ProductOrder.objects.get(id=order.id)
            except:
                pass
            else:
                retail_prices = CurrencyRetailPrice.objects.filter(
                    product=item.product,
                    currency=this_instance.location.currency
                ).order_by('created_at')
                if len(retail_prices) > 0:
                    retail_price = retail_prices[0].retail_price
                    original_price += float(retail_price) * float(order.quantity)

        else:
            service_prices = PriceService.objects.filter(service=item.service, duration=item.duration,
                                                         currency=this_instance.location.currency).order_by(
                '-created_at')
            service_price = 0
            if len(service_prices) > 0:
                service_price = service_prices[0].price
            else:
                service_prices = PriceService.objects.filter(service=item.service, 
                                                             currency=this_instance.location.currency).order_by(
                    '-created_at')
                if len(service_prices) > 0:
                    service_price = service_prices[0].price

            if service_price:
                original_price += float(service_price) * float(order.quantity)

    return [original_price, discounted_prices]


def get_Appointment_fixed_prices(this_instance, orders):
    original_price = 0
    discounted_prices = 0

    for order in orders:

        discounted_prices += float(order.price)

        service_prices = PriceService.objects.filter(service=order.service, duration=order.duration,
                                                     currency=this_instance.location.currency).order_by('-created_at')
        service_price = 0
        if len(service_prices) > 0:
            service_price = service_prices[0].price
        else:
            service_prices = PriceService.objects.filter(service=order.service,
                                                         currency=this_instance.location.currency).order_by(
                '-created_at')
            if len(service_prices) > 0:
                service_price = service_prices[0].price

        if service_price:
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
    invoice = models.ForeignKey(SaleInvoice, on_delete=models.SET_NULL, related_name='invoice_discount_sales',
                                null=True, blank=True)

    promotion_id = models.CharField(max_length=900, default='')
    promotion_type = models.CharField(max_length=900, default='')
    promotion_name = models.CharField(max_length=900, default='')

    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='user_discount_sales', null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name='client_discount_sales', null=True,
                               blank=True)
    location = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, related_name='location_discount_sales',
                                 null=True, blank=True)
    
    
    quantity = models.PositiveBigIntegerField(default=0)
    gst = models.FloatField(default=0)
    original_price = models.DecimalField(default=0, max_digits=10, decimal_places=5)
    discount_percentage = models.FloatField(default=0)
    discount_price = models.FloatField(default=0)

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

    def get_appointment_prices(self):
        from  SaleRecords.models import SaleRecordsAppointmentServices
        
        original_prices = 0
        discounted_prices = 0

        app_checkout = SaleRecordsAppointmentServices.objects.get(
            sale_record_id=self.checkout_id
        )

        orders = AppointmentService.objects.filter(
            appointment=app_checkout.appointment
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
                oop = order.total_price or order.price  # Order Original Price
                oop = float(oop)

                if order.discount_price:
                    discounted_prices += float(order.discount_price)
                else:
                    discounted_prices += oop

                original_prices += oop

        return {
            'original_prices': original_prices,
            'discounted_prices': discounted_prices,
        }

    def get_sale_prices(self):
        original_prices = 0
        discounted_prices = 0

        orders = Order.objects.filter(
            checkout__id=self.checkout_id
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
            original_prices, discounted_prices = get_fixed_prices(self, orders)

        else:
            for order in orders:
                if order.discount_price:
                    discounted_prices += float(order.discount_price) * float(order.quantity)
                else:
                    discounted_prices += float(order.total_price) * float(order.quantity)

                original_prices += float(order.total_price) * float(order.quantity)

        return {
            'original_prices': original_prices,
            'discounted_prices': discounted_prices,
        }
        
        
    def get_discounts_and_original_prices(self):
        from SaleRecords.models import SaleRecords, SaleRecordsAppointmentServices, SaleRecordServices, SaleRecordsProducts
        
        
        original_price = 0 
        dicounted_price = 0
        
        if self.checkout_type == 'Appointment' or self.checkout_type == 'Group Appointment' or self.checkout_type == 'Sale':
            
            appointment_service_records = SaleRecordsAppointmentServices.objects.filter(sale_record_id = self.checkout_id)
            service_records = SaleRecordServices.objects.filter(sale_record_id = self.checkout_id)
            product_records = SaleRecordsProducts.objects.filter(sale_record_id = self.checkout_id)
            # raise ValidationError(f"error {product_records.count()}")
            try:
                if appointment_service_records:
                    for rec in appointment_service_records:
                        service_price = PriceService.objects.filter(service=rec.service, duration=rec.duration,
                                                                    currency=self.location.currency).order_by(
                            '-created_at')
                        if len(service_price) > 0:
                            service_price[0].price
                        else:
                            service_price = PriceService.objects.filter(service=rec.service, 
                                                                        currency=self.location.currency).order_by(
                                '-created_at')
                            if len(service_price) > 0:
                                service_price = service_price[0].price
                            if service_price:
                                original_price += float(service_price) * float(rec.quantity)
            except Exception as e:
                raise ValidationError({'erorr occured in dicount Promotion Appointment Service': str(e) })
                            
            try:              
                if service_records:
                    for rec in service_records:
                        service_price = PriceService.objects.filter(service=rec.service, duration=rec.duration,
                                                                    currency=self.location.currency).order_by(
                            '-created_at')
                        if len(service_price) > 0:
                            service_price[0].price
                        else:
                            service_price = PriceService.objects.filter(service=rec.service, 
                                                                        currency=self.location.currency).order_by(
                                '-created_at')
                            if len(service_price) > 0:
                                service_price = service_price[0].price
                            if service_price:
                                original_price += float(service_price) * float(rec.quantity)
            except Exception as e:
                raise ValidationError({'erorr occured in dicount Promotion service': str(e) })
                            
            try:              
                if product_records:
                    for rec in product_records:
                        product_price = CurrencyRetailPrice.objects.filter(
                            product=rec.product,
                            currency=self.location.currency).order_by('created_at')
                        if len(product_price) > 0:
                            product_actual_price = product_price[0].retail_price
                            original_price += float(product_actual_price) * float(rec.quantity)
            except Exception as e:
                raise ValidationError({'erorr occured in dicount Promotion Product': str(e) })
                    
                        
        # if self.checkout_type == 'Sale':
        #     services_records = SaleRecordServices.objects.filter(sale_record_id = self.checkout_id)
        return original_price, dicounted_price
            
            
                

        
        
        
        

    # def set_gst_price(self):
    #     if self.checkout_type == 'Sale' or self.checkout_type == 'Appointment' or self.checkout_type == 'Group Appointment':
    #         from SaleRecords.models import SaleRecords
    #         checkout = SaleRecords.objects.get(id=self.checkout_id)
    #         self.gst = checkout.total_tax

        # elif self.checkout_type == 'Appointment':
        #     checkout = AppointmentCheckout.objects.get(id=self.checkout_id)
        #     self.gst = checkout.gst_price

    def save(self, *args, **kwargs):
        if not self.promotion_name:
            promotion = get_promotions(
                promotion_type=self.promotion_type,
                promotion_id=self.promotion_id
            )

            if promotion:
                self.promotion_name = promotion['promotion_name']

        # if not self.gst:
        #     self.set_gst_price()

        # if not self.original_price:
        #     if self.checkout_type == 'Sale':
        #         prices = self.get_sale_prices()
        #     elif self.checkout_type == 'Appointment':
        #         prices = self.get_appointment_prices()

        #     else:
        #         prices = {'original_prices': 0, 'discounted_prices': 0}

        #     self.original_price = prices.get('original_prices', 0)
        #     self.discount_price = prices.get('discounted_prices', 0)
        if not self.original_price and not self.discount_price:
            self.original_price , self.discount_price = self.get_discounts_and_original_prices()
        self.is_active = True

        super(DiscountPromotionSalesReport, self).save(*args, **kwargs)


class CouponReport(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True , related_name='coupon_reports')
    id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    checkout_id = models.TextField(null=True)
    checkout_type = models.TextField(null=True)
    invoice = models.ForeignKey(SaleInvoice, on_delete=models.SET_NULL, related_name='invoice_coupon_sale',
                                null=True, blank=True)
    client_type = models.TextField(null=True, blank=True)
    coupon_type_value = models.TextField(null=True)
    coupon_name = models.TextField(null=True)
    coupon_type = models.TextField(null=True)
    amount_spent = models.FloatField(null=True)
    discounted_percentage = models.FloatField(null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='user_coupon', null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name='client_coupon', null=True,
                            blank=True)
    location = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, related_name='location_coupon',
                                null=True, blank=True)
    quantity = models.PositiveBigIntegerField(default=0)
    gst = models.FloatField(default=0)
    original_price = models.DecimalField(default=0, max_digits=10, decimal_places=5)
    discount_percentage = models.FloatField(default=0)
    discount_price = models.FloatField(default=0)

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)


# Do not remove this line
from .public_reports_models import *
