# Generated by Django 4.0.6 on 2023-05-19 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0061_alter_loyaltypointlogs_points_earned'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loyaltypointlogs',
            name='balance',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
