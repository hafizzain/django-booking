# Generated by Django 4.0.6 on 2023-12-19 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0011_clientmissedopportunity_dependency_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='cancel_note',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='cancel_reason',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
