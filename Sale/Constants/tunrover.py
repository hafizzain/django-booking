from urllib import response
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from Product.models import Product, ProductOrderStockReport

from django_tenants.utils import tenant_context
from django.conf import settings
from django.db.models import Sum
from datetime import datetime,date

from Utility.models import ExceptionRecord, TurnOverProductRecord

def ProductTurnover(product=None, product_stock = None, business_address = None ,tenant= None):
    with tenant_context(tenant):
        try:
            email = 'rijariaz5@gmail.com'
            try:
                product= Product.objects.get(id = str(product))
            except Exception as err:
                pass
            
            TurnOverProductRecord.objects.create(
                text = 'Email Generate for Product Turnover',
                i_email = 'TURNOVER_PRODUCT'
            )
            try:
                total_sold = ProductOrderStockReport.objects.filter(
                    product__id=product,
                    report_choice__iexact='Sold',
                    location__id = business_address,            
                ).aggregate(Sum('quantity'))
            except Exception as err:
                ExceptionRecord.objects.create(
                text = f'turnover emails error35:::  {str(err)}'
            )
            
            ExceptionRecord.objects.create(
                text = f'turnover emails error {total_sold}'
            )
            
            try:   
                html_file = render_to_string("Sales/product_turnover_details.html")
                text_content = strip_tags(html_file)
                    
                email = EmailMultiAlternatives(
                        'Turnover Report',
                        text_content,
                        settings.EMAIL_HOST_USER,
                        to = [email],
                    
                    )
                email.attach_alternative(html_file, "text/html")
                email.send()
            except Exception as err:
                ExceptionRecord.objects.create(
                    text = f'turnover emails error {str(err)}'
                )
        except Exception as err:
            ExceptionRecord.objects.create(
                text = f'turnover emails error {str(err)}'
            )