# Generated by Django 4.0.6 on 2024-02-07 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SaleRecords', '0060_rename_tax_percentage_saletax_tax_rate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appliedmemberships',
            name='price',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='appliedvouchers',
            name='price',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
