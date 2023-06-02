# Generated by Django 4.0.6 on 2023-05-23 12:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Order', '0026_redeemmembershipitem_service_and_more'),
        ('Appointment', '0043_appointment_is_promotion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointmentemployeetip',
            name='checkout',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_tips', to='Order.checkout'),
        ),
    ]