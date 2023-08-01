
from urllib import request
from Service.models import Service
from Product.models import Product

from Business.models import ClientNotificationSetting, StaffNotificationSetting, StockNotificationSetting

from Client.models import Client
from Employee.models import Employee
from Utility.models import ExceptionRecord
from django_tenants.utils import tenant_context
from django.conf import settings
from datetime import datetime,date

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

# def StaffSaleEmail(ids = None, location = None, tenant = None, member =None, invoice = None, client = None):
def StaffSaleEmail( ids = None,location = None, tenant = None, member =None, invoice = None, client = None):
    with tenant_context(tenant):
        sdata = []
        
        try:
            if ids is not None:
                for service_name in ids:
                    service = Service.objects.get( name = str(service_name))
                    sdata.append(f'Service {service.name}')

            if ids is not None:
                for product_name in ids:
                    product = Product.objects.get( name = str(product_name))
                    sdata.append(f'Product {product.name}')       
        except Exception as err:
            ExceptionRecord.objects.create(
                    text = f' error in getting names of service and product{str(err)}'
                )
                
        try:
            dates = date.today()
            current_time = datetime.now().time()
            
            invoice =  str(invoice).split('-')[0]
            
            try:
                member_id = Employee.objects.get(id = str(member))
            except Exception as err:
                pass
            try:
                client_email = ClientNotificationSetting.objects.get(business = str(member_id.business))
                staff_email = StaffNotificationSetting.objects.get(business = str(member_id.business))
                
            except Exception as err:
                pass            
            
            try:
                client = Client.objects.get(id = str(client))
                
                if client_email.sms_quick_sale == True:
                    
                    html_file = render_to_string("Sales/quick_sales_staff.html", {'name': client.full_name,'location':location, 'sale_type': ids, 'invoice': invoice, 'date': dates,'time': current_time, 'client': None})
                    text_content = strip_tags(html_file)
                        
                    email = EmailMultiAlternatives(
                            'Daily Sale',
                            text_content,
                            settings.EMAIL_HOST_USER,
                            to = [client.email],
                        
                        )
                    email.attach_alternative(html_file, "text/html")
                    email.send()
            except Exception as err:
                pass
            
            try:   
                if staff_email.sms_daily_sale == True:
                    
                   
                    # html_file = render_to_string("Sales/quick_sales_staff.html", {'name': member_id.full_name,'location':location, 'sale_type': ids, 'invoice': invoice, 'date': dates,'time': current_time, 'client': client})
                    html_file = render_to_string("Sales/quick_sales_staff.html", {
                        'name': member_id.full_name,
                        'location': location,
                        'sdata': sdata,
                        'invoice': invoice,
                        'date': dates,
                        'time': current_time,
                        'client': client,
                    })
                    text_content = strip_tags(html_file)     
                    email = EmailMultiAlternatives(
                            'Daily Sale',
                            text_content,
                            settings.EMAIL_HOST_USER,
                            to = [member_id.email],
                        
                        )
                    email.attach_alternative(html_file, "text/html")
                    email.send()
            except Exception as err:
                ExceptionRecord.objects.create(
                    text = f' error in email sale{str(err)}'
                )
        except Exception as err:
                ExceptionRecord.objects.create(
                    text = f' error in email sale{str(err)}'
                )