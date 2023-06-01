# Generated by Django 3.2.15 on 2022-10-15 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Service', '0007_rename_treatment_type_service_service_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='slot_availible_for_online',
            field=models.CharField(choices=[('Anytime_In_The_Future', 'Anytime In The Future'), ('No_More_Than_1_Months_In_The_Future', 'No More Than 1 Months In The Future'), ('No_More_Than_2_Months_In_The_Future', 'No More Than 2 Months In The Future'), ('No_More_Than_3_Months_In_The_Future', 'No More Than 3 Months In The Future')], default='Anytime_In_The_Future', max_length=100),
        ),
    ]
