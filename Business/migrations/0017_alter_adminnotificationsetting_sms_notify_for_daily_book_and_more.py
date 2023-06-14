# Generated by Django 4.0.6 on 2022-09-06 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Business', '0016_alter_businessopeninghour_close_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminnotificationsetting',
            name='sms_notify_for_daily_book',
            field=models.BooleanField(default=False, verbose_name='Send SMS Notification for daily book'),
        ),
        migrations.AlterField(
            model_name='adminnotificationsetting',
            name='sms_notify_on_appoinment',
            field=models.BooleanField(default=False, verbose_name='Send SMS Notification on Apoinment'),
        ),
        migrations.AlterField(
            model_name='adminnotificationsetting',
            name='sms_notify_on_quick_sale',
            field=models.BooleanField(default=False, verbose_name='Send SMS Notification on quick sale'),
        ),
        migrations.AlterField(
            model_name='clientnotificationsetting',
            name='sms_for_ewallet_balance_on_quick_sale',
            field=models.BooleanField(default=False, verbose_name='Send SMS Notification for ewallet balance on quick sale'),
        ),
        migrations.AlterField(
            model_name='clientnotificationsetting',
            name='sms_for_rewards_on_quick_sale',
            field=models.BooleanField(default=False, verbose_name='Send SMS Notification for Rewards on quick Sale'),
        ),
        migrations.AlterField(
            model_name='clientnotificationsetting',
            name='sms_pending_payment',
            field=models.BooleanField(default=False, verbose_name='Send SMS Notification on Pending Payment'),
        ),
        migrations.AlterField(
            model_name='clientnotificationsetting',
            name='sms_purchase_plan',
            field=models.BooleanField(default=False, verbose_name='Send SMS Notification on Purchase Plan'),
        ),
        migrations.AlterField(
            model_name='staffnotificationsetting',
            name='sms_daily_sale',
            field=models.BooleanField(default=False, verbose_name='Send SMS Notification on Daily Sale'),
        ),
    ]
