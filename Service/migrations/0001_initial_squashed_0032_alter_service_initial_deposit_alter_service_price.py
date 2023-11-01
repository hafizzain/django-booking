# Generated by Django 4.0.6 on 2023-11-01 07:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    replaces = [('Service', '0001_initial'), ('Service', '0002_alter_service_business'), ('Service', '0003_service_price'), ('Service', '0004_auto_20221004_1221'), ('Service', '0005_alter_service_duration'), ('Service', '0006_auto_20221015_1620'), ('Service', '0007_rename_treatment_type_service_service_type'), ('Service', '0008_service_slot_availible_for_online'), ('Service', '0009_auto_20221017_1012'), ('Service', '0010_alter_service_controls_time_slot'), ('Service', '0011_auto_20221017_1755'), ('Service', '0012_alter_service_initial_deposit'), ('Service', '0013_auto_20221019_1035'), ('Service', '0014_alter_service_service_type'), ('Service', '0015_alter_service_service_type'), ('Service', '0016_remove_service_employee'), ('Service', '0017_alter_service_service_type'), ('Service', '0018_alter_service_service_type'), ('Service', '0019_servicegroup'), ('Service', '0020_auto_20221108_0943'), ('Service', '0021_alter_service_service_availible'), ('Service', '0022_alter_priceservice_duration'), ('Service', '0023_servicegroup_allow_client_to_select_team_member'), ('Service', '0024_priceservice_currency'), ('Service', '0025_service_is_default'), ('Service', '0026_alter_priceservice_price'), ('Service', '0027_priceservice_created_at'), ('Service', '0028_service_urdu_name'), ('Service', '0029_rename_urdu_name_service_arabic_name'), ('Service', '0030_service_arabic_id'), ('Service', '0031_servicetranlations'), ('Service', '0032_alter_service_initial_deposit_alter_service_price')]

    dependencies = [
        ('Business', '0009_businessvendor'),
        ('Business', '0021_businessaddress_banking'),
        ('Employee', '0019_asset_assetdocument'),
        ('Business', '0017_alter_adminnotificationsetting_sms_notify_for_daily_book_and_more'),
        ('Business', '0022_business_is_completed'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Utility', '0012_auto_20221015_1633'),
        ('Utility', '0013_turnoverproductrecord'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(default='', max_length=100)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_services_or_packages', to='Business.business')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_services_or_packages', to=settings.AUTH_USER_MODEL)),
                ('price', models.FloatField(default=0)),
                ('description', models.CharField(default='', max_length=255)),
                ('enable_team_comissions', models.BooleanField(blank=True, default=True, null=True, verbose_name='Enable Team Member Comission')),
                ('enable_vouchers', models.BooleanField(blank=True, default=False, null=True)),
                ('is_package', models.BooleanField(default=False)),
                ('parrent_service', models.ManyToManyField(blank=True, null=True, related_name='parent_package_services', to='Service.service')),
                ('client_can_book', models.CharField(blank=True, choices=[('Anytime', 'Anytime'), ('5_Hours_Before', '5 Hours Before'), ('12_Hours_Before', '12 Hours Before'), ('24_Hours_Before', '24 Hours Before'), ('36_Hours_Before', '36 Hours Before')], default='Anytime', max_length=100, null=True)),
                ('controls_time_slot', models.CharField(blank=True, choices=[('30_Mins', '30 Mins'), ('60_Mins', '60 Mins'), ('90_Mins', '90 Mins'), ('120_Mins', '120 Mins')], default='30_Mins', max_length=100, null=True)),
                ('initial_deposit', models.FloatField(blank=True, default=0, null=True)),
                ('slot_availible_for_online', models.CharField(blank=True, choices=[('Anytime_In_The_Future', 'Anytime In The Future'), ('No_More_Than_1_Months_In_The_Future', 'No More Than 1 Months In The Future'), ('No_More_Than_2_Months_In_The_Future', 'No More Than 2 Months In The Future'), ('No_More_Than_3_Months_In_The_Future', 'No More Than 3 Months In The Future')], default='Anytime_In_The_Future', max_length=100, null=True)),
                ('location', models.ManyToManyField(blank=True, null=True, related_name='address_services_or_packages', to='Business.businessaddress')),
                ('service_availible', models.CharField(blank=True, choices=[('Everyone', 'Everyone'), ('Male', 'Male'), ('Female', 'Female')], default='Everyone', max_length=50, null=True)),
                ('is_default', models.BooleanField(default=False)),
                ('arabic_name', models.CharField(default='', max_length=999)),
                ('arabic_id', models.CharField(default='', editable=False, max_length=999)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceGroup',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(default='', max_length=100)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('business', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_servicesgroup', to='Business.business')),
                ('services', models.ManyToManyField(blank=True, null=True, related_name='servicegroup_services', to='Service.service')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_servicesgroup', to=settings.AUTH_USER_MODEL)),
                ('allow_client_to_select_team_member', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='PriceService',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('duration', models.CharField(blank=True, choices=[('30_Min', '30 Min'), ('60_Min', '60 Min'), ('90_Min', '90 Min'), ('120_Min', '120 Min'), ('150_Min', '150 Min'), ('180_Min', '180 Min'), ('210_Min', '210 Min')], max_length=50, null=True)),
                ('price', models.FloatField(default=0)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_priceservice', to='Service.service')),
                ('currency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='priceservice_currency', to='Utility.currency')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceTranlations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_name', models.CharField(blank=True, max_length=500, null=True)),
                ('language', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Utility.language')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Service.service')),
            ],
        ),
    ]
