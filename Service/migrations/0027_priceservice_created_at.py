# Generated by Django 4.0.6 on 2023-07-08 07:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Service', '0026_alter_priceservice_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='priceservice',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]