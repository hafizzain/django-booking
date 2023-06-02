# Generated by Django 3.2.15 on 2022-10-17 05:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Business', '0022_business_is_completed'),
        ('Service', '0008_service_slot_availible_for_online'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='location',
        ),
        migrations.AddField(
            model_name='service',
            name='location',
            field=models.ManyToManyField(blank=True, null=True, related_name='address_services_or_packages', to='Business.BusinessAddress'),
        ),
    ]
