from django.db import models

class ClientTypeChoices(models.TextChoices):
    CLIENT_TYPE = 'Walk_in', 'Walk In'
    CASH_REFUND = 'In_Saloon', 'In Saloon'

class CheckoutType(models.TextChoices):
    SALE_CHECKOUT = 'sale_checkout', 'Sale Checkout'
    APPOINTMENT_CHECKOUT = 'appointment_checkout' ,'Appointment Checkout'
    
class RefundSatus(models.TextChoices):
    REFUND = 'refund', 'Refund'
    CANCEL = 'cancel','Cancel'

class PaymentMethods(models.TextChoices):
    CASH = 'cash','Cash Payment'
    MASTER_CARD = 'master','Master Payment'
    VISA_CARD = 'visa','Visa Payment'
    PAYPAL = 'paypal','PayPal Payment'
    GIFT = 'gift','Gift Payment'
    
class CheckoutType(models.TextChoices):
    APPOINTMENT_CHECKOUT = 'appointment_checkout', 'Appointment Checkout'
    SALE_CHECKOUT = 'sale_checkout','Sale Checkout'
    
    
class ItemType(models.TextChoices):
    
    PRODCUT =  'product', 'Product'
    SERIVCIE =  'service', 'Service'
    APPOINTMENT = 'appointment','Appointment'
    
class Status (models.TextChoices):
    IS_REFUND = 'is_refund','Is Refund'
    CANCELLED = 'cancelled','cancelled'
    PAID = 'paid' , 'paid'
    UN_PAID = 'un_paid' , 'un_paid'

    
class AppointmentStatus(models.TextChoices):
    VOID = 'void','Void'
    BOOKED = 'booked' , 'Booked'
    CANCELLED = 'cancelled' , 'Cancelled'
    COMPLETED = 'completed' ,'Completed'
    
    
class CouponType (models.TextChoices):
    REFUND = 'refund','Refund Coupon'
    SPEICFIC_PRODUCT_SERVICES = 'specific_product_services','Specific Service/Product Coupon'
    BUY_ONE_GET_ONE = 'buy_one_get' ,'Buy one Get one Free'
    SPEND_SOME_AMOUNT_= 'spend_some_amount' ,'Spend Some Amount'
    