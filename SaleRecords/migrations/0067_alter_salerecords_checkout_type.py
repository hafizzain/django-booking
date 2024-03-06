# Generated by Django 4.0.6 on 2024-02-12 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SaleRecords', '0066_alter_salerecords_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salerecords',
            name='checkout_type',
            field=models.CharField(choices=[('Appointment', 'Appointment Checkout'), ('Sale', 'Sale Checkout'), ('Refund', 'Refund')], max_length=50),
        ),
    ]