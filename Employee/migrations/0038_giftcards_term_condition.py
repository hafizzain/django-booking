# Generated by Django 4.0.6 on 2024-01-17 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0037_alter_giftdetail_gift_card'),
    ]

    operations = [
        migrations.AddField(
            model_name='giftcards',
            name='term_condition',
            field=models.TextField(null=True),
        ),
    ]
