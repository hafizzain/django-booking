# Generated by Django 4.0.6 on 2024-01-15 10:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Employee', '0023_employedailyschedule_is_holiday_due_to_update'),
    ]

    operations = [
        migrations.RenameField(
            model_name='giftcards',
            old_name='expire_date',
            new_name='date',
        ),
    ]
