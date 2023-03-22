from urllib import response
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from Appointment.models import Appointment, AppointmentService
from Business.models import ClientNotificationSetting, StaffNotificationSetting

from django_tenants.utils import tenant_context
from django.conf import settings
from datetime import datetime,date

from Utility.models import ExceptionRecord


def Add_appointment(appointment = None, tenant = None, client =  None):
    if appointment is None or tenant is None:
        ExceptionRecord.objects.create(
            text='Appointment, Tenant Is None'
        )

    with tenant_context(tenant):
        try:
            appointment =  AppointmentService.objects.filter(appointment = appointment)                
            for appo in appointment:
                
                email_c = appo.appointment.client.email
                name_c = appo.appointment.client.full_name
                ser_name = appo.service.name
                dat = appo.appointment_date
                mem_email = appo.member.email
                mem_name = appo.member.full_name
                mem_id= appo.member.employee_id
                client_type= appo.appointment.client_type
                name = appo.appointment.client.full_name

                phone = appo.appointment.client.mobile_number
                location = appo.appointment.business_address.address_name
                duration = appo.duration
                
                try:
                    staff_email = StaffNotificationSetting.objects.get(business = str(appo.appointment.business))
                    client_email = ClientNotificationSetting.objects.get(business = str(appo.appointment.business))
                except:
                    pass
                if staff_email.sms_daily_sale == True:
                    ExceptionRecord.objects.create(
                    text = f'ccreate client 43 {staff_email.sms_daily_sale == True}'
                )
                    try:   
                        html_file = render_to_string("AppointmentEmail/email_for_client_appointment.html", {'client': True, 'staff': False,'name': name_c,'t_name':mem_name , 'ser_name':ser_name , 'date':dat, 'mem_id':mem_id, 'client_type': client_type})
                        text_content = strip_tags(html_file)
                            
                        email = EmailMultiAlternatives(
                                'Appointment Booked',
                                text_content,
                                settings.EMAIL_HOST_USER,
                                #to = [mem_email],
                                to = [client_email],
                            
                            )
                        email.attach_alternative(html_file, "text/html")
                        email.send()
                    except Exception as err:
                        pass
                    
            current_time = datetime.now().time()
            if client_email.sms_appoinment == True and client:
                ExceptionRecord.objects.create(
                    text=f'client email {email_c}'
                )
                try:
                    #html_file = render_to_string("AppointmentEmail/add_appointment.html",{'client': False, 'appointment' : appointment,'staff': True,'t_name':name_c} )
                    html_file = render_to_string("AppointmentEmail/new_appointment_n.html", { 
                                'ser_name':ser_name ,'t_name':name , 'mem_name':mem_name,
                                'date':dat, 'location': location, 'duration': duration,
                                'time': current_time,
                                })
                    text_content = strip_tags(html_file)
                    
                    email = EmailMultiAlternatives(
                        'Appointment Booked',
                        text_content,
                        settings.EMAIL_HOST_USER,
                        #to = [email_c],
                        to = [mem_email],
                    )
                        
                    email.attach_alternative(html_file, "text/html")
                    email.send()
                except Exception as err:
                    ExceptionRecord.objects.create(
                        text = f'Error on creating email client;;;'
                    )
            ExceptionRecord.objects.create(
                text = f'create app email {staff_email.sms_daily_sale} {client_email.sms_appoinment}'
            )
    
        except Exception as err:
            ExceptionRecord.objects.create(
                text = f'create email line 78 on create app {str(err)} '
        )