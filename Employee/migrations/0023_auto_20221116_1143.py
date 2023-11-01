# Generated by Django 3.2.15 on 2022-11-16 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0022_auto_20221116_1033'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='location_employe',
        ),
        migrations.AddField(
            model_name='employee',
            name='location',
            field=models.ManyToManyField(related_name='location_employee', to='Business.BusinessAddress'),
        ),
    ]
