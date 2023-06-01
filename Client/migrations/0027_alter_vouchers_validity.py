# Generated by Django 3.2.15 on 2022-10-26 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0026_auto_20221026_1711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vouchers',
            name='validity',
            field=models.CharField(choices=[('7 Days', '7 Days'), ('14 Days', '14 Days'), ('1 Month', '1 Months'), ('2 Months', '2 Months'), ('3 Months', '3 Months'), ('4 Months', '4 Months'), ('6 Months', '6 Months'), ('8 Months', '8 Months'), ('1 Years', '1 Years'), ('18 Months', '18 Months'), ('2 Years', '2 Years'), ('5 Years', '5 Years')], default='7 Days', max_length=100, verbose_name='No of Days/Month'),
        ),
    ]
