from urllib import response
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from Appointment.models import Appointment, AppointmentService

from django_tenants.utils import tenant_context
from django.conf import settings
from datetime import datetime,date

from Utility.models import ExceptionRecord


def Add_appointment(appointment = None, tenant = None):
    if appointment is None or tenant is None:
        ExceptionRecord.objects.create(
            text='Appointment, Tenant Is None'
        )

    with tenant_context(tenant):

        try:
            appointment =  AppointmentService.objects.filter(appointment = appointment)
            if len(appointment) == 0 :
                ExceptionRecord.objects.create(text='0 Records Founds Appointment services sending mails to appointment client and staffs')
                return
                
            for appo in appointment:
                
                email_c =appo.appointment.client.email
                name_c =appo.appointment.client.full_name
                ser_name = appo.service.name
                dat = appo.appointment_date
                mem_email = appo.member.email
                mem_name = appo.member.full_name
                mem_id= appo.member.employee_id
                client_type= appo.appointment.client_type
                name = appo.appointment.client.full_name  
                
        #{'client': False, 'staff': True,'name': name,'email': email_c, 'ser_name':ser_name ,'t_name':mem_name , 'date':dat, 'mem_id':mem_id, 'client_type': client_type}
            html_file = render_to_string("AppointmentEmail/add_appointment.html",{'client': False, 'appointment' : appointment,'staff': True,'t_name':mem_name} )
            text_content = strip_tags(html_file)
            
            email = EmailMultiAlternatives(
                'Appointment Added',
                text_content,
                settings.EMAIL_HOST_USER,
                to = [mem_email],
            )
                
            email.attach_alternative(html_file, "text/html")
            email.send()
    
        except Exception as err:
            ExceptionRecord.objects.create(
                text=str(err)
            )
            print(err)

        #name = appointment.client.full_name
        #email_c = appointment.client.email

        try:     
            html_file = render_to_string("AppointmentEmail/email_for_client_appointment.html", {'client': False, 'staff': True,'name': name_c,'t_name':name , 'ser_name':ser_name , 'date':dat, 'mem_id':mem_id, 'client_type': client_type})
            text_content = strip_tags(html_file)
                
            email = EmailMultiAlternatives(
                    'Appointment Booked',
                    text_content,
                    settings.EMAIL_HOST_USER,
                    to = [email_c],
                
                )
            email.attach_alternative(html_file, "text/html")
            email.send()
        except Exception as err:
            ExceptionRecord.objects.create(
                text=str(err)
            )