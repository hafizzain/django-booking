# Generated by Django 4.0.6 on 2024-01-15 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0026_rename_date_giftcards_expire_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='giftcards',
            name='end_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='giftcards',
            name='start_date',
            field=models.DateField(null=True),
        ),
    ]
