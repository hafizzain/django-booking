# Generated by Django 4.0.6 on 2024-02-07 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SaleRecords', '0061_appliedmemberships_price_appliedvouchers_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='salerecords',
            name='change',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
