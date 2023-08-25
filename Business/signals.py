

from django.dispatch import receiver
from django.db.models.signals import post_save
from Utility.Constants.compressImage import upload_to_bucket

from Business.models import Business

@receiver(post_save, sender=Business)
def UploadLogoToS3Bucket(sender, instance, *args, **kwargs):
    upload_to_bucket(instance.logo.path, instance.logo.name)
    # instance.is_logo_uploaded_s3 = True
    # instance.save()