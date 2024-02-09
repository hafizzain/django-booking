# Generated by Django 4.0.6 on 2024-02-09 11:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0008_alter_vouchers_end_date'),
        ('Appointment', '0034_appointmentgroup_group_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='comments',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='Client.comments'),
        ),
    ]
