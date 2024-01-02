# error_logging_middleware.py

from Utility.models import ExceptionRecord
import logging
from Tenants.models import Tenant
from django_tenants.utils import tenant_context
from django.db import connection
class ServerErrorLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if 500 <= response.status_code < 600:
            # Log the server error
            try:
                response_text = response.data
            except AttributeError:
                response_text = response.content

            logger = logging.getLogger('django')
            # logger.error(
            #     f"Server Error: {response.status_code} - {request.method} {request.path}\n"
            #     f"Response Content: {response.content}\n"
            # )

            tenant = connection.get_tenant()
            tenant_id = None
            if tenant and hasattr(tenant, 'id'):
                tenant_id = str(tenant.id)

            try:
                pub_tenant = Tenant.objects.get(schema_name = 'public')
            except:
                ExceptionRecord.objects.create(text=str(response.content), status_code=str(response.status_code), method=str(request.method), path=str(request.path))
            else:
                with tenant_context(pub_tenant):
                    err_instance = ExceptionRecord.objects.create(text=str(response.content), status_code=str(response.status_code), method=str(request.method), path=str(request.path))
                    if tenant_id:
                        try:
                            user_tenant = Tenant.objects.get(id = tenant_id)
                        except:
                            pass
                        else:
                            err_instance.tenant = user_tenant
                            err_instance.save()

        return response
