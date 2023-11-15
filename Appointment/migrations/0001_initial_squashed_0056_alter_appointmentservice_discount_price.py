# Generated by Django 4.0.6 on 2023-11-01 07:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    replaces = [('Appointment', '0001_initial'), ('Appointment', '0002_checkout'), ('Appointment', '0003_appointmentservice_and_more'), ('Appointment', '0004_appointment_discount_type_appointment_payment_method_and_more'), ('Appointment', '0005_alter_appointmentservice_duration'), ('Appointment', '0006_appointmentservice_appointment_status'), ('Appointment', '0007_auto_20220923_1045'), ('Appointment', '0008_alter_appointmentservice_duration'), ('Appointment', '0009_alter_appointmentservice_duration'), ('Appointment', '0010_appointmentnotes'), ('Appointment', '0011_alter_appointment_payment_method'), ('Appointment', '0012_alter_appointmentnotes_text'), ('Appointment', '0013_alter_appointmentservice_appointment_status'), ('Appointment', '0014_auto_20221020_1048'), ('Appointment', '0015_appointmentcheckout_business_address'), ('Appointment', '0016_appointmentservice_is_favourite'), ('Appointment', '0017_auto_20221027_1024'), ('Appointment', '0018_appointmentservice_price'), ('Appointment', '0019_rename_destails_appointmentservice_details'), ('Appointment', '0020_alter_appointmentservice_duration'), ('Appointment', '0021_alter_appointmentservice_appointment_time'), ('Appointment', '0022_auto_20230201_1600'), ('Appointment', '0023_auto_20230202_1137'), ('Appointment', '0024_auto_20230203_1759'), ('Appointment', '0025_appointment_member'), ('Appointment', '0026_appointment_extra_price'), ('Appointment', '0027_appointment_tip'), ('Appointment', '0028_appointment_discount_price'), ('Appointment', '0029_auto_20230223_1658'), ('Appointment', '0030_appointment_is_checkout'), ('Appointment', '0031_auto_20230301_1308'), ('Appointment', '0032_auto_20230302_1016'), ('Appointment', '0033_appointmentcheckout_gst_price'), ('Appointment', '0034_alter_appointmentcheckout_gst_price'), ('Appointment', '0035_appointmentlogs'), ('Appointment', '0036_appointmentlogs_appointment_appointmentlogs_location'), ('Appointment', '0037_logdetails'), ('Appointment', '0038_alter_appointmentlogs_customer_type'), ('Appointment', '0039_appointmentemployeetip'), ('Appointment', '0040_appointmentcheckout_is_promotion_and_more'), ('Appointment', '0041_alter_appointmentcheckout_service_commission'), ('Appointment', '0042_alter_appointmentcheckout_gst'), ('Appointment', '0043_appointment_is_promotion_and_more'), ('Appointment', '0044_appointmentemployeetip_checkout'), ('Appointment', '0045_alter_appointmentservice_price'), ('Appointment', '0046_alter_appointmentservice_discount_percentage_and_more'), ('Appointment', '0047_alter_appointmentlogs_log_type'), ('Appointment', '0048_appointmentlogs_user'), ('Appointment', '0049_alter_appointmentemployeetip_gst_and_more'), ('Appointment', '0050_alter_appointmentcheckout_service_price_and_more'), ('Appointment', '0051_alter_appointment_discount_price_and_more'), ('Appointment', '0052_alter_appointment_discount_percentage_and_more'), ('Appointment', '0053_appointmentcheckout_gst1_and_more'), ('Appointment', '0054_appointmentcheckout_tax_name_and_more'), ('Appointment', '0055_appointmentservice_is_redeemed_and_more'), ('Appointment', '0056_alter_appointmentservice_discount_price')]

    dependencies = [
        ('Business', '0001_initial_squashed_0038_alter_businessvendor_email'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Service', '0001_initial'),
        ('Service', '0003_service_price'),
        ('Client', '0009_delete_rewards'),
        ('Service', '0013_auto_20221019_1035'),
        ('Client', '0027_alter_vouchers_validity'),
        ('Employee', '0001_initial_squashed_0056_employee_is_image_uploaded_s3'),
        ('Order', '0026_redeemmembershipitem_service_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('business', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='business_appointments', to='Business.business')),
                ('business_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointment_address', to='Business.businessaddress')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_appointments', to=settings.AUTH_USER_MODEL, verbose_name='Creator ( User )')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client_appointments', to='Client.client')),
                ('client_type', models.CharField(blank=True, choices=[('IN HOUSE', 'IN HOUSE'), ('SALOON', 'SALOON')], max_length=50, null=True)),
                ('discount_type', models.CharField(blank=True, choices=[('Promotions', 'Promotions'), ('Rewards', 'Rewards'), ('Vouchers', 'Vouchers'), ('Memberships', 'Memberships'), ('Subscriptions', 'Subscriptions')], max_length=50, null=True)),
                ('payment_method', models.CharField(blank=True, choices=[('Cash', 'Cash'), ('Voucher', 'Voucher'), ('SplitBill', 'SplitBill'), ('MasterCard', 'MasterCard'), ('Visa', 'Visa'), ('Paypal', 'Paypal'), ('GooglePay', 'Google Pay'), ('ApplePay', 'Apple Pay')], default='', max_length=100, null=True)),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_appointments_lg', to='Employee.employee')),
                ('extra_price', models.FloatField(blank=True, default=0, null=True)),
                ('tip', models.FloatField(blank=True, default=0, null=True)),
                ('discount_price', models.FloatField(blank=True, default=0, null=True)),
                ('service_commission', models.FloatField(blank=True, default=0, null=True)),
                ('service_commission_type', models.CharField(default='', max_length=50)),
                ('is_checkout', models.BooleanField(default=False)),
                ('discount_percentage', models.FloatField(blank=True, default=0, null=True)),
                ('is_promotion', models.BooleanField(default=False)),
                ('selected_promotion_id', models.CharField(default='', max_length=800)),
                ('selected_promotion_type', models.CharField(default='', max_length=400)),
            ],
        ),
        migrations.CreateModel(
            name='AppointmentNotes',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('text', models.TextField(blank=True, default='', null=True)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointment_notes', to='Appointment.appointment')),
            ],
        ),
        migrations.CreateModel(
            name='AppointmentService',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('appointment_date', models.DateField()),
                ('appointment_time', models.TimeField(verbose_name='Appointment Start Time')),
                ('duration', models.CharField(default='', max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointment_services', to='Appointment.appointment')),
                ('business', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_appointment_services', to='Business.business')),
                ('business_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='b_address_appointment_services', to='Business.businessaddress')),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member_appointments', to='Employee.employee')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='serivce_appointments', to='Service.service')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_appointment_services', to=settings.AUTH_USER_MODEL, verbose_name='Creator ( User )')),
                ('tip', models.FloatField(blank=True, default=0, null=True)),
                ('appointment_status', models.CharField(choices=[('Appointment_Booked', 'Appointment Booked'), ('Arrived', 'Arrived'), ('In Progress', 'In Progress'), ('Done', 'Done'), ('Paid', 'Paid'), ('Cancel', 'Cancel')], default='Appointment Booked', max_length=100)),
                ('details', models.CharField(blank=True, max_length=255, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('is_favourite', models.BooleanField(default=False)),
                ('price', models.FloatField(blank=True, default=0, null=True)),
                ('service_commission', models.FloatField(blank=True, default=0, null=True)),
                ('service_commission_type', models.CharField(default='', max_length=50)),
                ('client_can_book', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('slot_availible_for_online', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('discount_percentage', models.FloatField(blank=True, default=0, null=True)),
                ('discount_price', models.FloatField(blank=True, default=None, null=True)),
                ('total_price', models.FloatField(blank=True, default=0, null=True)),
                ('is_redeemed', models.BooleanField(default=False)),
                ('redeemed_instance_id', models.CharField(default='', max_length=800)),
                ('redeemed_price', models.FloatField(default=0)),
                ('redeemed_type', models.CharField(default='', max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='AppointmentLogs',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('log_type', models.CharField(blank=True, choices=[('Create', 'Create'), ('Edit', 'Edit'), ('Reschedule', 'Reschedule'), ('Cancel', 'Cancel'), ('done', 'Done')], max_length=50, null=True)),
                ('customer_type', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointmentlogs_staffname', to='Employee.employee')),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointmentlogs_service_type', to='Appointment.appointment')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointmentlogs_location', to='Business.businessaddress')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_appointments_logs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LogDetails',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('start_time', models.TimeField()),
                ('duration', models.CharField(default='', max_length=400)),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('appointment_service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='app_service_logs', to='Appointment.appointmentservice')),
                ('log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointment_log_details', to='Appointment.appointmentlogs')),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member_log_details', to='Employee.employee')),
            ],
        ),
        migrations.CreateModel(
            name='AppointmentEmployeeTip',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('tip', models.FloatField(blank=True, default=0, null=True)),
                ('gst', models.FloatField(blank=True, default=0, null=True)),
                ('gst_price', models.FloatField(blank=True, default=0, null=True)),
                ('service_price', models.FloatField(blank=True, default=0, null=True)),
                ('total_price', models.FloatField(blank=True, default=0, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tips_checkout', to='Appointment.appointment')),
                ('business', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_appointment_tips', to='Business.business')),
                ('business_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointment_address_tips', to='Business.businessaddress')),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_member_tips', to='Employee.employee')),
                ('checkout', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_tips', to='Order.checkout')),
            ],
        ),
        migrations.CreateModel(
            name='AppointmentCheckout',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('payment_method', models.CharField(blank=True, choices=[('Cash', 'Cash'), ('Voucher', 'Voucher'), ('SplitBill', 'SplitBill'), ('MasterCard', 'MasterCard'), ('Visa', 'Visa'), ('Paypal', 'Paypal'), ('GooglePay', 'Google Pay'), ('ApplePay', 'Apple Pay')], default='', max_length=100, null=True)),
                ('tip', models.FloatField(blank=True, default=0, null=True)),
                ('gst', models.FloatField(blank=True, default=0, null=True)),
                ('service_price', models.FloatField(blank=True, default=0, null=True)),
                ('total_price', models.FloatField(blank=True, default=0, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointment_checkout', to='Appointment.appointment')),
                ('appointment_service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointment_service_checkout', to='Appointment.appointmentservice')),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_member_appointments', to='Employee.employee')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_service_appointments', to='Service.service')),
                ('business_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointment_address_checkout', to='Business.businessaddress')),
                ('membership', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_membership_appointments', to='Client.membership')),
                ('promotion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_promotion_appointments', to='Client.promotion')),
                ('rewards', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_reward_appointments', to='Client.rewards')),
                ('voucher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_voucher_appointments', to='Client.vouchers')),
                ('service_commission', models.DecimalField(blank=True, decimal_places=5, default=0, max_digits=8, null=True)),
                ('service_commission_type', models.CharField(default='', max_length=50)),
                ('gst_price', models.FloatField(blank=True, default=0, null=True)),
                ('is_promotion', models.BooleanField(default=False)),
                ('selected_promotion_id', models.CharField(default='', max_length=800)),
                ('selected_promotion_type', models.CharField(default='', max_length=400)),
                ('gst1', models.FloatField(blank=True, default=0, null=True)),
                ('gst_price1', models.FloatField(blank=True, default=0, null=True)),
                ('tax_name', models.CharField(default='', max_length=250)),
                ('tax_name1', models.CharField(default='', max_length=250)),
            ],
        ),
    ]
