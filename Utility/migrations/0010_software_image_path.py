# Generated by Django 4.0.6 on 2022-09-19 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Utility', '0009_exceptionrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='software',
            name='image_path',
            field=models.CharField(blank=True, default='', max_length=2000, null=True),
        ),
    ]
