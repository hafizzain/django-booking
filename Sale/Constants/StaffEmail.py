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

def StaffSaleEmail(ids = None, location = None, tenant = None, member =None, invoice = None, client = None):
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
            
            date = datetime.date.today()
            current_time = datetime.datetime.now().time()
            
            invoice =  invoice.split('-')[0]
            ExceptionRecord.objects.create(
                    text = f'Staff Email on sale {member_id} {location} {ids} {invoice} {date} {current_time} {client} '
                )
            try:   
                html_file = render_to_string("Sales/quick_sales_staff.html", {'name': member_id.name,'location':location, 'sale_type': ids, 'invoice': invoice, 'date': date,'time': current_time, 'client': client})
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