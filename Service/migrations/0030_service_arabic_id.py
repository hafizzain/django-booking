# Generated by Django 4.0.6 on 2023-07-12 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Service', '0029_rename_urdu_name_service_arabic_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='arabic_id',
            field=models.CharField(default='', editable=False, max_length=999, unique=True),
        ),
    ]
