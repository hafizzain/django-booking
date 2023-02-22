from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from Appointment.models import Appointment, AppointmentService
from Authentication.models import AccountType, User
from Tenants.models import EmployeeTenantDetail, Tenant
from Utility.models import ExceptionRecord

from django_tenants.utils import tenant_context
from django.conf import settings

def add_employee(emp_name, emp_email, mobile_number , template,busines_name , tenant_id ,domain,user ,tenant = None):
    # if tenant is None:
    #     ExceptionRecord.objects.create(
    #         text='Tenant is None'
    #     )
    try:
        tenant = Tenant.objects.get(id = tenant_id )
    except:
        pass
    with tenant_context(Tenant.objects.get(schema_name = 'public')):
        #url = f'http://{domain}.localhost:3000/set-password?user_id={user.id}&hash={tenant_id}'
        url = f'http://{domain}.midtechdxb.com/set-password?user_id={user.id}&hash={tenant_id}'
        
        try:
            html_file = render_to_string("EmployeeEmail/employee_create.html", {'name': emp_name,'t_name': template , 'bes_name':busines_name, 'url': url })
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
        try:
            try:
                username = emp_email.split('@')[0]
                try:
                    user_check = User.objects.get(username = username)
                except Exception as err:   
                    pass
                else:
                    username = f'{username} {len(User.objects.all())}'
            except Exception as err:
                pass
            user = User.objects.create(
                    first_name = emp_name,
                    username = username,
                    email = emp_email,
                    is_email_verified = True,
                    is_active = True,
                    mobile_number = mobile_number,
                ) 
            account_type = AccountType.objects.create(
                user = user,
                account_type = 'Employee'
            )       
            user_client = EmployeeTenantDetail.objects.create(
                user = user,
                tenant = tenant,
                is_tenant_staff = True
            )
            
        except Exception as err:
            ExceptionRecord.objects.create(
                text=str(err)
            )