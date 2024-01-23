import json
from Authentication.Constants.Domain import ssl_sub_domain, create_aws_domain_record
from Client.models import Client
from Employee.Constants.Add_Employe import add_employee
from Employee.models import EmployeDailySchedule, Employee, EmployeeProfessionalInfo, EmployeeSelectedService
from Permissions.models import EmployePermission
from Tenants.models import Tenant, Domain
from Business.models import (Business, BusinessAddress, BusinessOpeningHour,
                             ClientNotificationSetting, AdminNotificationSetting,
                             StockNotificationSetting, StaffNotificationSetting,
                             BusinessPaymentMethod, BusinessType)
from Profile.models import Profile
from Utility.Constants.Data.PermissionsValues import ALL_PERMISSIONS, PERMISSIONS_MODEL_FIELDS
from Utility.Constants.get_from_public_schema import get_country_from_public, get_state_from_public
from Utility.Constants.add_data_db import add_business_types, add_countries, add_software_types, add_states, add_cities, add_currencies, add_languages
from Utility.models import Country, Currency, ExceptionRecord, Language
from Utility.models import GlobalPermissionChoices
from MultiLanguage.models import InvoiceTranslation

from rest_framework.authtoken.models import Token
from django.conf import  settings

from django_tenants.utils import tenant_context
from Authentication.models import AccountType, User, NewsLetterDetail
from Authentication.Constants import AuthTokenConstants
from threading import Thread
from Service.models import PriceService, Service, ServiceGroup
from datetime import date, timedelta

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
            text=f'SWITCH TENANT TIME DIFF . {total_seconds} Seconds'
        )

        user_profile = Profile.objects.create(
            user=tenant_user,
            is_active=True
        )
        return user_profile


def create_tenant_business(tenant_user=None, tenant_profile=None, tenant=None, data=None):
    if tenant_user is None or tenant is None or tenant_profile is None:
        return None

    with tenant_context(tenant):
        user_business = Business.objects.create(
            user=tenant_user,
            profile=tenant_profile,
            business_name=data.get('business_name', tenant_user.username)
        )
        return user_business


def create_tenant_user_token(tenant_user=None, tenant=None):
    print(tenant_user, tenant)
    if tenant_user is None or tenant is None:
        return None

    with tenant_context(tenant):
        user_token = Token(
            user=tenant_user,
        )
        user_token.save()
        return user_token


def create_tenant_account_type(tenant_user=None, tenant=None, account_type='Business'):
    if tenant_user is None or tenant is None:
        return None

    with tenant_context(tenant):
        return AccountType.objects.create(
            user=tenant_user,
            account_type='Business'  # account_type
        )


def create_employee(tenant=None, user=None, business=None, data=None):
    if tenant is not None and user is not None and business is not None and data is not None:
        country_unique_id = data.get('country')
        public_country = get_country_from_public(country_unique_id)
        try:
            with tenant_context(tenant):
                currency_id = 'Dirham'
                domain = tenant.domain
                template = 'Employee'

                tenant_name = str(tenant.domain).split('.')[0]
                tenant_name = tenant_name.split('-')
                tenant_name = [word[0].upper() for word in tenant_name if
                               word]  # Use upper() to capitalize letters and add a check to skip empty strings
                employe_id = f'{" ".join(tenant_name)}-EMP-0001'

                opening_day = {
                    "monday": {"start_time": "09:00:00", "end_time": "18:00:00"},
                    "tuesday": {"start_time": "09:00:00", "end_time": "18:00:00"},
                    "wednesday": {"start_time": "09:00:00", "end_time": "18:00:00"},
                    "thursday": {"start_time": "09:00:00", "end_time": "18:00:00"},
                    "friday": {"start_time": "09:00:00", "end_time": "18:00:00"},
                }
                days = [
                    'monday',
                    'tuesday',
                    'wednesday',
                    'thursday',
                    'friday',
                    'saturday',
                    'sunday',
                ]
                try:
                    country, created = Country.objects.get_or_create(
                        name=public_country.name,
                        unique_id=public_country.unique_id
                    )
                    currency = Currency.objects.get(name__iexact=currency_id)
                    language = Language.objects.get(name__icontains='English')

                except Exception as err:
                    country = None

                if language:
                    invoice_translation = InvoiceTranslation.objects.create(
                        language=language,
                        user=user,
                        invoice='Invoice',
                        items='Items',
                        amount='Amount',
                        subtotal='Subtotal',
                        tips='Tips',
                        taxes='Taxes',
                        total='Total',
                        payment_method='Payment Method',
                        status='active'
                    )

                business_address = BusinessAddress.objects.create(
                    business=business,
                    user=user,
                    address='',
                    address_name='',
                    email=user.email,
                    mobile_number=user.mobile_number,
                    country=country,
                    is_primary=False,
                    is_active=True,
                    is_deleted=False,
                    is_closed=False,
                    is_default=True
                )

                if invoice_translation:
                    business_address.primary_translation = invoice_translation
                    business_address.save()

                employee = Employee.objects.create(
                    user=user,
                    business=business,
                    full_name=user.full_name,
                    email=user.email,
                    country=country,
                    address='',
                    is_active=True,
                    employee_id=employe_id,
                    is_default=True

                )
                employee.location.add(business_address)
                employee.save()

                EmployeeProfessionalInfo.objects.create(
                    employee=employee,
                    salary=20,
                    income_type='Hourly_Rate',
                    designation='Store Manager',
                    monday=True,
                    tuesday=True,
                    wednesday=True,
                    thursday=True,
                    friday=True,
                )

                for day in days:
                    bds_schedule = BusinessOpeningHour.objects.create(
                        business_address=business_address,
                        business=business,
                        day=day,
                    )
                    s_day = opening_day.get(day.lower(), None)
                    if s_day is not None:

                        bds_schedule.start_time = s_day['start_time']
                        bds_schedule.close_time = s_day['end_time']

                    else:
                        bds_schedule.is_closed = True

                    bds_schedule.save()

                try:
                    username = user.email.split('@')[0]
                    try:
                        user_check = User.objects.get(username=username)
                    except Exception as err:
                        # data.append(f'username user is client errors {str(err)}')'
                        email_check = f'{username}-abc'
                        pass
                    else:
                        username = f'{username} {len(User.objects.all())}'
                        email_check = f'{username} {len(User.objects.all())}'

                except Exception as err:
                    pass
                auto_generate_email = f'{email_check}@gmail.com'

                user = User.objects.create(
                    first_name=user.full_name,
                    username=username,
                    email=auto_generate_email,
                    is_email_verified=True,
                    is_active=True,
                    mobile_number=user.mobile_number,
                )

                account_type = AccountType.objects.create(
                    user=user,
                    account_type='Employee'
                )

                try:
                    thrd = Thread(target=add_employee, args=['ABCD', auto_generate_email, user.mobile_number, template,
                                                             business.business_name, tenant.id, domain, user])
                    thrd.start()
                except Exception as err:
                    pass
        except Exception as err:
            ExceptionRecord.objects.create(
                text=f'errors in some create employee {str(err)}'
            )


def create_client(tenant=None, user=None, business=None):
    if tenant is not None and user is not None and business is not None:
        with tenant_context(tenant):
            tenant_name = str(tenant.domain).split('.')[0]
            tenant_name = tenant_name.split('-')
            tenant_name = [word[0].upper() for word in tenant_name if
                           word]  # Use upper() to capitalize letters and add a check to skip empty strings
            client_unique_id = f'{" ".join(tenant_name)}-CLI-0001'

            try:
                languages = 'English'
                language_id = Language.objects.get(name__icontains='English')
            except Exception as err:
                ExceptionRecord.objects.create(
                    text=f'create client languages not found {str(err)}'
                )
            Client.objects.create(
                business=business,
                user=user,
                full_name=user.first_name,  # 'ABCD',
                gender='Male',
                language=language_id,
                client_id=client_unique_id,
                is_active=True,
                is_default=True,
            )


def create_ServiceGroup(tenant=None, user=None, business=None):
    if tenant is not None and user is not None and business is not None:
        try:
            with tenant_context(tenant):
                try:
                    # currency_id = 'Dirham'
                    location = BusinessAddress.objects.all()[0]
                    emp = Employee.objects.all()[0]
                    # currency = Currency.objects.get(name__iexact = currency_id)
                except:
                    pass
                service_grp = ServiceGroup.objects.create(
                    business=business,
                    user=user,
                    name='Hair Care',
                    is_active=True
                )
                # while verifying OTP, it created 2 services each time.
                # we are counting if services are 0 then create 2 services
                services_count = Service.objects.all().count()
                if services_count == 0:
                    for ser in range(2):
                        if int(ser) == 0:
                            ser_name = 'Hair color'
                        else:
                            ser_name = 'Hair cut'
                        service = Service.objects.create(
                            user=user,
                            business=business,
                            name=ser_name,
                            description=f'{ser_name} description',
                            service_availible='Everyone',
                            is_default=True,
                        )
                        service.location.add(location)
                        service.save()
                        service_grp.services.add(service)
                        service_grp.save()

                        employe_service = EmployeeSelectedService.objects.create(
                            service=service,
                            employee=emp
                        )
                        price_service = PriceService.objects.create(
                            service=service,
                            # currency = currency,
                            duration='30Min',
                            price=500,
                        )
                else:
                    pass
        except Exception as err:
            ExceptionRecord.objects.create(
                text=f'Service creating error occur {str(err)} {location}'
            )


def create_emp_schedule(tenant=None, user=None, business=None):
    if tenant is not None and user is not None and business is not None:
        try:
            start_time = datetime.time(9, 0, 0)
            end_time = datetime.time(18, 0, 0)
            today = date.today()

            with tenant_context(tenant):
                emp = Employee.objects.all()[0]
                for dt in range(30):
                    next_date = today + timedelta(days=dt)
                    EmployeDailySchedule.objects.create(
                        user=user,
                        business=business,
                        employee=emp,

                        start_time=start_time,
                        end_time=end_time,

                        from_date=next_date,
                        to_date=next_date,
                        note="ABCD note",

                        date=next_date,
                        is_vacation=False,
                        is_leave=False,
                        is_off=False,
                        is_active=True
                    )

        except Exception as err:
            ExceptionRecord.objects.create(
                text=f'Service creating error occur {str(err)}'
            )


def create_global_permission(tenant=None, user=None, business=None):
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
                    text=per,
                    slug=per,
                )


def default_payment_method(tenant=None, user=None, business=None):
    if tenant is not None and user is not None and business is not None:
        with tenant_context(tenant):
            payment_method = [

                "Cash",
                "Mastercard",
                "Visa",
                'Paypal',
                'GooglePay',
                'ApplePay',
            ]
            for pay in payment_method:
                BusinessPaymentMethod.objects.create(
                    user=user,
                    business=business,
                    method_type=pay,

                )


def create_busines_notification_settings(tenant=None, business=None):
    if tenant is None:
        return

    with tenant_context(tenant):
        StaffNotificationSetting.objects.create(business=business, user=business.user, is_active=True)
        ClientNotificationSetting.objects.create(business=business, user=business.user, is_active=True)
        AdminNotificationSetting.objects.create(business=business, user=business.user, is_active=True)
        StockNotificationSetting.objects.create(business=business, user=business.user, is_active=True)


def add_data_to_tenant_thread(tenant=None):
    if tenant is None:
        return

    time_start = datetime.datetime.now()

    try:
        print('gonna create DB data')
        add_currencies(tenant=tenant)
        add_languages(tenant=tenant)

    except Exception as err:
        print(err)
    else:

        time_end = datetime.datetime.now()
        time_diff = time_end - time_start

        total_seconds = time_diff.total_seconds()

        ExceptionRecord.objects.create(
            text=f'ADD DATA TO TENANT DB TIME DIFF . {total_seconds} Seconds'
        )


def create_tenant(request=None, user=None, data=None):
    if user is None or data is None:
        return

    td_name = str(data.get('business_name', user.username)).strip().replace('&', '').replace('  ', '-').replace(' ',
                                                                                                                '-').replace(
        '.', '').replace('/', '-').lower()  # Tenant Domain name
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
            user__isnull=True,
            is_active=False,
            is_ready=True
        )
        if len(all_tenants) > 0:
            user_tenant = all_tenants[0]

            user_tenant.user = user
            user_tenant.domain = user_domain_name
            user_tenant.is_active = True
            user_tenant.save()
        else:
            user_tenant = Tenant.objects.create(
                user=user,
                name=td_name,
                domain=user_domain_name,
                schema_name=td_name
            )

        Domain.objects.create(
            user=user,
            schema_name=td_name,
            domain=f'{td_name}.{settings.BACKEND_DOMAIN_NAME}',
            tenant=user_tenant,
        )
    except Exception as err:
        ExceptionRecord.objects.create(
            text=f'Check domain errors . {str(err)} {user_tenant} line 400 create_tenant'
        )

    with tenant_context(user_tenant):
        if not settings.USE_WILDCARD_FOR_SSL:
            try:
                thrd = Thread(target=ssl_sub_domain, args=[td_name])
                thrd.start()
            except Exception as err:
                ExceptionRecord.objects.create(
                    text=f'SSL ERROR . {str(err)}'
                )
        else:
            ExceptionRecord.objects.create(text=f'Using Wildcard for SSL {td_name}')
            try:
                thrd = Thread(target=create_aws_domain_record, args=[f'{td_name}.{settings.BACKEND_DOMAIN_NAME}'])
                thrd.start()
            except Exception as err:
                ExceptionRecord.objects.create(text=f'AWS HOSTED ERROR . {str(err)}')

        t_user = create_tenant_user(tenant=user_tenant, data=data)

        if t_user is not None:

            t_profile = create_tenant_profile(tenant_user=t_user, data=data, tenant=user_tenant)
            t_business = create_tenant_business(tenant_user=t_user, tenant_profile=t_profile, tenant=user_tenant,
                                                data=data)
            try:
                ubs_type = BusinessType.objects.get(slug=data['business_industry'])  # User Business Type
                t_business.business_types.add(ubs_type)
                t_business.save()
            except:
                pass

            try:
                t_token = create_tenant_user_token(tenant_user=t_user, tenant=user_tenant)
            except:
                pass

            try:
                create_employee(tenant=user_tenant, user=t_user, business=t_business, data=data)
            except:
                ExceptionRecord.objects.create(
                    text=f'{str(err)}'
                )

            try:
                create_tenant_account_type(tenant_user=t_user, tenant=user_tenant,
                                           account_type='Business')  # data['account_type'])
            except:
                pass

            try:
                service_thrd = Thread(target=create_global_permission,
                                      kwargs={'tenant': user_tenant, 'user': t_user, 'business': t_business})
                service_thrd.start()
            except:
                pass

            try:
                payment_thrd = Thread(target=default_payment_method,
                                      kwargs={'tenant': user_tenant, 'user': t_user, 'business': t_business})
                payment_thrd.start()
            except:
                pass

            """
                            Comment Reason : 
                            Now we don't want to create client on tenant creation
                            (Discussed in meeting - 22 Sep, 2023)
            """
            # try:
            #     service_thrd = Thread(target=create_client, kwargs={'tenant' :user_tenant , 'user' : t_user, 'business': t_business})
            #     service_thrd.start()
            # except:
            #     pass

            try:
                service_thrd = Thread(target=create_ServiceGroup,
                                      kwargs={'tenant': user_tenant, 'user': t_user, 'business': t_business})
                service_thrd.start()
            except:
                pass
            try:
                service_thrd = Thread(target=create_emp_schedule,
                                      kwargs={'tenant': user_tenant, 'user': t_user, 'business': t_business})
                service_thrd.start()
            except Exception as err:
                pass

            try:
                notification_thread = Thread(target=create_busines_notification_settings,
                                             kwargs={'tenant': user_tenant, 'business': t_business})
                notification_thread.start()
            except Exception as err:
                pass
