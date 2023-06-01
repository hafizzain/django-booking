# Generated by Django 4.0.6 on 2022-10-01 05:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Business', '0021_businessaddress_banking'),
        ('Employee', '0018_alter_employeeprofessionalinfo_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(default='', max_length=300)),
                ('given_date', models.DateField(verbose_name='given date')),
                ('return_date', models.DateField(blank=True, null=True, verbose_name='return date')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_assets', to='Business.business')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_assets', to='Employee.employee')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_assets', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AssetDocument',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('document', models.FileField(upload_to='employee/assets/documents/')),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asset_documents', to='Employee.asset')),
            ],
        ),
    ]
