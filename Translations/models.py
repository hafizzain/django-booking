from django.db import models

class Language(models.Model):
    title = models.CharField(max_length=132, null=True)
    
    def __str__(self):
        return self.title
    
    
class Labels(models.Model):
    language = models.ForeignKey(Language, on_delete=models.PROTECT, related_name='language_labels', null=True)
    section = models.CharField(max_length=132, null=True, blank=True)

    label = models.TextField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.label} - {self.value}"


