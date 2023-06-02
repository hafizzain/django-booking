
from Product.models import Product

from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.views import APIView

from django.db.models import Count
from Product.serializers import ProductInsightSerializer
import re

from datetime import datetime

DATE_REGEX = '\d{4}-\d{2}-\d{2}'

class FilteredInsightProducts(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        top_sold = request.GET.get('top_sold', None)
        TOP_SOLD_CHOICES = {'TOP_SOLD_PRODUCTS' : lambda : None, 'LAST_7_DAYS' : lambda : datetime.date().strftime('%Y-%') , 'LAST_30_DAYS' : '' }

        most_consumed = request.GET.get('most_consumed', None)
        MOST_COMSUMED_CHOICES = ['MOST_COMSUMED_PRODUCTS', 'LAST_7_DAYS', 'LAST_30_DAYS']

        most_ordered = request.GET.get('most_ordered', None)
        MOST_ORDERED_CHOICES = ['MOST_ORDERED_PRODUCTS', 'LAST_7_DAYS', 'LAST_30_DAYS']

        most_transferred = request.GET.get('most_transferred', None)
        MOST_TRANSFERRED_CHOICES = ['MOST_TRANSFERRED_PRODUCTS', 'LAST_7_DAYS', 'LAST_30_DAYS']

        low_stock_products = request.GET.get('low_stock_products', None)
        out_of_stock_products = request.GET.get('out_of_stock_products', None)


        queries = {
            'filter' : {},'order_by' : [], 'annotate' : {}
        }

        if top_sold :
            queries['order_by'].append('-top_sold_orders')
            queries['annotate']['top_sold_orders'] = Count('product_orders__quantity')
            if top_sold in TOP_SOLD_CHOICES or re.match(DATE_REGEX, top_sold):
                pass
            else:
                return Response(
                    {
                        'status' : False,
                        'status_code' : 400,
                        'response' : {
                            'message' : 'Invalid Top Sold Query',
                            'error_message' : None,
                        }
                    },
                    status=status.HTTP_200_OK
                )

        filtered_products = Product.objects.filter(
            is_deleted = False,
            **queries['filter'],
        ).annotate(
            **queries['annotate'],
        ).distinct().order_by(*queries['order_by'])

        # serialized = ProductInsightSerializer(filtered_products, many=True)

        data = []

        for product_instance in filtered_products:
            product = {
                # 'id' : f'{product_instance.id}',
                'name' : f'{product_instance.name}',
            }

            if product_instance.top_sold_orders:
                product['top_sold_orders'] = f'{product_instance.top_sold_orders}'

            data.append(product)

        return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : 'Insight Products',
                    'error_message' : None,
                    'products' : data
                }
            },
            status=status.HTTP_200_OK
        )