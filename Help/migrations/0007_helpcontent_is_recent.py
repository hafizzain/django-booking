# Generated by Django 4.0.6 on 2023-07-19 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Help', '0006_helpcontent_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='helpcontent',
            name='is_recent',
            field=models.BooleanField(default=False),
        ),
    ]
