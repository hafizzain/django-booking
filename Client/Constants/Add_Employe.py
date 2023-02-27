from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from Appointment.models import Appointment, AppointmentService
from Authentication.models import AccountType, User
from Tenants.models import EmployeeTenantDetail, Tenant
from Utility.models import ExceptionRecord

from django_tenants.utils import tenant_context
from django.conf import settings

def add_client(emp_name, emp_email, template,busines_name ,tenant = None):
    # if tenant is None:
    #     ExceptionRecord.objects.create(
    #         text='Tenant is None'
    #     )

    # with tenant_context(tenant):
    
    try:
        html_file = render_to_string("EmployeeEmail/client_create.html", {'name': emp_name,'t_name': template , 'bes_name':busines_name, })
        text_content = strip_tags(html_file)
        
        email = EmailMultiAlternatives(
            'Employee Created',
            text_content,
            settings.EMAIL_HOST_USER,
            to = [emp_email],
        
        )
        email.attach_alternative(html_file, "text/html")
        email.send()
        print('email sended')
    
    except Exception as err:
        ExceptionRecord.objects.create(
            text=str(err)
        )