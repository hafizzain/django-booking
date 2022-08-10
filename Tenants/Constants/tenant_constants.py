


from cmath import e
from django_tenants.utils import tenant_context
from Tenants.models import Tenant
from Authentication.models import User


def set_schema(schema_name_=None, user=None):
    if schema_name_ is None and user is None:
        raise Exception('schema_name or user is required')

    try:
        if schema_name_ is not None:
            tenant_scm = Tenant.objects.get(schema_name=schema_name_)
        elif user is not None:
            tenant_scm = Tenant.objects.get(user=user)

    except Exception as err:
        print('ERROR: ' , err)
        raise Exception(err)

    with tenant_context(tenant_scm):
        return tenant_scm



def verify_tenant_email_mobile(prev_tenant_name='public', user=None, verify='Mobile'):
    if user is None:
        print('ERROR : User is None')
        return None

    set_schema(user=user)
    try:
        user = User.objects.get(username=user.username)
        if verify == 'Mobile':
            user.is_mobile_verified = True
        elif verify == 'Email':
            user.is_email_verified = True
        user.save()
        print('USER VERIFIED')
    except Exception as err:
        print('ERROR ' , err)
        return None
    set_schema(schema_name_=prev_tenant_name)