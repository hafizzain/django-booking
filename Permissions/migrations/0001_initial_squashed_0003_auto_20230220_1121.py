# Generated by Django 4.0.6 on 2023-11-01 07:22

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    replaces = [('Permissions', '0001_initial'), ('Permissions', '0002_auto_20221018_0958'), ('Permissions', '0003_auto_20230220_1121')]

    dependencies = [
        ('Employee', '0020_auto_20221014_1252'),
        ('Utility', '0012_auto_20221015_1633'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployePermission',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_permissions', to='Employee.employee')),
                ('staffgroup', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staffGroup_permissions', to='Employee.staffgroup')),
                ('account_business_setting', models.ManyToManyField(related_name='global_permissions_account_business_setting', to='Utility.globalpermissionchoices', verbose_name='Account Business Setting')),
                ('account_finance_setting', models.ManyToManyField(related_name='global_permissions_account_finance_setting', to='Utility.globalpermissionchoices', verbose_name='Account Finance Setting')),
                ('account_notification_setting', models.ManyToManyField(related_name='global_permissions_account_notification_setting', to='Utility.globalpermissionchoices', verbose_name='Account Service Setting')),
                ('account_root_access', models.ManyToManyField(related_name='global_permissions_account_root_access', to='Utility.globalpermissionchoices', verbose_name='Account Root Access')),
                ('account_service_management', models.ManyToManyField(related_name='global_permissions_account_service_setting', to='Utility.globalpermissionchoices', verbose_name='Account Service Setting')),
                ('calender_appointment', models.ManyToManyField(related_name='global_permissions_calender_appointment', to='Utility.globalpermissionchoices', verbose_name='Calender Appointment')),
                ('calender_block_time', models.ManyToManyField(related_name='global_permissions_calender_block_time', to='Utility.globalpermissionchoices', verbose_name='Calender Block time')),
                ('calender_root_access', models.ManyToManyField(related_name='global_permissions_calender_root_access', to='Utility.globalpermissionchoices', verbose_name='Calender Root Access')),
                ('client_discount', models.ManyToManyField(related_name='global_permissions_client_discount', to='Utility.globalpermissionchoices', verbose_name='Client Discount/Promotions')),
                ('client_groups', models.ManyToManyField(related_name='global_permissions_client_groups', to='Utility.globalpermissionchoices', verbose_name='Client Groups')),
                ('client_list', models.ManyToManyField(related_name='global_permissions_client_list', to='Utility.globalpermissionchoices', verbose_name='Client list')),
                ('client_loyality', models.ManyToManyField(related_name='global_permissions_client_loyality', to='Utility.globalpermissionchoices', verbose_name='Client loyality ')),
                ('client_profile', models.ManyToManyField(related_name='global_permissions_client_profile', to='Utility.globalpermissionchoices', verbose_name='Client Profile')),
                ('client_reward', models.ManyToManyField(related_name='global_permissions_client_reward', to='Utility.globalpermissionchoices', verbose_name='Client Reward/Promotions')),
                ('client_root_access', models.ManyToManyField(related_name='global_permissions_client_root_access', to='Utility.globalpermissionchoices', verbose_name='Client Root Access')),
                ('client_sharing', models.ManyToManyField(related_name='global_permissions_client_sharing', to='Utility.globalpermissionchoices', verbose_name='Client Sharing Settings')),
                ('employee_attendance', models.ManyToManyField(related_name='global_permissions_employee_attendance', to='Utility.globalpermissionchoices', verbose_name='Employee attendance')),
                ('employee_commission', models.ManyToManyField(related_name='global_permissions_employee_commission', to='Utility.globalpermissionchoices', verbose_name='Employee Commission')),
                ('employee_new', models.ManyToManyField(related_name='global_permissions_employee_new', to='Utility.globalpermissionchoices', verbose_name='New Employee')),
                ('employee_payroll', models.ManyToManyField(related_name='global_permissions_employee_payroll', to='Utility.globalpermissionchoices', verbose_name='Employee Payroll')),
                ('employee_reports', models.ManyToManyField(related_name='global_permissions_employee_reports', to='Utility.globalpermissionchoices', verbose_name='Employee Reports')),
                ('employee_root_access', models.ManyToManyField(related_name='global_permissions_employee_root_access', to='Utility.globalpermissionchoices', verbose_name='Employee Root Access')),
                ('employee_staff_group', models.ManyToManyField(related_name='global_permissions_employee_staff_group', to='Utility.globalpermissionchoices', verbose_name='Employee Staff Group')),
                ('employee_vacation', models.ManyToManyField(related_name='global_permissions_employee_vacation', to='Utility.globalpermissionchoices', verbose_name='Employee Vacation')),
                ('employee_work_schedule', models.ManyToManyField(related_name='global_permissions_employee_work', to='Utility.globalpermissionchoices', verbose_name='Employee Work Schedule')),
                ('inventory_consumption', models.ManyToManyField(related_name='global_permissions_inventory_consumption', to='Utility.globalpermissionchoices', verbose_name='Inventory Consumption')),
                ('inventory_goods_receipt', models.ManyToManyField(related_name='global_permissions_inventory_goods_receipt', to='Utility.globalpermissionchoices', verbose_name='Inventory Good Receipt')),
                ('inventory_purchase_order', models.ManyToManyField(related_name='global_permissions_inventory_purchase_order', to='Utility.globalpermissionchoices', verbose_name='Inventory Purchase Order')),
                ('inventory_report', models.ManyToManyField(related_name='global_permissions_inventory_report', to='Utility.globalpermissionchoices', verbose_name='Inventory Report')),
                ('inventory_root_access', models.ManyToManyField(related_name='global_permissions_inventory_root_access', to='Utility.globalpermissionchoices', verbose_name='Inventory Root Access')),
                ('inventory_stock_report', models.ManyToManyField(related_name='global_permissions_inventory_stock_report', to='Utility.globalpermissionchoices', verbose_name='Inventory Stock Report')),
                ('inventory_stock_transfer', models.ManyToManyField(related_name='global_permissions_inventory_stock_transfer', to='Utility.globalpermissionchoices', verbose_name='Inventory Stock Transfer')),
                ('mobile_root_access', models.ManyToManyField(related_name='global_permissions_mobile_root_access', to='Utility.globalpermissionchoices', verbose_name='Mobile Root Access')),
                ('pos_root_access', models.ManyToManyField(related_name='global_permissions_pos_root_access', to='Utility.globalpermissionchoices', verbose_name='POS Root Access')),
                ('product_root_access', models.ManyToManyField(related_name='global_permissions_product_root_access', to='Utility.globalpermissionchoices', verbose_name='Product Root Access')),
                ('profile_list', models.ManyToManyField(related_name='global_permissions_profile_list', to='Utility.globalpermissionchoices', verbose_name='Profile List Access')),
                ('profile_root_access', models.ManyToManyField(related_name='global_permissions_profile_root_access', to='Utility.globalpermissionchoices', verbose_name='Profile Root Access')),
                ('reports_commission', models.ManyToManyField(related_name='global_permissions_reports_commission', to='Utility.globalpermissionchoices', verbose_name='Report Commission')),
                ('reports_retail', models.ManyToManyField(related_name='global_permissions_reports_retail', to='Utility.globalpermissionchoices', verbose_name='Report Retail')),
                ('reports_root_access', models.ManyToManyField(related_name='global_permissions_reports_root_access', to='Utility.globalpermissionchoices', verbose_name='Report Root Access')),
                ('reports_service', models.ManyToManyField(related_name='global_permissions_reports_service', to='Utility.globalpermissionchoices', verbose_name='Report Service')),
                ('reports_staff', models.ManyToManyField(related_name='global_permissions_reports_staff', to='Utility.globalpermissionchoices', verbose_name='Report Staff')),
                ('reports_store', models.ManyToManyField(related_name='global_permissions_reports_store', to='Utility.globalpermissionchoices', verbose_name='Report Store')),
                ('sales_apply_offer', models.ManyToManyField(related_name='global_permissions_sale_apply_offer', to='Utility.globalpermissionchoices', verbose_name='Sales Apply offer/Discount')),
                ('sales_root_access', models.ManyToManyField(related_name='global_permissions_sale_root_access', to='Utility.globalpermissionchoices', verbose_name='Sales Root Access')),
                ('target_control_retail', models.ManyToManyField(related_name='global_permissions_target_control_retail', to='Utility.globalpermissionchoices', verbose_name='Target Control Retail Target')),
                ('target_control_service', models.ManyToManyField(related_name='global_permissions_target_control_service', to='Utility.globalpermissionchoices', verbose_name='Target Control Service Target')),
                ('target_control_staff', models.ManyToManyField(related_name='global_permissions_target_control_staff', to='Utility.globalpermissionchoices', verbose_name='Target Control Staff Target')),
                ('target_control_store', models.ManyToManyField(related_name='global_permissions_target_control_store', to='Utility.globalpermissionchoices', verbose_name='Target Control Store Target')),
            ],
        ),
    ]
