# Generated by Django 4.0.6 on 2023-12-29 06:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0002_leavemanagement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leavemanagement',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_leaves', to='Employee.employee'),
        ),
    ]
