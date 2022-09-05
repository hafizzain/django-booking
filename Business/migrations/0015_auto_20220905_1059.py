# Generated by Django 3.2.15 on 2022-09-05 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Business', '0014_alter_businessaddress_postal_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminnotificationsetting',
            name='email_notify_on_daily_book',
            field=models.BooleanField(default=False, verbose_name='Send Email Notification on Daily Book'),
        ),
        migrations.AlterField(
            model_name='clientnotificationsetting',
            name='sms_appoinment_reschedule',
            field=models.BooleanField(default=False, verbose_name='Send SMS Notification on Appoinment reschedule'),
        ),
        migrations.AlterField(
            model_name='clientnotificationsetting',
            name='sms_birthday',
            field=models.BooleanField(default=False, verbose_name='Send SMS Notification on Birthday'),
        ),
        migrations.AlterField(
            model_name='clientnotificationsetting',
            name='sms_pending_services_quicksale',
            field=models.BooleanField(default=False, verbose_name='Send SMS Notification on Pending Services Quick Sale'),
        ),
    ]
