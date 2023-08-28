# Generated by Django 4.0.6 on 2023-08-25 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Utility', '0014_exceptionrecord_method_exceptionrecord_path_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='is_flag_uploaded_s3',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='country',
            name='is_flag_uploaded_s3',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='software',
            name='is_image_uploaded_s3',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='state',
            name='is_flag_uploaded_s3',
            field=models.BooleanField(default=False),
        ),
    ]