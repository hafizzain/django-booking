from django.db import models
from Utility.models import Language as AllLanguages
from Business.models import BusinessAddress


class Language(models.Model):
    title = models.CharField(max_length=132, null=True)
    icon = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.title

class Section(models.Model):
    title = models.CharField(max_length=132, null=True)
    icon = models.TextField(null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.PROTECT, null=True)
    
    def __str__(self):
        return self.title 
    
class Labels(models.Model):
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name='language_sections', null=True, blank=True)
    label = models.TextField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.label} - {self.value}"



class InvoiceTranslation(models.Model):
    location = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey(AllLanguages, on_delete=models.PROTECT, null=True, blank=True)
    invoice = models.CharField(max_length=500)
    items = models.CharField(max_length=500)
    amount = models.CharField(max_length=500)
    subtotal = models.CharField(max_length=500)
    tips = models.CharField(max_length=500)
    taxes = models.CharField(max_length=500)
    total = models.CharField(max_length=500)
    payment_method = models.CharField(max_length=500)
    
    def __str__(self):
        return f'{self.invoice} -- {self.items}'