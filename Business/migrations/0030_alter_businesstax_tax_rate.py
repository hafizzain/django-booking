# Generated by Django 4.0.6 on 2023-08-03 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Business', '0029_businessaddress_is_default'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businesstax',
            name='tax_rate',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
