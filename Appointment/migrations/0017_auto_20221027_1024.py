# Generated by Django 3.2.15 on 2022-10-27 05:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0027_alter_vouchers_validity'),
        ('Appointment', '0016_appointmentservice_is_favourite'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointmentcheckout',
            name='membership',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_membership_appointments', to='Client.membership'),
        ),
        migrations.AddField(
            model_name='appointmentcheckout',
            name='promotion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_promotion_appointments', to='Client.promotion'),
        ),
        migrations.AddField(
            model_name='appointmentcheckout',
            name='rewards',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_reward_appointments', to='Client.rewards'),
        ),
        migrations.AddField(
            model_name='appointmentcheckout',
            name='voucher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checkout_voucher_appointments', to='Client.vouchers'),
        ),
    ]
