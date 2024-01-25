

from django.dispatch import receiver

from django.db.models.signals import post_save

from Appointment.models import AppointmentService
from Client.models import ClientImages
from Utility.Constants.compressImage import upload_to_bucket


@receiver(post_save, sender=AppointmentService)
def onAppointmentCreateAddClientStatus(sender, instance, created, **kwargs):
    if created and instance.appointment and instance.appointment.client:
        instance.client_tag = instance.appointment.client.client_tag
        instance.client_type = instance.appointment.client.client_type
        instance.save()


@receiver(post_save, sender=ClientImages)
def UploadLogoToS3Bucket(sender, instance, *args, **kwargs):
    if instance.image:
        upload_to_bucket(instance.image.path, instance.image.file_name)