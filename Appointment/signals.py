

from django.dispatch import receiver

from django.db.models.signals import post_save

from Appointment.models import AppointmentService

@receiver(post_save, sender=AppointmentService)
def onAppointmentCreateAddClientStatus(sender, instance, created, **kwargs):
    if created and instance.appointment and instance.appointment.client:
        instance.client_tag = instance.appointment.client.client_tag
        instance.client_type = instance.appointment.client.client_type
        instance.save()