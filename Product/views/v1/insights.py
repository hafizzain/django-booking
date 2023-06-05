
from Product.models import Product

from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.views import APIView

from django.db.models import Count
from Product.serializers import ProductInsightSerializer
import re

from datetime import datetime, timedelta

DATE_REGEX = '\d{4}-\d{2}-\d{2}'

class FilteredInsightProducts(APIView):
    permission_classes = [AllowAny]

    today_date = datetime.now()
    today_date_format = today_date.strftime('%Y-%m-%d')
    days_before_7 = (today_date - timedelta(days=7)).strftime('%Y-%m-%d')
    days_before_30 = (today_date - timedelta(days=30)).strftime('%Y-%m-%d')

    queries = {
        'filter' : {},'order_by' : [], 'annotate' : {}
    }

    def retreive_top_sold_query(self, request):
        top_sold = request.GET.get('top_sold', None)
        TOP_SOLD_CHOICES = {'TOP_SOLD_PRODUCTS' : lambda : None, 'LAST_7_DAYS' : self.days_before_30 , 'LAST_30_DAYS' : self.days_before_30 }

        if top_sold :
            self.queries['order_by'].append('-top_sold_orders')
            self.queries['annotate']['top_sold_orders'] = Count('product_orders__quantity')
            if top_sold in TOP_SOLD_CHOICES or re.match(DATE_REGEX, top_sold):
                if top_sold != 'TOP_SOLD_PRODUCTS':
                    value = top_sold
                    if value in ['LAST_7_DAYS', 'LAST_30_DAYS']:
                        value = TOP_SOLD_CHOICES.get(value)
                    self.queries['filter']['product_orders__created_at__range'] = (value, self.today_date_format)
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
            
    def retreive_most_consumed_query(self, request):
        most_consumed = request.GET.get('most_consumed', None)
        MOST_COMSUMED_CHOICES = {'MOST_COMSUMED_PRODUCTS' : lambda : None, 'LAST_7_DAYS' : self.days_before_30 , 'LAST_30_DAYS' : self.days_before_30 }

        if most_consumed :
            self.queries['order_by'].append('-most_consumed_products')
            self.queries['annotate']['most_consumed_products'] = Count('consumptions__quantity')
            if most_consumed in MOST_COMSUMED_CHOICES or re.match(DATE_REGEX, most_consumed):
                if most_consumed != 'MOST_COMSUMED_PRODUCTS':
                    value = most_consumed
                    if value in ['LAST_7_DAYS', 'LAST_30_DAYS']:
                        value = MOST_COMSUMED_CHOICES.get(value)
                    self.queries['filter']['consumptions__created_at__range'] = (value, self.today_date_format)
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


    def get(self, request):

        most_consumed = request.GET.get('most_consumed', None)
        MOST_COMSUMED_CHOICES = ['MOST_COMSUMED_PRODUCTS', 'LAST_7_DAYS', 'LAST_30_DAYS']

        most_ordered = request.GET.get('most_ordered', None)
        MOST_ORDERED_CHOICES = ['MOST_ORDERED_PRODUCTS', 'LAST_7_DAYS', 'LAST_30_DAYS']

        most_transferred = request.GET.get('most_transferred', None)
        MOST_TRANSFERRED_CHOICES = ['MOST_TRANSFERRED_PRODUCTS', 'LAST_7_DAYS', 'LAST_30_DAYS']

        low_stock_products = request.GET.get('low_stock_products', None)
        out_of_stock_products = request.GET.get('out_of_stock_products', None)
        

        
        self.retreive_top_sold_query(request)
        self.retreive_most_consumed_query(request)

        filtered_products = Product.objects.filter(
            is_deleted = False,
            **self.queries['filter'],
        ).annotate(
            **self.queries['annotate'],
        ).distinct().order_by(*self.queries['order_by'])

        # serialized = ProductInsightSerializer(filtered_products, many=True)

        data = []

        for product_instance in filtered_products:
            product = {
                # 'id' : f'{product_instance.id}',
                'name' : f'{product_instance.name}',
            }

            if top_sold:
                product['top_sold_orders'] = int(product_instance.top_sold_orders)

            data.append(product)

        response = Response(
            {
                'status' : True,
                'status_code' : 200,
                'request' : {
                    'queries' : self.queries
                },
                'response' : {
                    'message' : 'Insight Products',
                    'error_message' : None,
                    'products' : data
                }
            },
            status=status.HTTP_200_OK
        )
        return response