# Generated by Django 3.2.15 on 2022-09-02 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Client', '0005_clientgroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientgroup',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254, null=True),
        ),
    ]
