# Generated by Django 4.0.6 on 2024-01-15 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0024_rename_expire_date_giftcards_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='giftcards',
            name='code',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='giftcards',
            name='title',
            field=models.TextField(blank=True, null=True),
        ),
    ]
