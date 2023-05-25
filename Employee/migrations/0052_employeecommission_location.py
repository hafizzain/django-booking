# Generated by Django 4.0.6 on 2023-05-25 10:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Business', '0029_businessaddress_is_default'),
        ('Employee', '0051_alter_employeecommission_commission_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeecommission',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='location_employee_commissions', to='Business.businessaddress'),
        ),
    ]
