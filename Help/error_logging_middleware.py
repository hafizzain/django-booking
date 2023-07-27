from Utility.models import ExceptionRecord
import logging

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
            ExceptionRecord.objects.create(text=str(response.content), status_code=str(response.status_code), method=str(request.method), path=str(request.path))

        return response
