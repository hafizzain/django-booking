from django.db import models
import uuid


class HelpContent(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    content = models.TextField()
    parent_comment = models.ForeignKey('HelpContent', on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='helpcenter/images/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)



    created_at = models.DateTimeField(auto_now_add=True)
    is_parent = models.BooleanField(default=False)


    def __str__(self):
        return self.content