from uuid import uuid4
from django.db import models
from django.utils.timezone import now


from Authentication.models import User
from Business.models import Business
from Employee.models import Employee, StaffGroup
from Utility.models import Country, State, City
from Service.models  import Service
from Utility.models import GlobalPermissionChoices


class EmployePermission(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)

    employee = models.OneToOneField(Employee, on_delete=models.CASCADE,null=True, blank=True ,related_name='employee_permissions')
    staffgroup = models.OneToOneField(StaffGroup, on_delete=models.CASCADE, null=True, blank=True, related_name='staffGroup_permissions')
    
    #Appointment Booking
    appointment = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Appointment', related_name='global_permissions_appointment')
    email_staff = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Email to staff' , related_name='global_permissions_email_staff')
    
    #Inventory Operations
    products = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Products' , related_name='global_permissions_products')
    brand = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Brand')
    categories = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Categories' , related_name='global_permissions_categories')
    vendors  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Vendors' , related_name='global_permissions_vendors')
    
    #Stock Management
    stock  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Stock' , related_name='global_permissions_stock')
    
    #Inventory Reports
    stock_report  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Stock Report' , related_name='global_permissions_stock_report')
    
    #Staff Reports
    staff_data  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Staff Data' , related_name='global_permissions_staff_data')
    staff_product_sales = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Staff Product Sales' , related_name='global_permissions_staff_product_sales')
    staff_product_sales = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Staff Service Sales' , related_name='global_permissions_staff_product_sales')
    staff_product_sales = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Staff Assets' , related_name='global_permissions_staff_product_sales')
    
    #Client Rewards
    rewards  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client Rewards' , related_name='global_permissions_rewards')
    promotions = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client Promotions' , related_name='global_permissions_promotions')
    vouchers = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client Vouchers' , related_name='global_permissions_vouchers')
    membership = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client Membership' , related_name='global_permissions_membership')
    subscriptions = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client Subscriptions' , related_name='global_permissions_subscriptions')
    
    #Sale Orders
    sale_product  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Product' , related_name='global_permissions_sale_product')
    sale_rewards  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Rewards' , related_name='global_permissions_sale_rewards')
    sale_promotions = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Promotions' , related_name='global_permissions_sale_promotions')
    sale_vouchers = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Vouchers' , related_name='global_permissions_sale_vouchers')
    sale_membership = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Membership' , related_name='global_permissions_sale_membership')
    sale_subscriptions = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Subscriptions' , related_name='global_permissions_sale_subscriptions')
    
    #Reports
    sale_report_product  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Report Product' , related_name='global_permissions_sale_report_product')
    sale_report_rewards  = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Report Rewards' , related_name='global_permissions_sale_report_rewards')
    sale_report_promotions = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Report Promotions' , related_name='global_permissions_sale_report_promotions')
    sale_report_vouchers = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Report Vouchers' , related_name='global_permissions_sale_report_vouchers')
    sale_report_membership = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Report Membership' , related_name='global_permissions_sale_report_membership')
    sale_report_subscriptions = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sale Report Subscriptions' , related_name='global_permissions_sale_report_subscriptions')
    
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)

#{
# appointment : ['Basic', '']
# email_staff : ['Basic', '']
# products : ['Basic', '']
# brand : ['Basic', '']
# categories : ['Basic', '']
# vendors : ['Basic', '']
# stock : ['Basic', '']
# stock_report : ['Basic', '']}