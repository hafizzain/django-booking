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


def Add_appointment(appointment = None, tenant = None):
    if appointment is None or tenant is None:
        ExceptionRecord.objects.create(
            text='Appointment, Tenant Is None'
        )
    current_time = datetime.now().time()
    with tenant_context(tenant):
        try:
            appointment =  AppointmentService.objects.filter(appointment = appointment)           
            
            for appo in appointment:
                try:
                    staff_email = StaffNotificationSetting.objects.get(business = str(appo.appointment.business))
                    client_email = ClientNotificationSetting.objects.get(business = str(appo.appointment.business))
                except:
                    pass 
                
                try:
                    email_c = appo.appointment.client.email
                    name_c = appo.appointment.client.full_name
                    client_type= appo.appointment.client_type
                except:
                    pass
                
                ser_name = appo.service.name
                dat = appo.appointment_date
                mem_email = appo.member.email
                mem_name = appo.member.full_name
                mem_id= appo.member.employee_id
                location = appo.business_address.address_name
                duration = appo.duration
                
                if staff_email.sms_daily_sale == True:
                    
                    try:   
                        html_file = render_to_string("AppointmentEmail/appointment_staff_new.html", {
                            'client': False, 'staff': True, #'name': name_c,'client_type': client_type ,
                            't_name':mem_name , 'ser_name':ser_name , 
                            'date':dat, 'mem_id':mem_id, 
                            'location':location, 'duration': duration, 'current_time': current_time,
                            })
                        text_content = strip_tags(html_file)
                        ExceptionRecord.objects.create(
                            text = f'inter in employee send email '
                        )
                        email = EmailMultiAlternatives(
                                'Appointment Booked',
                                text_content,
                                settings.EMAIL_HOST_USER,
                                #to = [mem_email],
                                to = [mem_email],
                            
                            )
                        email.attach_alternative(html_file, "text/html")
                        email.send()
                    except Exception as err:
                        ExceptionRecord.objects.create(
                            text = f'send email for employee error face issue {str(err)} '
                    )
        
            # if client_email.sms_appoinment == True and name_c is not None :
            #     try:
            #         #html_file = render_to_string("AppointmentEmail/add_appointment.html",{'client': False, 'appointment' : appointment,'staff': True,'t_name':name_c} )
            #         html_file = render_to_string("AppointmentEmail/new_appointment_n.html",{'client': True, 'appointment' : appointment,'staff': False,'t_name':name_c ,'time': current_time,} )
            #         text_content = strip_tags(html_file)
                    
            #         email = EmailMultiAlternatives(
            #             'Appointment Booked',
            #             text_content,
            #             settings.EMAIL_HOST_USER,
            #             to = [email_c],
            #             #to = [mem_email],
            #         )
                        
            #         email.attach_alternative(html_file, "text/html")
            #         email.send()
                    
            #     except Exception as err:
            #         ExceptionRecord.objects.create(
            #             text = f'Error on creating email client;;; {str(err)}'
            #         )
    
        except Exception as err:
            ExceptionRecord.objects.create(
                text = f'create email line 78 on create app {str(err)} '
        )