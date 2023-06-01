# Generated by Django 3.2.15 on 2022-09-27 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0014_remove_workingdays_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employeeprofessionalinfo',
            name='working_days',
        ),
        migrations.AddField(
            model_name='employeeprofessionalinfo',
            name='firday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employeeprofessionalinfo',
            name='monday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employeeprofessionalinfo',
            name='saturday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employeeprofessionalinfo',
            name='sunday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employeeprofessionalinfo',
            name='thursday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employeeprofessionalinfo',
            name='tuesday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employeeprofessionalinfo',
            name='wednesday',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='WorkingDays',
        ),
    ]
