from django.db import models
from Utility.models import Language as AllLanguages
# from Business.models import BusinessAddress
from Authentication.models import User


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
    status_type=(('active', 'active'),('inactive', 'inactive'))
    # location = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey(AllLanguages, on_delete=models.PROTECT, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    invoice = models.CharField(max_length=500, null=True, blank=True)
    items = models.CharField(max_length=500, null=True, blank=True)
    amount = models.CharField(max_length=500, null=True, blank=True)
    subtotal = models.CharField(max_length=500, null=True, blank=True)
    tips = models.CharField(max_length=500, null=True, blank=True)
    taxes = models.CharField(max_length=500, null=True, blank=True)
    total = models.CharField(max_length=500, null=True, blank=True)
    payment_method = models.CharField(max_length=500, null=True, blank=True)
    change = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=10, choices=status_type, default='active')
    
    def __str__(self):
        return f'{self.id} -- {self.invoice} -- {self.items}'
    


class TranslationLabels(models.Model):

    language = models.ForeignKey(Language, on_delete=models.PROTECT, null=True)

    key=models.TextField(null=True, blank=True)
    value=models.TextField(null=True, blank=True)
    english_name = models.TextField(null=True, blank=True)

    order = models.IntegerField(null=True, blank=True)

    
    class Meta:
        ordering = ['-order']
    def __str__(self):
        return f"{self.order} -- {self.english_name}"
