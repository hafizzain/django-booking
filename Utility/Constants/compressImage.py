
import boto3
from django.conf import settings
from django.db import connection


def upload_to_bucket(input_file, output_file):
    session = boto3.Session(
        aws_access_key_id= settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY,
    )
    s3 = session.resource('s3')
    filename = input_file
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    schema_name = connection.schema_name

    key = f'{schema_name}/{output_file}'
    s3.meta.client.upload_file(Filename=filename, Bucket=bucket, Key=key)