import boto3
import uuid

from Utility.models import ExceptionRecord
import datetime
from django.conf import settings


def create_route53_alias_record(domain_name):
    ExceptionRecord.objects.create(text = f'Starting :: create_route53_alias_record')
    time_start = datetime.datetime.now()
    try:
        route53_client = boto3.client('route53', aws_access_key_id=settings.AWS_API_KEY, aws_secret_access_key=settings.AWS_SECRET_KEY)
        changes = [{
            'Action': 'CREATE',
            'ResourceRecordSet': {
                'Name': f'{domain_name}',
                'Type': 'A',
                # 'TTL': 60,
                'AliasTarget': {
                    'DNSName': settings.AWS_DNS_NAME,
                    'EvaluateTargetHealth': True,
                    'HostedZoneId': settings.AWS_REGION_ZONE_ID,
                },
                # 'ResourceRecords': [
                #     {
                #         'Value': '172.31.0.0'
                #     },
                # ],
            },
        }]

        response = route53_client.change_resource_record_sets(HostedZoneId=settings.AWS_MY_ZONE_ID, ChangeBatch={'Changes': changes})
        print(response)

    except Exception as err:
        print(f"Error creating A record: {err}")
        ExceptionRecord.objects.create(text = f'AWS Record Creation ERROR :: {str(err)}')
        return False
    else:
        time_end = datetime.datetime.now()
        time_diff = time_end - time_start

        total_seconds = time_diff.total_seconds()

        ExceptionRecord.objects.create(text = f'AWS Record Creation DIFF {total_seconds} Seconds for {domain_name}')
        ExceptionRecord.objects.create(text = f'response :: {str(response)}')
        return True