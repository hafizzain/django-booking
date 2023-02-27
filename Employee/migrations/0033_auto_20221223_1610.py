# Generated by Django 3.2.15 on 2022-12-23 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0032_employedailyschedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='employedailyschedule',
            name='from_date',
            field=models.DateField(null=True, verbose_name='From Date'),
        ),
        migrations.AddField(
            model_name='employedailyschedule',
            name='is_vacation',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employedailyschedule',
            name='note',
            field=models.CharField(default='', max_length=300),
        ),
        migrations.AddField(
            model_name='employedailyschedule',
            name='to_date',
            field=models.DateField(null=True, verbose_name='To Date'),
        ),
    ]
