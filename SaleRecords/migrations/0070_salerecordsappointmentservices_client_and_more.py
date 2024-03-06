# Generated by Django 4.0.6 on 2024-02-19 05:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0009_delete_comments'),
        ('Appointment', '0043_appointment_appointment_discount'),
        ('SaleRecords', '0069_rename_clinet_loyalty_point_redeemedloyaltypoints_client_loyalty_point'),
    ]

    operations = [
        migrations.AddField(
            model_name='salerecordsappointmentservices',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointment_client', to='Client.client'),
        ),
        migrations.AddField(
            model_name='salerecordsappointmentservices',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointment_group', to='Appointment.appointmentgroup'),
        ),
    ]