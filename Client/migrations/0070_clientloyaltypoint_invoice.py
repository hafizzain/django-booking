# Generated by Django 4.0.6 on 2023-07-11 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0069_alter_loyaltypoints_number_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientloyaltypoint',
            name='invoice',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
