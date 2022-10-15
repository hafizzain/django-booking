from tabnanny import verbose
from uuid import uuid4
from django.db import models
from django.utils.timezone import now


from Authentication.models import User
from Business.models import Business
from Utility.models import Country, State, City
from Service.models  import Service
from Utility.models import GlobalPermissionChoices


class EmployePermission(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    
    #Appointment Booking
    appointment = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Appointment')
    email_staff = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Email to staff')
    
    #Inventory Operations
    products = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Products')
    brand = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Brand')
    categories = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Categories')
    vendors  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Vendors')
    
    #Stock Management
    stock  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Stock')
    
    #Inventory Reports
    stock_report  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Stock Report')
    
    #Staff Reports
    staff_data  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Staff Data')
    staff_product_sales = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Staff Product Sales')
    staff_product_sales = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Staff Service Sales')
    staff_product_sales = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Staff Assets')
    
    #Client Rewards
    rewards  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client Rewards')
    promotions = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client Promotions')
    vouchers = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client Vouchers')
    membership = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client Membership')
    subscriptions = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client Subscriptions')
    
    #Sale Orders
    sale_product  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Product')
    sale_rewards  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Rewards')
    sale_promotions = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Promotions')
    sale_vouchers = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Vouchers')
    sale_membership = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Membership')
    sale_subscriptions = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Subscriptions')
    
    #Reports
    sale_report_product  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Report Product')
    sale_report_rewards  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Report Rewards')
    sale_report_promotions = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Report Promotions')
    sale_report_vouchers = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Report Vouchers')
    sale_report_membership = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Report Membership')
    sale_report_subscriptions = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Report Subscriptions')
    
    def __str__(self):
        return str(self.id)