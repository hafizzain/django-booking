
import datetime

import subprocess

from Utility.models import ExceptionRecord
from django.conf import settings
import route53
import aws_cdk.aws_apigateway as apigw

from route53.resource_record_set import AResourceRecordSet


api_key = 'AKIAWFYNXTJRSQWQAI4R'
secret_key = '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'
my_zone_id = 'Z064377638Y3H4LDQPEU5'
region_zone_id = 'ZP97RAFLXTNZK'
dns_name = 'dualstack.pos-nstyle-production-1779321222.ap-south-1.elb.amazonaws.com.'


def ssl_sub_domain(domain):
    time_start = datetime.datetime.now()

    command = f'sudo certbot --nginx -d {domain}.{settings.BACKEND_DOMAIN_NAME}'
    subprocess.call(command, shell=True)

    time_end = datetime.datetime.now()
    time_diff = time_end - time_start

    total_seconds = time_diff.total_seconds()

    ExceptionRecord.objects.create(
        text = f'SSL Certificate TIME DIFF {total_seconds} Seconds for {domain} ---- {command}'
    )

    
def create_aws_domain_record(domain_name):
    from .AwsRoute53_boto import create_route53_alias_record
    create_route53_alias_record(domain_name)
