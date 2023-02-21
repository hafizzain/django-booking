


from Authentication.Constants.Domain import ssl_sub_domain
from Tenants.models import Tenant, Domain
from Business.models import Business, BusinessPaymentMethod, BusinessType
from Profile.models import Profile
from Utility.Constants.add_data_db import add_business_types, add_countries, add_software_types, add_states, add_cities, add_currencies, add_languages
from Utility.models import ExceptionRecord
from Utility.models import GlobalPermissionChoices

from rest_framework.authtoken.models import Token
from django.conf import  settings

from django_tenants.utils import tenant_context
from Authentication.models import AccountType, User, NewsLetterDetail
from Authentication.Constants import AuthTokenConstants
from Authentication.Constants.UserConstants import create_user_account_type
from threading import Thread
from Service.models import Service

import datetime


def create_tenant_user(tenant=None, data=None):
    if tenant is None or data is None:
        return None
    
    with tenant_context(tenant):

        first_name = data['first_name']
        last_name = data['last_name']
        social_account = data.get('social_account', None)

        user = User.objects.create_user(
            username = data['username'],
            email = data['email'],
            password = data['password']
        )

        user.first_name=first_name
        user.last_name=last_name
        user.full_name=f'{first_name} {last_name}'
        user.mobile_number = data['mobile_number']
        user.is_superuser=True
        user.is_staff=True
        user.is_admin=True
        user.is_active=True

        if social_account is not None:
            user.is_email_verified = True
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

    tnt_start_time = datetime.datetime.now()

    with tenant_context(tenant):

        time_end = datetime.datetime.now()
        time_diff = time_end - tnt_start_time

        total_seconds = time_diff.seconds

        ExceptionRecord.objects.create(
            text = f'SWITCH TENANT TIME DIFF . {total_seconds} Seconds'
        )

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
        

def create_tenant_account_type(tenant_user=None, tenant=None, account_type='Business'):
    if tenant_user is None or tenant is None :
        return None
    
    with tenant_context(tenant):
        return AccountType.objects.create(
            user=tenant_user,
            account_type= account_type#account_type.capitalize()
        )

def create_global_permission(tenant=None, user = None, business=None):
     if tenant is not None and user is not None and business is not None:
        with tenant_context(tenant):
            permission = [
    
                        "export",
                        "edit",
                        "invoice",
                        'modify',
                        'add',
                        'delete',
                        'email',
                        'filter',
                        'turnover',
                        'import',
                        'create',
                        'order',
                        'view',
                        'modify',
                        'cancel',
                        'reschedule',
                    ]
            for per in permission:
                GlobalPermissionChoices.objects.create(
                    text = per,
                    slug = per,
                )

def default_payment_method(tenant=None, user = None, business=None):
    if tenant is not None and user is not None and business is not None:
        with tenant_context(tenant):
            payment_method= [
    
                        "Cash",
                        "Mastercard",
                        "Visa",
                        'Paypal',
                        'GooglePay',
                        'ApplePay',
                    ]
            for pay in payment_method:
                BusinessPaymentMethod.objects.create(
                    user = user,
                    business = business,
                    method_type = pay,
                   
                )
                

# def create_service_user(tenant=None, user = None, business=None):
#     if tenant is not None and user is not None and business is not None:
#         with tenant_context(tenant):

#             service_list = [
#                 {
#                     'name' : 'Car wash',
#                     'price' : 355
#                 },
#                 {
#                     'name' : 'Haircolor',
#                     'price' : 123
#                 },
#                 {
#                     'name' : 'Bridal Makeup',
#                     'price' : 87
#                 },
#                 {
#                     'name' : 'Menicure',
#                     'price' : 1997
#                 },
#                 {
#                     'name' : 'Pedicure',
#                     'price' : 9886
#                 },
#                 {
#                     'name' : 'Bike Service',
#                     'price' : 1223
#                 },
#                 {
#                     'name' : 'Bike Wash',
#                     'price' : 1124
#                 },
#             ]

#             for service in service_list :
#                 test = Service.objects.create(
#                         user = user, 
#                         name=service['name'],
#                         price= service['price']
#                     )  

        
def add_data_to_tenant_thread(tenant=None):
    if tenant is None:
        return

    time_start = datetime.datetime.now()

    try:
        print('gonna create DB data')
        add_currencies(tenant=tenant)
        add_languages(tenant=tenant)
        add_countries(tenant=tenant)
        add_states(tenant=tenant)
        add_cities(tenant=tenant)
    
    except Exception as err:
        print(err)
    else:

        time_end = datetime.datetime.now()
        time_diff = time_end - time_start

        total_seconds = time_diff.total_seconds()

        ExceptionRecord.objects.create(
            text = f'ADD DATA TO TENANT DB TIME DIFF . {total_seconds} Seconds'
        )
            


def create_tenant(request=None, user=None, data=None):
    time_start = datetime.datetime.now()
    
    if user is None or data is None:
        return
    
    td_name = str(data.get('business_name', user.username)).strip().replace(' ' , '-').replace('.', '').replace('/' , '-').lower()  # Tenant Domain name
    try:
        Domain.objects.get(
            domain=f'{td_name}.{settings.BACKEND_DOMAIN_NAME}'
        )
        all_domains_length = Domain.objects.all().count()
        td_name = td_name + f'-{int(all_domains_length)}'
    except:
        pass
    try:
        user_domain_name = f'{td_name}.{settings.BACKEND_DOMAIN_NAME}'
        all_tenants = Tenant.objects.filter(
            user__isnull = True,
            is_active = False
        )
        if len(all_tenants) > 0:
            user_tenant = all_tenants[0]
            # user_tenant = Tenant.objects.create(
            #     user=user,
            #     name=td_name,
            #     domain=f'{td_name}.{settings.BACKEND_DOMAIN_NAME}',
            #     schema_name=td_name
            # )
            user_tenant.user = user
            user_tenant.domain = user_domain_name
            user_tenant.is_active = True
            user_tenant.save()
        else:
            ExceptionRecord.objects.create(
                text = f'Tenant was not found DUMMY'
            )
            user_tenant = Tenant.objects.create(
                user=user,
                name=td_name,
                domain = user_domain_name,
                schema_name=td_name
            )
        
        ExceptionRecord.objects.create(
            text = f'Check domain errors . {user_tenant} line 272 craete_tenat'
        )
        
        Domain.objects.create(
            user=user,
            schema_name=td_name,
            domain=f'{td_name}.{settings.BACKEND_DOMAIN_NAME}',
            tenant=user_tenant,
        )
    except Exception as err:
        ExceptionRecord.objects.create(
            text = f'Check domain errors . {str(err)} {user_tenant} line 272 craete_tenat'
    )


    with tenant_context(user_tenant):

        try:
            thrd = Thread(target=ssl_sub_domain, args=[td_name])
            thrd.start()
        except:
            pass
        
        t_user = create_tenant_user(tenant=user_tenant, data=data)
        
        if t_user is not None:

            t_profile = create_tenant_profile(tenant_user=t_user, data=data, tenant=user_tenant)
            t_business = create_tenant_business(tenant_user=t_user, tenant_profile=t_profile, tenant=user_tenant, data=data)
            try:
                ubs_type = BusinessType.objects.get(slug=data['business_industry']) # User Business Type
                t_business.business_types.add(ubs_type)
                t_business.save()
            except:
                pass
            
            try:
                t_token = create_tenant_user_token(tenant_user=t_user, tenant=user_tenant)
            except:
                pass
            # NewsLetterDetail.objects.create(
            #     user = t_user,
            #     terms_condition=data.get('terms_condition', True),
            #     is_subscribed=data.get('terms_condition', False)
            # )

            try:
                create_tenant_account_type(tenant_user=t_user, tenant=user_tenant, account_type='Business')#data['account_type'])
            except:
                pass
            
            # try:
            #     service_thrd = Thread(target=create_service_user, kwargs={'tenant' :user_tenant , 'user' : t_user, 'business': t_business})
            #     service_thrd.start()
            # except:
            #     pass
            try:
                service_thrd = Thread(target=create_global_permission, kwargs={'tenant' :user_tenant , 'user' : t_user, 'business': t_business})
                service_thrd.start()
            except:
                pass
            
            try:
                payment_thrd = Thread(target=default_payment_method, kwargs={'tenant' :user_tenant , 'user' : t_user, 'business': t_business})
                payment_thrd.start()
            except:
                pass

            try:
                thrd = Thread(target=add_business_types, kwargs={'tenant' : user_tenant})
                thrd.start()
            except:
                pass
            try:
                thrd = Thread(target=add_software_types, kwargs={'tenant' : user_tenant})
                thrd.start()
            except:
                pass
            
            try:
                thrd = Thread(target=add_data_to_tenant_thread, kwargs={'tenant' : user_tenant})
                thrd.start()
            except:
                pass
    
    time_end = datetime.datetime.now()
    time_diff = time_end - time_start

    total_seconds = time_diff.total_seconds()

    ExceptionRecord.objects.create(
        text = f'CREATE TENANT TIME DIFF . {total_seconds} Seconds'
    )
            