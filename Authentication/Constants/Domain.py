
import datetime

import subprocess

from Utility.models import ExceptionRecord
from django.conf import settings
import route53
import aws_cdk.aws_apigateway as apigw

from route53.resource_record_set import AResourceRecordSet


api_key = 'AKIAWFYNXTJRSQWQAI4R'
secret_key = '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'
zone_name = 'ap-south-1'
zone_id = 'Z064377638Y3H4LDQPEU5'




dns_server = '172.31.0.0'
dns_server1 = 'dualstack.pos-nstyle-production-1779321222.ap-south-1.elb.amazonaws.com'

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
            

# def create_aws_domain_record(domain_name):
#     ExceptionRecord.objects.create(text = f'Starting :: create_aws_domain_hosted_zone')
#     time_start = datetime.datetime.now()

#     try:
#         conn = route53.connect(
#             aws_access_key_id = api_key,
#             aws_secret_access_key = secret_key,
#         )
#         zone = conn.get_hosted_zone_by_id(zone_id)

#         new_record, change_info = zone.create_a_record(
#             name = f'{domain_name}.',
#             values=[dns_server,],
#             # alias_hosted_zone_id = zone_id,

#             alias_dns_name = dns_server1,
#             set_identifier='AliasRecord',
#             weight='1',

#         )
#         # region = zone_name,
#         # ttl = None,
        
#     except Exception as err:
#         print(f'ERROR :: {err}')
#         ExceptionRecord.objects.create(text = f'AWS Record Creation ERROR :: {str(err)}')
#     else:
#         print(change_info)

#         time_end = datetime.datetime.now()
#         time_diff = time_end - time_start

#         total_seconds = time_diff.total_seconds()

#         ExceptionRecord.objects.create(text = f'AWS Hosted ZONE TIME DIFF {total_seconds} Seconds for {domain_name}')
#         ExceptionRecord.objects.create(text = f'Zone ID :: {new_record}')
#         ExceptionRecord.objects.create(text = f'change_info :: {str(change_info)}')

def create_aws_domain_record(domain_name):
    try:
        conn = route53.connect(
            aws_access_key_id = api_key,
            aws_secret_access_key = secret_key,
        )
        zone = conn.get_hosted_zone_by_id(zone_id)


        a_c = AResourceRecordSet(
            connection=conn,
            zone_id=zone_id,
            name=domain_name,
            records=[],
            ttl=60,
            alias_dns_name='ap-south-1.elb.amazonaws.com',
            alias_hosted_zone_id=zone_id
        )
        print(a_c.is_alias_record_set())
        a_c.save()


        print(zone)
        return
        new_record, change_info = zone.create_a_record(
            name = f'{domain_name}',
            values=[dns_server1,],
            alias_hosted_zone_id = zone_id,
            alias_dns_name = 'ap-south-1.elb.amazonaws.com',
            # set_identifier='AliasRecord',
            # weight='1',
            is_alias_record_set=True,
            # region = zone_name,

        )
        # ttl = None,
        
    except Exception as err:
        print(f'ERROR :: {err}')
    else:
        print(change_info)