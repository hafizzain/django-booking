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
    