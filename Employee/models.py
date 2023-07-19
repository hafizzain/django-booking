from uuid import uuid4
from django.db import models
from django.utils.timezone import now


from Authentication.models import User
from Business.models import Business, BusinessAddress
from Utility.models import Country, State, City
from Service.models  import Service

class Employee(models.Model):
    GENDER_CHOICES = [
        ('Male' , 'Male'),
        ('Female' , 'Female'),
        ('Others' , 'Others'),
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_employees')

    full_name = models.CharField(max_length=300, default='')
    image = models.ImageField(upload_to='employee/employee_images/', null=True, blank=True)
    employee_id = models.CharField(max_length=50, default='')
    email = models.EmailField(verbose_name="email", max_length=60)
    mobile_number = models.CharField(max_length=30, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    is_mobile_verified = models.BooleanField(default=False)

    dob = models.DateField(verbose_name='Date of Birth', null=True, blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, default='Male', max_length=20)

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='country_employees')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='state_employees')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='city_employees')
    location = models.ManyToManyField(BusinessAddress, related_name='location_employee')
    
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(default='')

    joining_date = models.DateField(null=True, blank=True)
    to_present = models.BooleanField(default=False)
    ending_date = models.DateField(null=True, blank=True)
        
    is_default = models.BooleanField(default=False)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
    
class EmployeeProfessionalInfo(models.Model):
    # LEVEL_CHOICE =[
    #     ('Average', 'Average'),
    #     ('Above_Averge', 'Above Average'),
    # ]
    INCOME_TYPE_CHOICES = [
        ('Hourly_Rate', 'Hourly_Rate'),
        ('Daily_Income', 'Daily_Income'),
        ('Monthly_Salary', 'Monthly_Salary'),
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_professional_details')
    designation = models.CharField(max_length=300, default='')
    income_type = models.CharField(choices=INCOME_TYPE_CHOICES, default='Hourly_Rate', max_length=30)
    salary = models.PositiveIntegerField(default=0)
    #services = models.ManyToManyField(Service, through='EmployeeSelectedService' , related_name='services_employee')
    
    
    #level= models.CharField(max_length=100, choices=LEVEL_CHOICE, default = 'Average', verbose_name = 'Employee Level')
    
    #working_days = models.ManyToManyField(WorkingDays, related_name='days_employee')
    
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    maximum_discount = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    

    def __str__(self):
        return str(self.id)

class EmployeeSelectedService(models.Model):
    LEVEL_CHOICE =[
        ('Average', 'Average'),
        ('Above_Averge', 'Above Average'),
    ]
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='employee_service')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_selected_service')
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    level= models.CharField(max_length=100, choices=LEVEL_CHOICE, default = 'Average', verbose_name = 'Employee Service Level')

    def __str__(self):
        return str(self.id)

class EmployeePermissionSetting(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_permissions_setting')
    allow_calendar_booking = models.BooleanField(default=True)
    access_calendar = models.BooleanField(default=False)
    change_calendar_color = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)


class EmployeeModulePermission(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_module_permission')
    access_reports = models.BooleanField(default=False)
    access_sales = models.BooleanField(default=False)
    access_inventory = models.BooleanField(default=False)
    access_expenses = models.BooleanField(default=False)
    access_products = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)

class EmployeeMarketingPermission(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_marketing_permission')
    access_voucher = models.BooleanField(default=False)
    access_member_discount = models.BooleanField(default=False)
    access_invite_friend = models.BooleanField(default=False)
    access_loyalty_points = models.BooleanField(default=False)
    access_gift_cards = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)


class StaffGroup(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_staff_group')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_staff_group')

    name = models.CharField(max_length=300, default='')
    employees = models.ManyToManyField(Employee, related_name='staff_group_employees')

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class StaffGroupModulePermission(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    staff_group = models.ForeignKey(StaffGroup, on_delete=models.CASCADE, related_name='staff_group_module_permissions')

    access_reports = models.BooleanField(default=True)
    access_sales = models.BooleanField(default=False)
    access_inventory = models.BooleanField(default=False)
    access_expenses = models.BooleanField(default=True)
    access_products = models.BooleanField(default=False)

    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class Attendance(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_attendances')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_employee_attendances')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_attendances')

    in_time = models.TimeField()
    out_time = models.TimeField(null=True, blank=True)

    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)


    class Meta:
        verbose_name = 'Employee Attendance'
        verbose_name_plural = 'Employee Attendances'
        

class Payroll(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_payrolls')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_employee_payrolls')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_payrolls')
    
    name = models.CharField(max_length=300, default='')
    created_at = models.DateTimeField(auto_now_add=now)
    Total_hours = models.CharField(max_length=300, default='')
    
    def __str__(self):
        return str(self.id)
class SallarySlipPayrol(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_sallary_slip')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_employee_sallary_slip')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_sallary_slip')
    
    month = models.DateTimeField(null = True)
    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)


class CommissionSchemeSetting(models.Model):
    COMMISSION_CHOICES =[
        ('Every day', 'Every day'),
        ('Every week', 'Every week'),
        ('Every 2 week', 'Every 2 week'),
        ('Every 4 week', 'Every 4 week'),
        ('Every month', 'Every month'),
        ('Every quarter', 'Every quarter'),
        ('Every 6 months', 'Every 6 months'),
        ('Every year', 'Every year'),

    ]
    
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_commission_setting')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_commission_setting')
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_commissioin', null=True, blank=True)
    from_value = models.PositiveIntegerField(default=0, null=True, blank=True)
    to_value = models.PositiveIntegerField(default=0, null=True, blank=True)
    percentage = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    commission_cycle = models.CharField(choices=COMMISSION_CHOICES, max_length=50, default='Every day',)
    
    sale_price_before_discount = models.BooleanField(default=True)
    sale_price_including_tax = models.BooleanField(default=True)
    service_price_before_membership_discount = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)

class CategoryCommission(models.Model):
    COMMISSION_CHOICE = [
        ('percentage', 'percentage'),
        ('currency', 'currency'),
    ]
    CATEGORY_CHOICES =[
        ('Service', 'Service'),
        ('Retail', 'Retail'),
        ('Voucher', 'Voucher'),
    ]
    
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    commission = models.ForeignKey(CommissionSchemeSetting, on_delete=models.CASCADE, related_name='categorycommission_commission')
    
    from_value = models.PositiveIntegerField(default=0, null=True, blank=True)
    to_value = models.CharField(max_length=50, null=True, blank= True)
    commission_percentage = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    category_comission = models.CharField(choices=CATEGORY_CHOICES, max_length=50, default='Service',)
    comission_choice = models.CharField(choices=COMMISSION_CHOICE, max_length=50, default='percentage',)
    symbol = models.CharField(max_length=50, null=True, blank= True)
    
    created_at = models.DateTimeField(auto_now_add=now)

    
    def calculated_commission(self, price):
        value = self.commission_percentage
        if self.comission_choice == 'percentage':
            value = (self.commission_percentage * price) / 100

        return value
        
    
    def __str__(self):
        return str(self.id)

class Asset(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_assets')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_assets')
    
    name = models.CharField(max_length=300, default='')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_assets')
    given_date = models.DateField(verbose_name = 'given date')
    return_date = models.DateField(null=True, blank=True, verbose_name = 'return date')
    
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)
    
class AssetDocument(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE , related_name='asset_documents')
    
    document = models.FileField(upload_to='employee/assets/documents/')
    
    def __str__(self):
        return str(self.id)
    
class Vacation(models.Model):

    HOLIDAY_TYPE = (
        ('Vacation', 'Vacation'),
        ('Absence', 'Absence'),
    )
    
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null = True, related_name='user_vacation')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null = True , related_name='business_vacation')
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_vacation')

    holiday_type = models.CharField(choices=HOLIDAY_TYPE, default='Vacation', max_length=100)
    
    from_date = models.DateField(verbose_name = 'From Date', null=True)
    to_date = models.DateField(verbose_name = 'To Date', null=True)
    note = models.CharField(max_length=300, default='')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)
    
class EmployeDailySchedule(models.Model):
    DAYS_CHOICE =[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null = True, related_name='user_employedailyschedule')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null = True , related_name='business_employedailyschedule')
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_employedailyschedule')
    day = models.CharField(choices=DAYS_CHOICE, default='Monday', max_length=50, null=True, blank = True)
    #today_date = models.DateField(verbose_name = 'Today Date', null=True)
    vacation=models.ForeignKey(Vacation, on_delete=models.SET_NULL, null=True ,blank=True, related_name='vacation_employedailyschedules')
    
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    
    start_time_shift = models.TimeField(null=True, blank=True) #  =>>  Will be terminated
    end_time_shift = models.TimeField(null=True, blank=True) # =>>   Will be terminated
    
    from_date = models.DateField(verbose_name = 'From Date', null=True) #  =>>  Will be terminated
    to_date = models.DateField(verbose_name = 'To Date', null=True) # =>>   Will be terminated
    note = models.CharField(max_length=300, default='', null=True)
    
    date = models.DateTimeField(verbose_name = 'Date', null=True)
    
    is_leave = models.BooleanField(default=False)
    is_off = models.BooleanField(default=False)
    is_vacation = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)


    @property
    def total_hours(self):
        from datetime import datetime , timedelta

        try:
            income_type = EmployeeProfessionalInfo.objects.get(employee=self.employee).income_type
        except:
            return 0
        
        if income_type == 'Hourly_Rate':
            if self.is_vacation:
                return 8
            elif self.is_leave:
                return 0
            else:
                pass
            
        if self.start_time is None or self.end_time is None:
            return 0  # Return '0' if any of the time values is None

        shift1_start = datetime.strptime(self.start_time.strftime("%H:%M:%S"), "%H:%M:%S")
        shift1_end = datetime.strptime(self.end_time.strftime("%H:%M:%S"), "%H:%M:%S")

        if shift1_end < shift1_start:
            shift1_end += timedelta(days=1)  # Add 1 day if the shift ends on the next day

        total_hours = (shift1_end - shift1_start).total_seconds() / 3600  # calculate the time difference in hours

        if self.start_time_shift and self.end_time_shift:
            shift2_start = datetime.strptime(self.start_time_shift.strftime("%H:%M:%S"), "%H:%M:%S")
            shift2_end = datetime.strptime(self.end_time_shift.strftime("%H:%M:%S"), "%H:%M:%S")

            if shift2_end < shift2_start:
                shift2_end += timedelta(days=1)  # Add 1 day if the shift ends on the next day

            shift2_hours = (shift2_end - shift2_start).total_seconds() / 3600  # calculate the time difference in hours
            total_hours += shift2_hours

        total_hours = float(total_hours)  # convert to integer
        return float(total_hours)

    
# class EmployeDailyShift(models.Model):
#     id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null = True, related_name='user_employedailyshift')
#     business = models.ForeignKey(Business, on_delete=models.CASCADE, null = True , related_name='business_employedailyshift')
    
#     dailyschedule = models.ForeignKey(EmployeDailySchedule, on_delete=models.CASCADE, related_name='dailyschedule_employedailyshift')
#     start_time = models.TimeField(null=True, blank=True)
#     end_time = models.TimeField(null=True, blank=True)
    
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=now)
    
#     def __str__(self):
#         return str(self.id)


class EmployeeCommission(models.Model):

    CATEGORY_CHOICES =[
        ('Service', 'Service'),
        ('Retail', 'Retail'),
        ('Voucher', 'Voucher'),
    ]

    COMMISSION_CHOICE = [
        ('percentage', 'percentage'),
        ('currency', 'currency'),
    ]

    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null = True, related_name='user_commissions')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_employee_commissions')
    location = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, related_name='location_employee_commissions')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='commissions')


    commission = models.ForeignKey(CommissionSchemeSetting, on_delete=models.SET_NULL, null=True, related_name='employee_commissions')
    category_commission = models.ForeignKey(CategoryCommission, on_delete=models.SET_NULL, null=True, related_name='employee_category_commissions')

    commission_category = models.CharField(choices=CATEGORY_CHOICES, max_length=50, default='Service')
    commission_type = models.CharField(choices=COMMISSION_CHOICE, max_length=50, default='percentage')

    sale_value = models.FloatField(default=0, verbose_name='Single Sold Item Current Price')

    commission_rate = models.FloatField(default=0, verbose_name='Commission Current rate for single sold item, Percentage/Price')
    #  Commission rate will be filtered based on COMMISSION_CHOICE, commission_type

    commission_amount = models.FloatField(default=0, verbose_name='Commission Amount get by Single Item Sold')
    symbol = models.CharField(max_length=50, default='', verbose_name='Percentage/Currency Symbol')

    item_name = models.CharField(max_length=500, default='', verbose_name='Sold Item Name')
    item_id = models.CharField(max_length=500, default='')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Sold Items Quantity')

    tip = models.FloatField(default=0)

    sale_id = models.CharField(max_length=128, null=True, blank=True)

    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(auto_now_add=now)

    @property
    def employee_calculated_commissions(self,):
        return float(0)

    @property
    def single_item_commission(self):
        return self.commission_amount
    
    @property
    def full_commission(self):
        return self.single_item_commission * self.quantity


    @property
    def total_price(self):
        return self.sale_value * self.quantity


    def __str__(self):
        return str(self.id)
