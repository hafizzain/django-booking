# Generated by Django 4.0.6 on 2024-03-07 07:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Authentication', '0002_user_address_user_city_user_country_user_zip_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='address',
        ),
        migrations.RemoveField(
            model_name='user',
            name='city',
        ),
        migrations.RemoveField(
            model_name='user',
            name='country',
        ),
        migrations.RemoveField(
            model_name='user',
            name='zip_code',
        ),
    ]
