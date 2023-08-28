# Generated by Django 4.0.6 on 2023-08-28 05:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Appointment', '0055_appointmentservice_is_redeemed_and_more'),
        ('Business', '0031_businesstaxsetting'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Service', '0032_alter_service_initial_deposit_alter_service_price'),
        ('Employee', '0055_alter_categorycommission_commission_percentage_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeBookingDailyInsights',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('day_time_choice', models.CharField(choices=[('M', 'Morning'), ('A', 'Afternoon'), ('E', 'Evening')], default=None, max_length=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_daily_insights', to='Appointment.appointment')),
                ('appointment_service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_daily_insights', to='Appointment.appointmentservice')),
                ('business', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_daily_insights', to='Business.business')),
                ('business_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_daily_insights', to='Business.businessaddress')),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_daily_insights', to='Employee.employee')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_daily_insights', to='Service.service')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_daily_insights', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]