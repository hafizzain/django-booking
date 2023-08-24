
# import boto3
# from django.conf import settings


# def upload_to_bucket(input_file, output_file):
#     session = boto3.Session(
#         aws_access_key_id= settings.AWS_ACCESS_KEY_ID,
#         aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY,
#     )
#     s3 = session.resource('s3')
#     filename = input_file
#     bucket = settings.AWS_STORAGE_BUCKET_NAME
#     key = output_file
#     s3.meta.client.upload_file(Filename=filename, Bucket=bucket, Key=key)