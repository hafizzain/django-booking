"""
Django settings for NStyle project.

Generated by 'django-admin startproject' using Django 4.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import environ
import os
import json

from firebase_admin import initialize_app, credentials

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')
CSRF_TRUSTED_ORIGINS=[
    # 'https://*.YOUR_DOMAIN.COM',
    'https://hashedsystems.com',
    'https://hashedsystem.co.uk',
    'https://*.hashedsystem.co.uk',
                      ]
ALLOWED_HOSTS = ['*']
INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    "localhost",
    # ...
]

# Application definition

DJANGO_APPS = [

]

NSTYLE_APPS = [
    'Api.apps.ApiConfig',
    'Authentication.apps.AuthenticationConfig',
    'Profile.apps.ProfileConfig',
    'Utility.apps.UtilityConfig',
    'Business.apps.BusinessConfig',
    'Product.apps.ProductConfig',
    'Employee.apps.EmployeeConfig',
    'Service.apps.ServiceConfig',
    'Client.apps.ClientConfig',
    'Appointment.apps.AppointmentConfig',
    'Sale.apps.SaleConfig',
    'Permissions.apps.PermissionsConfig',
    'Order.apps.OrderConfig',
    'Dashboard.apps.DashboardConfig',
    'CRM.apps.CrmConfig',
    'TragetControl.apps.TragetcontrolConfig',
    'Customer.apps.CustomerConfig',
    'Promotions.apps.PromotionsConfig',
    'Reports.apps.ReportsConfig',
    'Invoices.apps.InvoicesConfig',
    'Help.apps.HelpConfig',
    'MultiLanguage.apps.MultilanguageConfig',
    'SuperInsight.apps.SuperinsightConfig',
    'Notification.apps.NotificationConfig',
    'Analytics.apps.AnalyticsConfig',
    'Finance.apps.FinanceConfig',
    'HRM.apps.HrmConfig',
    'SaleRecords.apps.SalerecordsConfig', #Added the New Checkout
    'Deal.apps.DealConfig',
]


SHARED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_tenants',
    'rest_framework',
    'rest_framework.authtoken',
    "corsheaders",
    'geoip2',
    'django_crontab',
    'django_extensions',
    'debug_toolbar',
    'fcm_django',
    'django_filters',
    # 'django.db.migrations',
    

    'Tenants.apps.TenantsConfig',
] +  NSTYLE_APPS

TENANT_APPS = [
    # The following Django contrib apps must be in TENANT_APPS
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework.authtoken',

] + NSTYLE_APPS

INSTALLED_APPS = ['jazzmin']  + list(set(SHARED_APPS + TENANT_APPS))


MIDDLEWARE = [
    'NStyle.Middlewares.TenantMiddleware.CustomTanantMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    # 'Api.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Appointment.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Authentication.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Business.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Client.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'CRM.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Customer.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Dashboard.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Employee.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Invoices.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Notification.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Order.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Permissions.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Product.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Profile.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Promotions.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Reports.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Sale.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Service.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'SuperInsight.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Tenants.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Utility.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'MultiLanguage.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Help.error_logging_middleware.ServerErrorLoggingMiddleware',
    # 'Analytics.error_logging_middleware.ServerErrorLoggingMiddleware'
    
]

BACKEND_DOMAIN_NAME=env('BACKEND_DOMAIN_NAME')
BACKEND_HOST=env('BACKEND_HOST')
CLOUD_FRONT_S3_BUCKET_URL=env('CLOUD_FRONT_S3_BUCKET_URL')

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    'http://midtechdxb.com',
    'https://midtechdxb.com',
    'http://us-telecoms.com',
    'https://us-telecoms.com',
    BACKEND_HOST,
]

CORS_ALLOW_ALL_ORIGINS = True
ROOT_URLCONF = 'NStyle.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'NStyle.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'OPTIONS': {
            'options': '-c search_path=public'
        },
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT'),
        'CONN_MAX_AGE': None,
        # 'ATOMIC_REQUESTS': True,  # Enable global transactions
    }
}

AUTH_USER_MODEL = 'Authentication.User'
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


DEFAULT_RENDERER_CLASSES = [
    'Utility.customizations.renderers.CustomRenderer',
]

if DEBUG:
    DEFAULT_RENDERER_CLASSES = DEFAULT_RENDERER_CLASSES + [
    'rest_framework.renderers.BrowsableAPIRenderer',
]


REST_FRAMEWORK = {

    'DEFAULT_RENDERER_CLASSES': DEFAULT_RENDERER_CLASSES,

    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],

    'DEFAULT_AUTHENTICATION_CLASSES' : [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    ],

    'DEFAULT_PERMISSION_CLASSES' : [
        'rest_framework.permissions.IsAuthenticated'
    ],

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # Set your desired page size here

}

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/


CRONJOBS = [
    ('* * * * *', 'Apponitment.Constants.today_appointment.today_appointment'),
    ('* * * * *', 'Product.Constants.Product_automation.ReorderQunatity'),
    ('0 0 * * *', 'Tenants.Constants.tenant_constants.createFreeAvailableTenants'),
    # ('15 * * * *', 'Tenants.Constants.tenant_constants.createFreeAvailableTenants'),
]


STATIC_URL = '/static/'

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
# ]



# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


DEFAULT_FILE_STORAGE = 'django_tenants.files.storages.TenantFileSystemStorage'
DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)
TENANT_MODEL = "Tenants.Tenant"
TENANT_DOMAIN_MODEL = "Tenants.Domain"

# TWILLIO_SETTINGS  

TWILLIO_ACCOUNT_SID = env('TWILLIO_ACCOUNT_SID')
TWILLIO_AUTH_TOKEN  = env('TWILLIO_AUTH_TOKEN')
TWILLIO_PHONE_NUMBER = env('TWILLIO_PHONE_NUMBER')


# EMAIL SETTINGS VARIABLES 

EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

GEOIP_PATH =os.path.join('geoip')


# FCM_DJANGO CONFIGURATION
fcm_credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
try:
    with open(fcm_credentials, 'r') as cred:
        json_data = json.loads(cred.read())

    cred = credentials.Certificate(json_data)
    FIREBASE_APP = initialize_app(cred)
    FCM_DJANGO_SETTINGS = {
        "DEFAULT_FIREBASE_APP": FIREBASE_APP,
        "APP_VERBOSE_NAME": "FCM Devices",
        "ONE_DEVICE_PER_USER": True,
        "DELETE_INACTIVE_DEVICES": False,
    }
except:
    pass


AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_SIGNATURE_VERSION = 's3v4'
# AWS_S3_REGION_NAME = 'ap-southeast-1'
# AWS_S3_FILE_OVERWRITE = env('AWS_S3_FILE_OVERWRITE')
AWS_S3_FILE_OVERWRITE = False
# AWS_DEFAULT_ACL = env('AWS_DEFAULT_ACL')
AWS_DEFAULT_ACL = None
# AWS_S3_VERIFY = env('AWS_S3_VERIFY')
AWS_S3_VERIFY = True
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

CLOUD_FRONT_S3_BUCKET_URL = env('CLOUD_FRONT_S3_BUCKET_URL')

try:
    USE_WILDCARD_FOR_SSL = env('USE_WILDCARD_FOR_SSL')
    USE_WILDCARD_FOR_SSL = True
except:
    USE_WILDCARD_FOR_SSL = False

try:
    AWS_API_KEY = env('AWS_API_KEY')
    AWS_SECRET_KEY = env('AWS_SECRET_KEY')
    AWS_MY_ZONE_ID = env('AWS_MY_ZONE_ID')
    AWS_REGION_ZONE_ID = env('AWS_REGION_ZONE_ID')
    AWS_DNS_NAME = env('AWS_DNS_NAME')
except Exception as err:
    print(err)
    AWS_API_KEY = None
    AWS_SECRET_KEY = None
    AWS_MY_ZONE_ID = None
    AWS_REGION_ZONE_ID = None
    AWS_DNS_NAME = None


# Frontend Domain
FRONTEND_DOMAIN = env('FRONTEND_DOMAIN')


# Set Atomic Requests Globally
# ATOMIC_REQUESTS = True
try:
    from .local_settings import LIVE_SERVER_PATH
except:
    LIVE_SERVER_PATH = '/home/ubuntu/backend-nstyle/'
