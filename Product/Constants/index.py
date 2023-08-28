

from django.conf import settings

def tenant_media_base_url(request, is_s3_url=False):
    if is_s3_url:
        return f'{settings.CLOUD_FRONT_S3_BUCKET_URL}/media/{request.tenant_schema_name}/'
    else:
        return f'{settings.BACKEND_HOST}/media/{request.tenant_schema_name}/'

def tenant_media_domain(request):
    return f'{settings.BACKEND_HOST}/media/{request}/'
