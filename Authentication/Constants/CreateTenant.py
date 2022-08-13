


from Tenants.models import Tenant, Domain
from Business.models import Business
from Profile.models import Profile
from Utility.Constants.add_data_db import add_countries, add_states, add_cities, add_currencies, add_languages

from rest_framework.authtoken.models import Token
from django.conf import  settings

from django_tenants.utils import tenant_context
from Authentication.models import AccountType, User, NewsLetterDetail
from Authentication.Constants import AuthTokenConstants
from Authentication.Constants.UserConstants import create_user_account_type
from threading import Thread


def create_tenant_user(tenant=None, data=None):
    if tenant is None or data is None:
        return None
    
    with tenant_context(tenant):

        first_name = data['first_name']
        last_name = data['last_name']
        social_account = data.get('social_account', False)

        user = User.objects.create_user(
            username = data['username'],
            email = data['email'],
            password = data['password']
        )

        user.first_name=first_name
        user.last_name=last_name
        user.full_name=f'{first_name} {last_name}'
        user.mobile_number = data['mobile_number']
        # user.is_superuser=True
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
        return user


def create_tenant_profile(tenant_user=None, data=None, tenant=None):
    if tenant_user is None or tenant is None:
        return None


    with tenant_context(tenant):
        user_profile = Profile.objects.create(
            user = tenant_user,
            is_active=True
        )
        return user_profile


def create_tenant_business(tenant_user=None, tenant_profile=None, tenant=None, data=None):
    if tenant_user is None or tenant is None or tenant_profile is None:
        return None
    
    with tenant_context(tenant):
        user_business = Business.objects.create(
            user = tenant_user,
            profile = tenant_profile,
            business_name = data.get('business_name', tenant_user.username)
        )
        return user_business


def create_tenant_user_token(tenant_user=None, tenant=None):
    print(tenant_user, tenant)
    if tenant_user is None or tenant is None :
        return None
    
    with tenant_context(tenant):
        user_token = Token(
            user=tenant_user,
        )
        user_token.save()
        return user_token


def create_tenant_account_type(tenant_user=None, tenant=None, account_type='everyone'):
    if tenant_user is None or tenant is None :
        return None
    
    with tenant_context(tenant):
        return AccountType.objects.create(
            user=tenant_user,
            account_type=account_type.capitalize()
        )

def add_data_to_tenant_thread(tenant=None):
    if tenant is None:
        return

    try:
        print('gonna create DB data')
        add_currencies(tenant=tenant)
        add_languages(tenant=tenant)
        add_countries(tenant=tenant)
        add_states(tenant=tenant)
        add_cities(tenant=tenant)
    except Exception as err:
        print(err)


def create_tenant(request=None, user=None, data=None):
    if user is None or data is None:
        return
    
    td_name = str(data.get('business_name', user.username)).strip().replace(' ' , '-').replace('.', '-').replace('/' , '-').lower()  # Tenant Domain name
    try:
        Domain.objects.get(
            domain=f'{td_name}.{settings.BACKEND_DOMAIN_NAME}'
        )
        all_domains_length = Domain.objects.all().count()
        td_name = td_name + f'-{int(all_domains_length)}'
    except:
        pass
    user_tenant = Tenant.objects.create(
        user=user,
        name=td_name,
        domain=f'{td_name}.{settings.BACKEND_DOMAIN_NAME}',
        schema_name=td_name
    )

    Domain.objects.create(
        user=user,
        schema_name=td_name,
        domain=f'{td_name}.{settings.BACKEND_DOMAIN_NAME}',
        tenant=user_tenant,
    )


    with tenant_context(user_tenant):
        t_user = create_tenant_user(tenant=user_tenant, data=data)
        print(t_user)
        
        if t_user is not None:
            NewsLetterDetail.objects.create(
                user = t_user,
                terms_condition=data.get('terms_condition', True),
                is_subscribed=data.get('terms_condition', False)
            )
            t_profile = create_tenant_profile(tenant_user=t_user, data=data, tenant=user_tenant)
            t_business = create_tenant_business(tenant_user=t_user, tenant_profile=t_profile, tenant=user_tenant, data=data)
            try:
                t_token = create_tenant_user_token(tenant_user=t_user, tenant=user_tenant)
            except:
                pass
            
            try:
                create_tenant_account_type(tenant_user=t_user, tenant=user_tenant, account_type=data['account_type'])
            except:
                pass
            try:
                thrd = Thread(target=add_data_to_tenant_thread, kwargs={'tenant' : user_tenant})
                thrd.start()
            except:
                pass

