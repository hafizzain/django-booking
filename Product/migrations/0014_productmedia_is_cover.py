# Generated by Django 4.0.6 on 2022-09-03 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0013_auto_20220902_1316'),
    ]

    operations = [
        migrations.AddField(
            model_name='productmedia',
            name='is_cover',
            field=models.BooleanField(default=False),
        ),
    ]
