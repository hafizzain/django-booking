# Generated by Django 3.2.18 on 2023-03-02 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0042_sallaryslippayrol'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='email',
            field=models.EmailField(max_length=60, verbose_name='email'),
        ),
    ]
