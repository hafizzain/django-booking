# Generated by Django 4.0.6 on 2024-02-14 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0048_giftcards_retail_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='giftcards',
            name='retail_price',
        ),
        migrations.AddField(
            model_name='giftdetail',
            name='retail_price',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]