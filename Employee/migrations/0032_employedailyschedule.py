# Generated by Django 3.2.15 on 2022-12-18 19:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Employee', '0031_alter_employeeprofessionalinfo_maximum_discount'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeDailySchedule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('day', models.CharField(blank=True, choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], default='Monday', max_length=50, null=True)),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('start_time_shift', models.TimeField(blank=True, null=True)),
                ('end_time_shift', models.TimeField(blank=True, null=True)),
                ('is_leave', models.BooleanField(default=False)),
                ('is_off', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('business', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_employedailyschedule', to='Business.business')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_employedailyschedule', to='Employee.employee')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_employedailyschedule', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
