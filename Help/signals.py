

from django.dispatch import receiver
from django.db.models.signals import post_save
from Utility.Constants.compressImage import upload_to_bucket

from Help.models import HelpContent

@receiver(post_save, sender=HelpContent)
def UploadHelpContentImageToS3Bucket(sender, instance, *args, **kwargs):
    if instance.image:
        upload_to_bucket(instance.image.path, instance.image.name)