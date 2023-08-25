

from django.dispatch import receiver
from django.db.models.signals import post_save
from Utility.Constants.compressImage import upload_to_bucket

from Business.models import Business, BusinessAddressMedia

@receiver(post_save, sender=Business)
def UploadLogoToS3Bucket(sender, instance, *args, **kwargs):
    if instance.logo:
        upload_to_bucket(instance.logo.path, instance.logo.name)
    
    if instance.banner:
        upload_to_bucket(instance.banner.path, instance.banner.name)


@receiver(post_save, sender=BusinessAddressMedia)
def UploadBusinessAddressMediaToS3Bucket(sender, instance, *args, **kwargs):
    if instance.image:
        upload_to_bucket(instance.image.path, instance.image.name)