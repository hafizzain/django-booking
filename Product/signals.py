

from django.dispatch import receiver
from django.db.models.signals import post_save
from Utility.Constants.compressImage import upload_to_bucket

from Product.models import Brand, ProductMedia

@receiver(post_save, sender=ProductMedia)
def UploadProductMediaImageToS3Bucket(sender, instance, *args, **kwargs):
    if instance.image:
        upload_to_bucket(instance.image.path, instance.image.name)

@receiver(post_save, sender=Brand)
def UploadBrandImageToS3Bucket(sender, instance, *args, **kwargs):
    if instance.image:
        upload_to_bucket(instance.image.path, instance.image.name)