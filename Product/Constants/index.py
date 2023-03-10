

from django.conf import settings

def tenant_media_base_url(request):

    return f'{settings.BACKEND_HOST}/media/{request.tenant_schema_name}/'

def tenant_media_domain(request):
    return f'{settings.BACKEND_HOST}/media/{request}/'
