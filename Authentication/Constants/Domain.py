
import datetime

import subprocess

from Utility.models import ExceptionRecord


def ssl_sub_domain(domain):
    time_start = datetime.datetime.now()

    subprocess.call(f'sudo certbot --nginx -d {domain}.us-telecoms.com', shell=True)

    time_end = datetime.datetime.now()
    time_diff = time_end - time_start

    total_seconds = time_diff.total_seconds()

    ExceptionRecord.objects.create(
        text = f'SSL Certificate TIME DIFF . {total_seconds} Seconds'
    )
            