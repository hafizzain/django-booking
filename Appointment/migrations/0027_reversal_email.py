# Generated by Django 4.0.6 on 2024-01-24 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0026_reversal'),
    ]

    operations = [
        migrations.AddField(
            model_name='reversal',
            name='email',
            field=models.TextField(null=True),
        ),
    ]
