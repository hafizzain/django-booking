# Generated by Django 4.0.6 on 2022-09-19 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Business', '0017_alter_adminnotificationsetting_sms_notify_for_daily_book_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='businesstype',
            name='image_path',
            field=models.CharField(blank=True, default='', max_length=2000, null=True),
        ),
    ]
