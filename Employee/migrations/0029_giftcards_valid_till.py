# Generated by Django 4.0.6 on 2024-01-15 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0028_giftcards_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='giftcards',
            name='valid_till',
            field=models.CharField(blank=True, choices=[('7 Days', '7 Days'), ('14 Days', '14 Days'), ('1 Month', '1 Months'), ('2 Months', '2 Months'), ('3 Months', '3 Months'), ('4 Months', '4 Months'), ('6 Months', '6 Months'), ('8 Months', '8 Months'), ('1 Years', '1 Years'), ('18 Months', '18 Months'), ('2 Years', '2 Years'), ('5 Years', '5 Years')], default='7 Days', max_length=100, null=True, verbose_name='No of Days/Month'),
        ),
    ]
