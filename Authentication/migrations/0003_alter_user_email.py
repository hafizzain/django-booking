# Generated by Django 3.2.15 on 2023-01-18 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Authentication', '0002_user_is_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=60, verbose_name='email'),
        ),
    ]
