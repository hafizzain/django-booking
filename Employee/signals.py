

from django.dispatch import receiver
from django.db.models.signals import post_save
from Utility.Constants.compressImage import upload_to_bucket

from Employee.models import Employee

@receiver(post_save, sender=Employee)
def UploadEmployeeImageToS3Bucket(sender, instance, *args, **kwargs):
    if instance.image:
        upload_to_bucket(instance.image.path, instance.image.name)