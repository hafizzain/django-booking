from django.db import models

class ClientTypeChoices(models.TextChoices):
    CLIENT_TYPE = 'Walk_in', 'Walk In'
    CASH_REFUND = 'In_Saloon', 'In Saloon'

    
class RefundSatus(models.TextChoices):
    REFUND = 'refund', 'Refund'
    CANCEL = 'cancel','Cancel'

class PaymentMethodsChoices(models.TextChoices):
    CASH = 'Cash','Cash Payment'
    MASTER_CARD = 'Mastercard','Master Card Payment'
    VISA_CARD = 'Visa','Visa Payment'
    PAYPAL = 'Paypal','PayPal Payment'
    # GIFT = 'Gift','Gift Payment'
    
class CheckoutType(models.TextChoices):
    APPOINTMENT_CHECKOUT = 'Appointment', 'Appointment Checkout'
    SALE_CHECKOUT = 'Sale','Sale Checkout'
    REFUND = 'Refund' , 'Refund'
    GROUP_APPOINTMENT = 'Group Appointment', 'Group Appointment'
    
    
class ItemType(models.TextChoices):
    
    PRODCUT =  'product', 'Product'
    SERIVCIE =  'service', 'Service'
    APPOINTMENT = 'appointment','Appointment'
    
class Status (models.TextChoices):
    IS_REFUND = 'refund','Is Refund'
    CANCELLED = 'cancelled','Cancelled'
    PAID = 'paid' , 'Paid'
    UN_PAID = 'un_paid' , 'Un Paid'


class AppointmentStatus(models.TextChoices):
    VOID = 'void','Void'
    BOOKED = 'booked' , 'Booked'
    CANCELLED = 'cancelled' , 'Cancelled'
    COMPLETED = 'completed' ,'Completed'
    
    
class CouponType (models.TextChoices):
    REFUND = 'Refund Coupon','Refund Coupon'
    SPEICFIC_PRODUCT_SERVICES = 'Specific Service/Product Coupon','Specific Service/Product Coupon'
    BUY_ONE_GET_ONE = 'Buy one Get one Free' ,'Buy one Get one Free'
    SPEND_SOME_AMOUNT_= 'Spend Some Amount' ,'Spend Some Amount'
    PROMOTION = "Promotion","Promotion"
    VOUCHER = "Voucher","Voucher"
    MEMBERSHIP = "Membership","Membership"
    GIFT = "Gift", "Gift"
    