


from Tenants.models import Tenant, Domain
from Utility.Constants.add_data_db import add_countries, add_states, add_cities

from django_tenants.utils import tenant_context
from Authentication.models import User
from Authentication.Constants import AuthTokenConstants
from Authentication.Constants.UserConstants import create_user_account_type
from threading import Thread

def add_data_to_tenant_thread(tenant=None):
    if tenant is None:
        return

    try:
        print('gonna create countries')
        add_countries(tenant=tenant)
        add_states(tenant=tenant)
        add_cities(tenant=tenant)
    except Exception as err:
        print(err)


def create_tenant(request=None, user=None, data=None):
    if user is None or data is None:
        return
    
    user_tenant = Tenant.objects.create(
        user=user,
        name=user.username,
        domain=user.username,
        schema_name=user.username
    )

    Domain.objects.create(
        user=user,
        schema_name=user.username,
        domain=f'{user.username}.localhost',
        tenant=user_tenant,
    )


    with tenant_context(user_tenant):
        username = data['username']
        email = data['email']
        password = data['password']
        first_name = data['first_name']
        last_name = data['last_name']
        mobile_number = data['mobile_number']
        social_account = data.get('social_account', False)
        print(username, password)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.first_name=first_name
        user.last_name=last_name
        user.full_name=f'{first_name} {last_name}'
        user.mobile_number=mobile_number
        user.is_superuser=True
        user.is_staff=True
        user.is_admin=True
        user.is_active=True

        if social_account and social_account is not None:
            social_platform = data.get('social_platform', None)
            social_id = data.get('social_id', None)
            user.social_account = True
            if social_platform is not None:
                user.social_platform = social_platform
            if social_id is not None:
                user.social_id = social_id

        user.save()
        # AuthTokenConstants.create_user_token(user=user, tenant=user_tenant)
        create_user_account_type(user=user, account_type=data['account_type'])
        try:
            thrd = Thread(target=add_data_to_tenant_thread, kwargs={'tenant' : user_tenant})
            thrd.start()
        except:
            pass

