from Tenants.models import Tenant

from django.conf import settings
from Authentication.Constants.CreateTenant import add_business_types, add_software_types
from Utility.Constants.add_data_db import add_business_types, add_software_types, add_currencies, add_languages
from Utility.models import ExceptionRecord
import datetime
from uuid import uuid4

def CreateDummyTenants():
    total_tenants = Tenant.objects.all()
    total_tenants = len(total_tenants)
    start = datetime.datetime.now()
    
    ExceptionRecord.objects.create(
        status_code='200',
        text=f'Creating Tenants.... {start.strftime("%Y-%m-%d %A %H:%M:%S")}',
        method='GET',
        is_resolved = True
    )
    
    t_amount = 15
    for i in range(t_amount):

        count = total_tenants + i

        name = f'NST-{count}'
        new_id = str(uuid4())
        new_id = new_id.split('-')
        new_id = new_id[0]

        tenant_name = f'NStyle-Tenancy-{count}-{new_id}'
        
        tenant = Tenant.objects.create(
            name = name,
            domain=f'{tenant_name}.{settings.BACKEND_DOMAIN_NAME}',
            schema_name = tenant_name,
            is_active = False
        )

        if tenant is not None:
            add_business_types(tenant = tenant)
            add_software_types(tenant = tenant)
            add_currencies(tenant=tenant)
            try:
                add_languages(tenant=tenant)
            except:
                pass

        tenant.is_ready = True
        tenant.save()

    end = datetime.datetime.now()
    final = end - start
    ExceptionRecord.objects.create(
        status_code='200',
        text=f'{t_amount} Tenants Created in {final.seconds}',
        method='GET',
        is_resolved = True
    )
    print(f'Total Time Taken : {final.seconds} Seconds')