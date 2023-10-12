from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# class CustomPagination(PageNumberPagination):
#     def get_paginated_response(self, data, details=None, playlist=None):
#         return Response({
#             'links': {
#                'next': self.get_next_link(),
#                'previous': self.get_previous_link()
#             },
#             'count': self.page.paginator.count,
#             'per_page_result': self.page_size,
#             'results': data,
#             'details': details,
#             'playlist': playlist,
#         })

class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data, pramas_data, extra=None):
        base_url = self.request.build_absolute_uri().split('?')[0] + '?'
        count = self.page.paginator.count
        per_page_result = self.page_size
        invoice_translations = extra if extra else None
        return Response({
            'links': {
               'next': base_url + self.get_next_link().split('?')[-1] if self.get_next_link() else None,
               'previous': base_url + self.get_previous_link().split('?')[-1] if self.get_previous_link() else None
            },
            'count': count,
            'pages' : count / per_page_result,
            'per_page_result': per_page_result ,
            'response' : {
                'message' : f'All {pramas_data}',
                'error_message' : None,
                pramas_data : data,
                'invoice_translations': invoice_translations
            }

        })



class NewsFeedPagination(PageNumberPagination):
    def get_paginated_response(self, data, details=None, playlist=None):
        # Code to get 10 results on first page.
        if self.get_previous_link():
            per_page_results = self.page_size
        else:
            per_page_results = 10
        return Response({
            'links': {
               'next': self.get_next_link(),
               'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'per_page_result': per_page_results,
            'results': data,
            'details': details,
            'playlist': playlist,
            })
    
