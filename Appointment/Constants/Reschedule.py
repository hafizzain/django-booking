from urllib import response
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from Appointment.models import Appointment, AppointmentService

from django.conf import settings
from datetime import datetime,date
from Business.models import ClientNotificationSetting, StaffNotificationSetting
from django_tenants.utils import tenant_context
from Utility.models import ExceptionRecord




def reschedule_appointment(appointment = None , tenant = None, client =  None):
    if appointment is None or tenant is None:
        ExceptionRecord.objects.create(
            text='Appointment, Tenant Is None'
        )

    with tenant_context(tenant):

        try:
            
            appointment =  AppointmentService.objects.filter(appointment = str(appointment))
            current_time = datetime.now().time()
            client =  False
            for appo in appointment:
                
                email_c = appo.appointment.client.email
                phone = appo.appointment.client.mobile_number
                name_c = appo.appointment.client.full_name
                ser_name = appo.service.name
                dat = appo.appointment_date
                mem_email = appo.member.email
                mem_name = appo.member.full_name
                mem_id= appo.member.employee_id
                name = appo.appointment.client.full_name
                location = appo.appointment.business_address.address_name
                duration = appo.duration
                time = appo.appointment_time
                
                if name is not None:
                    client = True
                
                try:
                    staff_email = StaffNotificationSetting.objects.get(business = str(appo.appointment.business))
                    client_email = ClientNotificationSetting.objects.get(business = str(appo.appointment.business))
                except:
                    pass
                if staff_email.sms_daily_sale == True:
                    try:
                        html_file = render_to_string("AppointmentEmail/appointment_reschedule_n.html", {'name': name_c, 
                                    'ser_name':ser_name ,'t_name':mem_name , 
                                    'date':dat, 'mem_id':mem_id,'location': location, 'duration': duration,
                                    'time': time
                                    })
                        text_content = strip_tags(html_file)
                            
                        email = EmailMultiAlternatives(
                                'Appointment Reschedule',
                                text_content,
                                settings.EMAIL_HOST_USER,
                                to = [mem_email],
                            )
                        email.attach_alternative(html_file, "text/html")
                        email.send()
                        
                    except Exception as err:
                        ExceptionRecord.objects.create(
                            text = f'reschedule_appointment template error{str(err)}'
                        )
                        
            if client_email.sms_appoinment == True and client == True:
                
                    html_file = render_to_string("AppointmentEmail/appointment_reschedule_n.html", {'name': name_c, 
                                'ser_name':ser_name ,'t_name':name , 
                                'date':dat, 'mem_id':mem_id,'location': location, 'duration': duration,
                                'time': current_time, 'email_c': email_c , 'phone': phone, 'client': client
                                })
                    text_content = strip_tags(html_file)
                        
                    email = EmailMultiAlternatives(
                            'Appointment Reschedule',
                            text_content,
                            settings.EMAIL_HOST_USER,
                            to = [email_c],
                        )
                    email.attach_alternative(html_file, "text/html")
                    email.send()
                
        except Exception as err:
            ExceptionRecord.objects.create(
                text = f'reschedule_appointment {str(err)}'
            )
            
        
    