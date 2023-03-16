from Service.models import Service
from Product.models import Product
from Business.models import StaffNotificationSetting
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
def StaffSaleEmail( ids = None,location = None, tenant = None, member =None, invoice = None, client = None, ssitem = None, spitem = None):
    with tenant_context(tenant):
        try:
            try:
                member_id = Employee.objects.get(id = str(member))
            except Exception as err:
                pass
            
            try:
                client = Client.objects.get(id = str(client))
            except Exception as err:
                pass
            
            dates = date.today()
            current_time = datetime.now().time()
            
            invoice =  str(invoice).split('-')[0]
            try:
                if ssitem:
                    ssitem_obj = Product.name.get(id=ssitem)
                    
                if spitem:
                    spitem_obj = Service.name.get(id=spitem)
                    
            except Exception as err:
                pass
            try:   
                # html_file = render_to_string("Sales/quick_sales_staff.html", {'name': member_id.full_name,'location':location, 'sale_type': ids, 'invoice': invoice, 'date': dates,'time': current_time, 'client': client})
                html_file = render_to_string("Sales/quick_sales_staff.html", {
                    'name': member_id.full_name,
                    'location': location,
                    'sale_type': ids,
                    'invoice': invoice,
                    'date': dates,
                    'time': current_time,
                    'client': client,
                    'ssitem': ssitem_obj,
                    'spitem': spitem_obj
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