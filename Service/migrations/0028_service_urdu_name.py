# Generated by Django 4.0.6 on 2023-07-12 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Service', '0027_priceservice_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='urdu_name',
            field=models.CharField(default='', max_length=999),
        ),
    ]
