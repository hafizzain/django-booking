# Generated by Django 4.0.6 on 2023-12-29 13:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0001_initial_squashed_0053_brand_is_image_uploaded_s3_and_more'),
        ('Finance', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RefundProduct',
            new_name='RefundProducts',
        ),
    ]
