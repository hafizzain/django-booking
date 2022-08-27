# Generated by Django 4.0.6 on 2022-08-27 05:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Business', '0011_businesstheme_theme_name'),
        ('Employee', '0006_alter_employee_ending_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('in_time', models.TimeField()),
                ('out_time', models.TimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_employee_attendances', to='Business.business')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_attendances', to='Employee.employee')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_attendances', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Employee Attendance',
                'verbose_name_plural': 'Employee Attendances',
            },
        ),
    ]
