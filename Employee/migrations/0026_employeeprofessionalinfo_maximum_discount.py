# Generated by Django 3.2.15 on 2022-12-08 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0025_rename_duration_commissionschemesetting_category_com'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeprofessionalinfo',
            name='maximum_discount',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
