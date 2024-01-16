# Generated by Django 4.0.6 on 2024-01-15 11:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0022_appointmentcheckout_is_refund_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointmentservice',
            name='is_refund',
            field=models.CharField(blank=True, choices=[('refund', 'Refund'), ('cancel', 'Cancel')], default='', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='appointmentservice',
            name='previous_app_service_refunded',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='app_service_refunded', to='Appointment.appointmentservice'),
        ),
    ]
