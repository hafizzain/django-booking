# Generated by Django 3.2.15 on 2022-10-04 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Service', '0004_auto_20221004_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='duration',
            field=models.CharField(blank=True, choices=[('30_Min', '30 Min'), ('60_Min', '60 Min'), ('90_Min', '90 Min'), ('120_Min', '120 Min'), ('150_Min', '150 Min'), ('180_Min', '180 Min'), ('210_Min', '210 Min')], max_length=50, null=True),
        ),
    ]
