# Generated by Django 4.0.6 on 2022-09-26 07:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Employee', '0011_commissionschemesetting'),
        ('Business', '0018_businesstype_image_path'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(default='', max_length=300)),
                ('treatment_type', models.CharField(blank=True, choices=[('Hair_Color', 'Hair Color'), ('test2', 'test2')], default='test2', max_length=20, null=True)),
                ('description', models.CharField(default='', max_length=100)),
                ('price', models.PositiveIntegerField(default=0, verbose_name='Sale Price')),
                ('duration', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('enable_team_comissions', models.BooleanField(blank=True, default=True, null=True, verbose_name='Enable Team Member Comission')),
                ('enable_vouchers', models.BooleanField(blank=True, default=False, null=True)),
                ('is_package', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_services_or_packages', to='Business.business')),
                ('employee', models.ManyToManyField(related_name='service_or_package_employe', to='Employee.employee')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='service_or_package_address', to='Business.businessaddress')),
                ('service', models.ManyToManyField(blank=True, null=True, related_name='package_services', to='Sale.service')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_services_or_packages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
