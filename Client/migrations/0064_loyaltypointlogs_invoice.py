# Generated by Django 4.0.6 on 2023-06-01 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0063_client_is_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='loyaltypointlogs',
            name='invoice',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
