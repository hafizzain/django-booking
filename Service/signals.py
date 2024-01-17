
from django.dispatch import receiver
from django.db.models.signals import post_save
from Utility.Constants.compressImage import upload_to_bucket

from Service.models import Service, ServiceGroup

@receiver(post_save, sender=Service)
def UploadLogoToS3Bucket(sender, instance, *args, **kwargs): 
    if instance.image:
        upload_to_bucket(instance.image.path, instance.image.name)

@receiver(post_save, sender=ServiceGroup)
def UploadLogoToS3Bucket(sender, instance, *args, **kwargs): 
    if instance.image:
        upload_to_bucket(instance.image.path, instance.image.name)