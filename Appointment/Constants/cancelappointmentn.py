from urllib import response
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from Appointment.models import Appointment, AppointmentService

from django.conf import settings
from datetime import datetime,date
from Business.models import ClientNotificationSetting, StaffNotificationSetting

from Utility.models import ExceptionRecord
from django_tenants.utils import tenant_context




def cancel_appointment_n(appointment = None , tenant = None):
    if appointment is None or tenant is None:
        ExceptionRecord.objects.create(
            text='Appointment, Tenant Is None'
        )

    with tenant_context(tenant):

        try:
            appointment =  AppointmentService.objects.filter(appointment=appointment)
            
            email_c =appointment.appointment.client.email
            email_m = appointment.member.email
            mem_id= appointment.member.employee_id
            name_c = appointment.appointment.client.full_name
            mem_name= appointment.member.full_name

            ser_name =appointment.service.name
            dat = appointment.appointment_date
            time = datetime.now()
            
            try:
                staff_email = StaffNotificationSetting.objects.get(business = str(appointment.appointment.business))
                client_email = ClientNotificationSetting.objects.get(business = str(appointment.appointment.business))
            except:
                pass
                if staff_email.sms_daily_sale == True: 
                    try:                   
                        html_file = render_to_string("AppointmentEmail/cancel_appointment_n.html", {'name': name_c, 'ser_name':ser_name ,'t_name':mem_name , 'date':dat,'time':time ,'mem_id':mem_id})
                        text_content = strip_tags(html_file)
                            
                        email = EmailMultiAlternatives(
                                'Appointment Canceled',
                                text_content,
                                settings.EMAIL_HOST_USER,
                                to = [email_m],
                            
                            )
                        email.attach_alternative(html_file, "text/html")
                        email.send()
                    except Exception as err:
                            pass
                
            if client_email.sms_appoinment == True:
                ExceptionRecord.objects.create(
                    text = f'ccreate client {client_email.sms_appoinment == True} apppointment {appointment}'
                )
                try:
                    html_file = render_to_string("AppointmentEmail/cancel_appointment_n.html", {'client': False, 'appointment' : appointment,'staff': True,'t_name':name_c})
                    text_content = strip_tags(html_file)
                        
                    email = EmailMultiAlternatives(
                            'Appointment Canceled',
                            text_content,
                            settings.EMAIL_HOST_USER,
                            to = [email_m],
                        
                        )
                    email.attach_alternative(html_file, "text/html")
                    email.send()
                except Exception as err:
                    ExceptionRecord.objects.create(
                        text = f'Error on creating email client;;;'
                    )
        except Exception as err:
                print("Appointment error",err)

        
    
    

# def cancel_appointment_n(appointment = None , tenant = None):
#     if appointment is None or tenant is None:
#         ExceptionRecord.objects.create(
#             text='Appointment, Tenant Is None'
#         )

#     with tenant_context(tenant):

#         try:
#             appointment =  AppointmentService.objects.get(id = appointment.id)
            
#             email_c = appointment.appointment.client.email
#             email_m = appointment.member.email
#             mem_id = appointment.member.employee_id
#             name_c = appointment.appointment.client.full_name
#             mem_name = appointment.member.full_name

#             ser_name = appointment.service.name
#             dat = appointment.appointment_date

#             time = datetime.today().time()
#             loc_name = appointment.business_address.address_name
#             dur = appointment.duration
#             phon = appointment.member.mobile_number
            
#             try:
#                 staff_email = StaffNotificationSetting.objects.get(business = str(appointment.appointment.business))
#                 client_email = ClientNotificationSetting.objects.get(business = str(appointment.appointment.business))
#             except:
#                 pass
#             if staff_email.sms_daily_sale == True:                    
#                 html_file = render_to_string("AppointmentEmail/cancel_appointment_n.html", {'location':loc_name, 'ser_name':ser_name  , 'duration':dur,'time':time, 'date':dat})
#                 text_content = strip_tags(html_file)
                    
#                 email = EmailMultiAlternatives(
#                         'Appointment Canceled',
#                         text_content,
#                         settings.EMAIL_HOST_USER,
#                         to = [email_m],
                    
#                     )
#                 email.attach_alternative(html_file, "text/html")
#                 email.send()
                
#             if client_email.sms_appoinment == True:
#                 html_file = render_to_string("AppointmentEmail/cancel_appointment_n.html", {'name': name_c,'mobile_number': phon,'email':email_m})
#                 text_content = strip_tags(html_file)
                    
#                 email = EmailMultiAlternatives(
#                         'Appointment Canceled',
#                         text_content,
#                         settings.EMAIL_HOST_USER,
#                         to = [email_c],
                    
#                     )
#                 email.attach_alternative(html_file, "text/html")
#                 email.send()
            
#         except Exception as err:
#             print("Appointment error",err)
    