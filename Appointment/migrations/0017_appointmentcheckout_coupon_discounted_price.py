# Generated by Django 4.0.6 on 2023-12-27 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0016_appointmentservice_client_tag_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointmentcheckout',
            name='coupon_discounted_price',
            field=models.FloatField(null=True),
        ),
    ]