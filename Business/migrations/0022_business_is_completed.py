# Generated by Django 3.2.15 on 2022-10-06 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Business', '0021_businessaddress_banking'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='is_completed',
            field=models.BooleanField(default=False, verbose_name='Business setting completed'),
        ),
    ]
