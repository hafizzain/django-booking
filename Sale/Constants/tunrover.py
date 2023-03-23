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
from Business.models import BusinessAddress


def ProductTurnover(product=None, product_stock = None, business_address = None ,tenant= None):
    with tenant_context(tenant):
        try:
            email = 'rijariaz5@gmail.com'
                    
            try:
                product= Product.objects.get(id = product)
            except Exception as err:
                pass
            try:
                business= BusinessAddress.objects.get(id = business_address)
            except Exception as err:
                pass
            dates = date.today()
            name = 'Rija Riaz'
            turnover = 'Lowest'
            try:   
                html_file = render_to_string("Sales/product_turnover_details.html", {'name': business.user.full_name ,'pro_name': product.name, 'location':business.address_name, 'turnover': turnover , 'date': dates})
                text_content = strip_tags(html_file)
                    
                email = EmailMultiAlternatives(
                        'Turnover Report',
                        text_content,
                        settings.EMAIL_HOST_USER,
                        to = [business.user.email],
                    
                    )
                email.attach_alternative(html_file, "text/html")
                email.send()
            except Exception as err:
                pass
                # ExceptionRecord.objects.create(
                #     text = f'turnover emails error {str(err)}'
                # )
        except Exception as err:
            pass
                # ExceptionRecord.objects.create(
                #     text = f'turnover emails error {str(err)}'
                # )