# Generated by Django 4.0.6 on 2023-08-02 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0049_alter_appointmentemployeetip_gst_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointmentcheckout',
            name='service_price',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='appointmentcheckout',
            name='total_price',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]