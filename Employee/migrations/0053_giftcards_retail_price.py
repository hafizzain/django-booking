# Generated by Django 4.0.6 on 2024-02-29 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0052_giftcards_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='giftcards',
            name='retail_price',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]