# Generated by Django 4.0.6 on 2024-02-20 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SaleRecords', '0072_alter_salerecordservices_service_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='salerecordsappointmentservices',
            name='discount_percentage',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='salerecordservices',
            name='discount_percentage',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='salerecordsproducts',
            name='discount_percentage',
            field=models.FloatField(blank=True, null=True),
        ),
    ]