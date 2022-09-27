# Generated by Django 3.2.15 on 2022-09-27 05:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Business', '0018_businesstype_image_path'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Employee', '0011_commissionschemesetting'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeprofessionalinfo',
            name='end_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employeeprofessionalinfo',
            name='start_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='WorkingDays',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('monday', models.BooleanField(default=False)),
                ('tuesday', models.BooleanField(default=False)),
                ('wednesday', models.BooleanField(default=False)),
                ('thursday', models.BooleanField(default=False)),
                ('firday', models.BooleanField(default=False)),
                ('saturday', models.BooleanField(default=False)),
                ('sunday', models.BooleanField(default=False)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='working_busines', to='Business.business')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='working_days', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='employeeprofessionalinfo',
            name='working_days',
            field=models.ManyToManyField(related_name='days_employee', to='Employee.WorkingDays'),
        ),
    ]
