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
    
    #POS Application
    pos_root_access = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='POS Root Access', related_name='global_permissions_pos_root_access')
    
    #Mobile App
    mobile_root_access = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Mobile Root Access', related_name='global_permissions_mobile_root_access')
    
    #My Account
    account_root_access = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Account Root Access', related_name='global_permissions_account_root_access')
    account_business_setting = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Account Business Setting', related_name='global_permissions_account_business_setting')
    account_finance_setting = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Account Finance Setting', related_name='global_permissions_account_finance_setting')
    account_service_management = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Account Service Setting', related_name='global_permissions_account_service_setting')
    account_notification_setting = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Account Service Setting', related_name='global_permissions_account_notification_setting')
    
    #Inventory Operatuins
    inventory_root_access = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Inventory Root Access', related_name='global_permissions_inventory_root_access')
    inventory_purchase_order = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Inventory Purchase Order', related_name='global_permissions_inventory_purchase_order')
    inventory_goods_receipt = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Inventory Good Receipt', related_name='global_permissions_inventory_goods_receipt')
    inventory_consumption = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Inventory Consumption', related_name='global_permissions_inventory_consumption')
    inventory_stock_transfer = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Inventory Stock Transfer', related_name='global_permissions_inventory_stock_transfer')
    inventory_stock_report = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Inventory Stock Report', related_name='global_permissions_inventory_stock_report')
    inventory_report = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Inventory Report', related_name='global_permissions_inventory_report')
    
    #Target Control
    target_control_staff = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Target Control Staff Target', related_name='global_permissions_target_control_staff')
    target_control_store = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Target Control Store Target', related_name='global_permissions_target_control_store')
    target_control_service = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Target Control Service Target', related_name='global_permissions_target_control_service')
    target_control_retail = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Target Control Retail Target', related_name='global_permissions_target_control_retail')
    
    #Reports
    reports_root_access = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Report Root Access', related_name='global_permissions_reports_root_access')
    reports_commission = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Report Commission', related_name='global_permissions_reports_commission')
    reports_staff = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Report Staff', related_name='global_permissions_reports_staff')
    reports_store = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Report Store', related_name='global_permissions_reports_store')
    reports_service = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Report Service', related_name='global_permissions_reports_service')
    reports_retail = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Report Retail', related_name='global_permissions_reports_retail')
    
    #Online Profie
    profile_root_access = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Profile Root Access', related_name='global_permissions_profile_root_access')
    profile_list = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Profile List Access', related_name='global_permissions_profile_list')
    
    #Product
    product_root_access = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Product Root Access', related_name='global_permissions_product_root_access')
    
    #Client
    client_root_access = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client Root Access', related_name='global_permissions_client_root_access')
    client_list = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client list', related_name='global_permissions_client_list')
    client_profile = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client Profile', related_name='global_permissions_client_profile')
    client_groups = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client Groups', related_name='global_permissions_client_groups')
    client_discount = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client Discount/Promotions', related_name='global_permissions_client_discount')
    client_reward = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client Reward/Promotions', related_name='global_permissions_client_reward')
    client_loyality = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client loyality ', related_name='global_permissions_client_loyality')
    client_sharing = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Client Sharing Settings', related_name='global_permissions_client_sharing')
    
    #Employee
    employee_root_access = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Employee Root Access', related_name='global_permissions_employee_root_access')
    employee_new = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='New Employee', related_name='global_permissions_employee_new')
    employee_payroll = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Employee Payroll', related_name='global_permissions_employee_payroll')
    employee_attendance = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Employee attendance', related_name='global_permissions_employee_attendance')
    employee_staff_group = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Employee Staff Group', related_name='global_permissions_employee_staff_group')
    employee_reports = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Employee Reports', related_name='global_permissions_employee_reports')
    employee_commission = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Employee Commission', related_name='global_permissions_employee_commission')
    employee_work_schedule = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Employee Work Schedule', related_name='global_permissions_employee_work')
    employee_vacation = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Employee Vacation', related_name='global_permissions_employee_vacation')
    
    #Sales
    sales_root_access = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sales Root Access', related_name='global_permissions_sale_root_access')
    sales_apply_offer = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Sales Apply offer/Discount', related_name='global_permissions_sale_apply_offer')
    
    #Calender
    calender_root_access = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Calender Root Access', related_name='global_permissions_calender_root_access')
    calender_appointment = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Calender Appointment', related_name='global_permissions_calender_appointment')
    calender_block_time = models.ManyToManyField(GlobalPermissionChoices, verbose_name ='Calender Block time', related_name='global_permissions_calender_block_time')
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)