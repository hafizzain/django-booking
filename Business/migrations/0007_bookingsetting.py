# Generated by Django 4.0.6 on 2022-08-15 06:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Business', '0006_stocknotificationsetting_staffnotificationsetting_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingSetting',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('cancel_or_reschedule', models.CharField(choices=[('Anytime', 'Anytime'), ('12_Hours_Prior_To_The_Appoinment', '12 Hours Prior To The Appoinment'), ('24_Hours_Prior_To_The_Appoinment', '24 Hours Prior To The Appoinment'), ('36_Hours_Prior_To_The_Appoinment', '36 Hours Prior To The Appoinment')], default='Anytime', max_length=100)),
                ('client_can_book', models.CharField(choices=[('Anytime', 'Anytime'), ('5_Hours_Before', '5 Hours Before'), ('12_Hours_Before', '12 Hours Before'), ('24_Hours_Before', '24 Hours Before'), ('36_Hours_Before', '36 Hours Before')], default='Anytime', max_length=100)),
                ('controls_time_slot', models.CharField(choices=[('Anytime_In_The_Future', 'Anytime In The Future'), ('No_More_Than_1_Months_In_The_Future', 'No More Than 1 Months In The Future'), ('No_More_Than_2_Months_In_The_Future', 'No More Than 2 Months In The Future'), ('No_More_Than_3_Months_In_The_Future', 'No More Than 3 Months In The Future')], default='Anytime_In_The_Future', max_length=100)),
                ('time_slots_interval', models.CharField(choices=[('15_Mins', '15 Mins'), ('30_Mins', '30 Mins'), ('45_Mins', '45 Mins'), ('60_Mins', '60 Mins'), ('120_Mins', '120 Mins')], default='15_Mins', max_length=50)),
                ('allow_client_to_select_team_member', models.BooleanField(default=True)),
                ('send_to_client', models.BooleanField(default=False)),
                ('send_to_specific_email_address', models.BooleanField(default=False)),
                ('auto_confirmation', models.BooleanField(default=False)),
                ('admin_confirmation', models.BooleanField(default=False)),
                ('start_time', models.BooleanField(default=True)),
                ('services', models.BooleanField(default=True)),
                ('duration', models.BooleanField(default=False)),
                ('choose_team_member', models.BooleanField(default=True)),
                ('select_payment_type', models.BooleanField(default=False)),
                ('initial_deposit', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('business', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='business_booking_setting', to='Business.business')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_booking_setting', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
