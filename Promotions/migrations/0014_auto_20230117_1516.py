# Generated by Django 3.2.15 on 2023-01-17 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Promotions', '0013_auto_20230117_1445'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spendsomeamountandgetdiscount',
            name='business',
        ),
        migrations.RemoveField(
            model_name='spendsomeamountandgetdiscount',
            name='user',
        ),
    ]
