from django.conf import settings
from django.db import connection
from django.http import Http404
from django.urls import set_urlconf
from django.utils.deprecation import MiddlewareMixin

from django_tenants.utils import remove_www, get_public_schema_name, get_tenant_types, \
    has_multi_type_tenants, get_tenant_domain_model, get_public_schema_urlconf


class CustomTanantMiddleware(MiddlewareMixin):
    TENANT_NOT_FOUND_EXCEPTION = Http404

    @staticmethod
    def hostname_from_request(request):
        return remove_www(request.get_host().split(':')[0])

    def get_tenant(self, domain_model, hostname):
        # domain = domain_model.objects.select_related('tenant').get(domain=hostname)
        domain = domain_model.objects.get(
            domain=hostname,
            is_deleted=False,
            is_active=True,
            is_blocked=False
        )
        try:
            self.domain_name = domain.domain.split('.')[0]
        except:
            self.domain_name = ''
        return domain.tenant

    def process_request(self, request):
        connection.set_schema_to_public()
        hostname = self.hostname_from_request(request)

        domain_model = get_tenant_domain_model()
        try:
            tenant = self.get_tenant(domain_model, hostname)
        except domain_model.DoesNotExist:
            self.no_tenant_found(request, hostname)
            return

        tenant.domain_url = hostname
        request.tenant = tenant
        try:
            request.tenant_name = self.domain_name
            request.tenant_schema_name = tenant.schema_name
        except:
            request.tenant_name = ''
            request.tenant_schema_name = ''

        connection.set_tenant(request.tenant)
        self.setup_url_routing(request)

    def no_tenant_found(self, request, hostname):
        if hasattr(settings, 'SHOW_PUBLIC_IF_NO_TENANT_FOUND') and settings.SHOW_PUBLIC_IF_NO_TENANT_FOUND:
            self.setup_url_routing(request=request, force_public=True)
        else:
            raise self.TENANT_NOT_FOUND_EXCEPTION('No tenant for hostname "%s"' % hostname)

    @staticmethod
    def setup_url_routing(request, force_public=False):
        public_schema_name = get_public_schema_name()
        if has_multi_type_tenants():
            tenant_types = get_tenant_types()
            if (not hasattr(request, 'tenant') or
                    ((force_public or request.tenant.schema_name == get_public_schema_name()) and
                     'URLCONF' in tenant_types[public_schema_name])):
                request.urlconf = get_public_schema_urlconf()
            else:
                tenant_type = request.tenant.get_tenant_type()
                request.urlconf = tenant_types[tenant_type]['URLCONF']
            set_urlconf(request.urlconf)

        else:
            if (hasattr(settings, 'PUBLIC_SCHEMA_URLCONF') and
                    (force_public or request.tenant.schema_name == get_public_schema_name())):
                request.urlconf = settings.PUBLIC_SCHEMA_URLCONF
