# Generated by Django 3.2.15 on 2022-12-13 06:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Business', '0022_business_is_completed'),
        ('Employee', '0030_alter_commissionschemesetting_commission_cycle'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffTarget',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('month', models.CharField(choices=[('January', 'January'), ('February', 'February'), ('March', 'March'), ('April', 'April'), ('May', 'May'), ('June', 'June'), ('July', 'July'), ('August', 'August'), ('September', 'September'), ('October', 'October'), ('November', 'November'), ('December', 'December')], default='January', max_length=100)),
                ('service_target', models.PositiveIntegerField(default=0)),
                ('retail_target', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_stafftarget', to='Business.business')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_stafftarget', to='Employee.employee')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_stafftarget', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
