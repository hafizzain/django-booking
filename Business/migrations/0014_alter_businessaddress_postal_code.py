# Generated by Django 3.2.15 on 2022-09-02 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Business', '0013_auto_20220901_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessaddress',
            name='postal_code',
            field=models.CharField(blank=True, default='', max_length=30, null=True),
        ),
    ]
