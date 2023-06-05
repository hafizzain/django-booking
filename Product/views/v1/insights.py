
from Product.models import Product

from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.views import APIView

from django.db.models import Count, F, Sum
from Product.serializers import ProductInsightSerializer
import re

from datetime import datetime, timedelta

DATE_REGEX = '\d{4}-\d{2}-\d{2}'

class FilteredInsightProducts(APIView):
    permission_classes = [AllowAny]

    today_date = datetime.now()
    today_date_format = (today_date + timedelta(days=1)).strftime('%Y-%m-%d')
    days_before_7 = (today_date - timedelta(days=7)).strftime('%Y-%m-%d')
    days_before_30 = (today_date - timedelta(days=30)).strftime('%Y-%m-%d')

    queries = {
        'filter' : {},'order_by' : [], 'annotate' : {}
    }

    def retreive_top_sold_query(self, request):
        self.top_sold = request.GET.get('top_sold', None)
        TOP_SOLD_CHOICES = {'TOP_SOLD_PRODUCTS' : lambda : None, 'LAST_7_DAYS' : self.days_before_7 , 'LAST_30_DAYS' : self.days_before_30 }

        if self.top_sold :
            self.queries['order_by'].append('-top_sold_orders')
            self.queries['annotate']['top_sold_orders'] = Sum('product_orders__quantity')
            if self.top_sold in TOP_SOLD_CHOICES or re.match(DATE_REGEX, self.top_sold):
                if self.top_sold != 'TOP_SOLD_PRODUCTS':
                    value = self.top_sold
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
        self.most_consumed = request.GET.get('most_consumed', None)
        MOST_COMSUMED_CHOICES = {'MOST_COMSUMED_PRODUCTS' : None, 'LAST_7_DAYS' : self.days_before_7 , 'LAST_30_DAYS' : self.days_before_30 }

        if self.most_consumed :
            self.queries['order_by'].append('-most_consumed_products')
            self.queries['annotate']['most_consumed_products'] = Sum('consumptions__quantity')
            if self.most_consumed in MOST_COMSUMED_CHOICES or re.match(DATE_REGEX, self.most_consumed):
                if self.most_consumed != 'MOST_COMSUMED_PRODUCTS':
                    value = self.most_consumed
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
            
    def retreive_most_ordered_query(self, request):
        self.most_ordered = request.GET.get('most_ordered', None)


        if self.most_ordered :
            MOST_ORDERED_CHOICES = {'MOST_ORDERED_PRODUCTS' : None, 'LAST_7_DAYS' : self.days_before_7 , 'LAST_30_DAYS' : self.days_before_30 }
            self.queries['order_by'].append('-most_ordered_products')
            self.queries['annotate']['most_ordered_products'] = Sum('product_order_stock__rec_quantity')
            if self.most_ordered in MOST_ORDERED_CHOICES or re.match(DATE_REGEX, self.most_ordered):
                if self.most_ordered != 'MOST_ORDERED_PRODUCTS':
                    value = self.most_ordered
                    if value in ['LAST_7_DAYS', 'LAST_30_DAYS']:
                        value = MOST_ORDERED_CHOICES.get(value)
                    self.queries['filter']['product_order_stock__order__created_at__range'] = (value, self.today_date_format)
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
            
    def retreive_most_transferred_query(self, request):
        self.most_transferred = request.GET.get('most_transferred', None)


        if self.most_transferred :
            MOST_TRANSFERRED_CHOICES = {'MOST_TRANSFERRED_PRODUCTS' : None, 'LAST_7_DAYS' : self.days_before_7 , 'LAST_30_DAYS' : self.days_before_30 }
            self.queries['order_by'].append('-most_transferred_products')
            self.queries['annotate']['most_transferred_products'] = Sum('products_stock_transfers__quantity')
            if self.most_transferred in MOST_TRANSFERRED_CHOICES or re.match(DATE_REGEX, self.most_transferred):
                if self.most_transferred != 'MOST_TRANSFERRED_PRODUCTS':
                    value = self.most_transferred
                    if value in ['LAST_7_DAYS', 'LAST_30_DAYS']:
                        value = MOST_TRANSFERRED_CHOICES.get(value)
                    self.queries['filter']['products_stock_transfers__created_at__range'] = (value, self.today_date_format)
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
    
    def retreive_low_stock_products_query(self, request):
        self.low_stock_products = request.GET.get('low_stock_products', None)

        if self.low_stock_products:
            self.queries['annotate']['sum_of_total_available_stock'] = Sum('product_stock__available_quantity')
            self.queries['annotate']['sum_of_total_lowest_stock_amount'] = Sum('product_stock__low_stock')
            self.queries['annotate']['remaing_stock'] = F('sum_of_total_available_stock') - F('sum_of_total_lowest_stock_amount')

            self.queries['filter']['sum_of_total_available_stock__lte'] = F('sum_of_total_lowest_stock_amount')


    def retreive_out_of_stock_products_query(self, request):
        self.out_of_stock_products = request.GET.get('out_of_stock_products', None)

        if self.out_of_stock_products:

            self.queries['filter']['product_stock__available_quantity__lte'] = 0



    def get(self, request):

        location_id = request.GET.get('location', None)

        if not location_id:
            return Response(
                {
                    'status' : False,
                    'status_code' : 400,
                    'response' : {
                        'message' : 'Please provide following missing fields',
                        'error_message' : 'Missing fields error',
                        'fields' : [
                            'location'
                        ]
                    }
                },
                status=status.HTTP_200_OK
            )

        
        self.retreive_top_sold_query(request)
        self.retreive_most_consumed_query(request)
        self.retreive_most_ordered_query(request)
        self.retreive_most_transferred_query(request)
        self.retreive_low_stock_products_query(request)
        self.retreive_out_of_stock_products_query(request)

        filtered_products = Product.objects.annotate(
            **self.queries['annotate'],
        ).filter(
            is_deleted = False,
            product_stock__location__id = location_id,
            **self.queries['filter'],
        ).distinct().order_by(*self.queries['order_by'])

        # serialized = ProductInsightSerializer(filtered_products, many=True)

        data = []

        for product_instance in filtered_products:
            product = {
                # 'id' : f'{product_instance.id}',
                'name' : f'{product_instance.name}',
            }

            if self.top_sold:
                product['top_sold_orders'] = int(product_instance.top_sold_orders)

            if self.most_consumed:
                product['most_consumed_products'] = int(product_instance.most_consumed_products)
            if self.most_ordered:
                product['most_ordered_products'] = int(product_instance.most_ordered_products)
            if self.most_transferred:
                product['most_transferred_products'] = int(product_instance.most_transferred_products)

            if self.low_stock_products:
                product['sum_of_total_available_stock'] = int(product_instance.sum_of_total_available_stock)
                product['sum_of_total_lowest_stock_amount'] = int(product_instance.sum_of_total_lowest_stock_amount)
                product['lowest_stock'] = int(product_instance.remaing_stock)

            # if self.out_of_stock_products:
            #     product['available_stock'] = int(product_instance.product_stock.all().available_quantity)

            data.append(product)

        response = Response(
            {
                'status' : True,
                'status_code' : 200,
                'request' : {
                    'queries' : str(self.queries)
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
    


@api_view(['GET'])
@permission_classes([AllowAny])
def get_filtered_chat_products(request):
    location_id = request.GET.get('location', None)
    selected_year = request.GET.get('selected_year', '2023')

    if not location_id:
        return Response(
            {
                'status' : False,
                'status_code' : 400,
                'response' : {
                    'message' : 'Please provide following missing fields',
                    'error_message' : 'Missing fields error',
                    'fields' : [
                        'location'
                    ]
                }
            },
            status=status.HTTP_200_OK
        )
    
    products = Product.objects.annotate(
        most_transferred_products = Sum('products_stock_transfers__quantity')
    ).filter(
        product_stock__location__id = location_id,
        is_deleted = False,
        products_stock_transfers__created_at__range = ('2020-01-01', f'{selected_year}-12-31')
    ).order_by('-most_transferred_products')[:10]


    data = []
    for product_instance in products:
        product = {
            # 'id' : f'{product_instance.id}',
            'name' : f'{product_instance.name}',
            'data' : int(product_instance.most_transferred_products),
        }

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