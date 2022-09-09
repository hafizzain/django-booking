
from Authentication.Constants import CreateTenant, AuthTokenConstants, OTP
from Authentication.models import AccountType, NewsLetterDetail, User

def create_user_account_type(user=None, account_type=None):
    if ( user is not None and account_type is not None ) and (account_type == 'everyone' or account_type == 'business'):
        try:
            user_account_type = AccountType.objects.get(user=user, account_type=account_type)
            print('Account Type already exist')
            return user_account_type
        except:
            user_account_type = AccountType.objects.create(
                user=user,
                account_type=account_type
            )
            return user_account_type
    else:
        print('Could not create User Account type')
        return None


def complete_user_account(request, user=None, data=None):

    if user is None:
        return

    first_name = data['first_name']
    last_name = data['last_name']
    mobile_number = data['mobile_number']
    social_account = data.get('social_account', False)

    user.first_name = first_name
    user.last_name = last_name
    username = f'{first_name}{last_name}'.trim()
    try:
        User.objects.get(username = username)
    except:
        username +=  len(User.objects.all())

    user.username = username
    user.full_name=f'{first_name} {last_name}'
    user.mobile_number=mobile_number

    if social_account and social_account is not None:
        social_platform = data.get('social_platform', None)
        social_id = data.get('social_id', None)
        user.social_account = True
        if social_platform is not None:
            user.social_platform = social_platform
        if social_id is not None:
            user.social_id = social_id

    user.save()
    NewsLetterDetail.objects.create(
        user = user,
        terms_condition=data.get('terms_condition', True),
        is_subscribed=data.get('terms_condition', False)
    )
    create_user_account_type(user=user, account_type=data['account_type'])
    AuthTokenConstants.create_user_token(user=user)
    OTP.generate_user_otp(user=user, code_for='Email')

    CreateTenant.create_tenant(user=user, data=data)