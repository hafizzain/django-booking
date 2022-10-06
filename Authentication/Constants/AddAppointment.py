from urllib import response
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from Appointment.models import Appointment, AppointmentService

from django.conf import settings
from datetime import datetime,date


def Add_appointment(appointment = None):
    if appointment is None:
        return response({
            'message': 'Appointment error'
        })
    for ids in appointment:
        try:
            appo=  AppointmentService.objects.get(id = str(ids))
            email_c =appo.appointment.client.email
            ser_name =appo.service.name
            dat = date.today()
            mem_email = appo.member.email
            mem_name = appo.member.full_name
            name = appo.appointment.client.full_name  

            #print(f'{mem_email} {email}')
            #print(f'{name} {email} {ser_name} {dat} {mem_email} {mem_name} ')
            
            html_file = render_to_string("AppointmentEmail/add_appointment.html", {'name': name,'email': email_c, 'ser_name':ser_name ,'t_name':mem_name , 'date':dat})
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
            print(err)
    
    name = appo.appointment.client.full_name  
    print(f'{name} - {email_c}')
    try:     
        html_file = render_to_string("AppointmentEmail/add_appointment.html", {'name': name,'t_name':name , 'ser_name':ser_name , 'date':dat})
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
        print(err)
            
    
    #print(f'{name} {email} {ser_name} {dat} {mem_email}')
    # print(appo[0].member)
    
    # for key, value in kwargs.items():
    #     print( key, value)
    #     if key == 'email':
    #         send = value
            
    
    # email_host = 'developeracount211@gmail.com'
    # print(send)
    
    