
from Authentication.Constants import CreateTenant, AuthTokenConstants, OTP
from Authentication.models import AccountType, NewsLetterDetail, User

from threading import Thread

from Utility.models import ExceptionRecord

def create_user_account_type(user=None, account_type=None):
    if ( user is not None and account_type is not None ) and (account_type == 'everyone' or account_type == 'business'):
        try:
            user_account_type = AccountType.objects.get(user=user, account_type=account_type)
            print('Account Type already exist')
            return user_account_type
        except:
            if account_type not in ['Everyone', 'Business', 'Employee']:
                account_type = 'Business'
            user_account_type = AccountType.objects.create(
                user=user,
                account_type=account_type
            )
            return user_account_type
    else:
        ExceptionRecord.objects.create(text='Could not create user type in create_user_account_type')

        return None


def complete_user_account(request, user=None, data=None):

    if user is None:
        return
    
    account_type = data.get('account_type', None)
    if account_type is not None and account_type == 'business':
        try:
            create_tenant_thread = Thread(target=CreateTenant.create_tenant, args=[], kwargs={'user' : user, 'data' : data})
            create_tenant_thread.start()
        except Exception as error:
            ExceptionRecord.objects.create(text=f'error from create_tenant_thread \n{str(error)}')


    first_name = data['first_name']
    last_name = data['last_name']
    mobile_number = data['mobile_number']
    social_account = data.get('social_account', None)
    address = data.get('address', None)
    city = data.get('city', None)
    country = data.get('country', None)
    zip_code = data.get('zip_code', None)


    user.first_name = first_name
    user.last_name = last_name
    
    user.full_name=f'{first_name} {last_name}'
    user.mobile_number=mobile_number

    user.address = address
    user.city = city
    user.country = country
    user.zip_code = zip_code
    
    if social_account is not None:
        user.is_email_verified = True
        user.is_active = True
        social_platform = data.get('social_platform', None)
        social_id = data.get('social_id', None)
        user.social_account = True
        if social_platform is not None:
            user.social_platform = social_platform
        if social_id is not None:
            user.social_id = social_id


    user.save()
    
    if not social_account:
        try:
            OTP.generate_user_otp(user=user, code_for='Email')
        except Exception as error:
            ExceptionRecord.objects.create(text=f'error from create_tenant_thread \n{str(error)}')

   
    # NewsLetterDetail.objects.create(
    #     user = user,
    #     terms_condition=data.get('terms_condition', True),
    #     is_subscribed=data.get('terms_condition', False)
    # )

    if not account_type:
        account_type = 'Business'
    create_user_account_type(user=user, account_type=account_type)
    AuthTokenConstants.create_user_token(user=user)
