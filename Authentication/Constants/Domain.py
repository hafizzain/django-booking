

import subprocess

def ssl_sub_domain(domain):
    subprocess.call(f'sudo certbot --nginx -d {domain}.us-telecoms.com', shell=True)