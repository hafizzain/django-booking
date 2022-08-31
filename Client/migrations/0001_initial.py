# Generated by Django 4.0.6 on 2022-08-31 09:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Utility', '0007_language_code'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Business', '0011_businesstheme_theme_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('full_name', models.CharField(default='', max_length=300)),
                ('image', models.ImageField(blank=True, null=True, upload_to='employee/employee_images/')),
                ('client_id', models.CharField(default='', max_length=50)),
                ('email', models.EmailField(default='', max_length=254)),
                ('mobile_number', models.CharField(default='', max_length=30)),
                ('is_email_verified', models.BooleanField(default=False)),
                ('is_mobile_verified', models.BooleanField(default=False)),
                ('dob', models.DateField(verbose_name='Date of Birth')),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')], default='Male', max_length=20)),
                ('postal_code', models.CharField(default='', max_length=20)),
                ('address', models.TextField(default='')),
                ('card_number', models.CharField(default='', max_length=30)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_blocked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_client', to='Business.business')),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='city_clients', to='Utility.city')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='country_clients', to='Utility.country')),
                ('state', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='state_clients', to='Utility.state')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
