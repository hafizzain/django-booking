from urllib import response
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from Appointment.models import Appointment, AppointmentService

from django.conf import settings
from datetime import datetime,date

from Utility.models import ExceptionRecord


def Add_appointment(appointment = None):
    if appointment is None:
        ExceptionRecord.objects.create(
            text='Appointment Is None'
        )

    try:
        appointment =  AppointmentService.objects.filter(appointment = appointment)
        for appo in appointment:
            
            email_c =appo.appointment.client.email
            ser_name =appo.service.name
            dat = appo.appointment_date
            mem_email = appo.member.email
            mem_name = appo.member.full_name
            mem_id= appo.member.employee_id
            name = appo.appointment.client.full_name  

            html_file = render_to_string("AppointmentEmail/add_appointment.html", {'name': name,'email': email_c, 'ser_name':ser_name ,'t_name':mem_name , 'date':dat, 'mem_id':mem_id})
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

    name = appointment.client.full_name
    email_c = appointment.client.email

    try:     
        html_file = render_to_string("AppointmentEmail/add_appointment.html", {'name': name,'t_name':name , 'ser_name':ser_name , 'date':dat, 'mem_id':mem_id})
        text_content = strip_tags(html_file)
            
        email = EmailMultiAlternatives(
                'Appointment Added',
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
        print(err)