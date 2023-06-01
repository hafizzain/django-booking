from urllib import response
from xmlrpc import client
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from Appointment.models import Appointment, AppointmentService

from django_tenants.utils import tenant_context
from django.conf import settings
from datetime import datetime,date

from Business.models import Business
from Tenants.models import Tenant


def send_appointment_to_business(busines_user):
    today = date.today()

    email = busines_user.user.email
    name = busines_user.user.full_name
    
    appointments =  AppointmentService.objects.filter(appointment_date = today)
    price_list=[]
    try:
        
        for appointment in appointments:
                
                price = appointment.service.price
                price_list.append(price)

    except Exception as err:
        print(err)
    
    toatal_price = sum(price_list)
    
    html_file = render_to_string("AppointmentEmail/daily_booking.html", {'price_list' : toatal_price, 'appointment': appointments, 'name': name})
    text_content = strip_tags(html_file)
            
    email = EmailMultiAlternatives(
                'Appointment Added',
                text_content,
                settings.EMAIL_HOST_USER,
                to = [email],
            
            )
    email.attach_alternative(html_file, "text/html")
    email.send()



def today_appointment():
    all_tenants = Tenant.objects.all()
    for tenant in all_tenants:
        with tenant_context(tenant):
            busines_user = Business.objects.all()
            if len(busines_user) > 0:
                busines_user = busines_user[0]
                send_appointment_to_business(busines_user)                  
