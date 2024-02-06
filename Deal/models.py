from django.db import models

from uuid import uuid4
from Product.models import Category, Brand, Product
from Service.models import Service
from Business.models import BusinessAddress
# Create your models here.


class DealCategory(models.Model):
    name = models.CharField(default='', max_length=999)


class RedeemableChannel(models.Model):
    name = models.CharField(default='', max_length=999)


class Deal(models.Model):

    DEAL_TYPE_CHOICES = (
        ('Fixed Amount Discount Deal', 'Fixed Amount Discount Deal'),
        ('Percentage Discount Deal', 'Percentage Discount Deal'),
        ('Buy one or more item get one or more free/discount', 'Buy one or more item get one or more free/discount'),
        ('Complimentary Voucher', 'Complimentary Voucher'),
        ('Custom Package', 'Custom Package'),
        ('Get free item when user purchase specific items in given period', 'Get free item when user purchase specific items in given period'),
        ('Spend some amount and get some item free', 'Spend some amount and get some item free'),
        ('Fixed price items deal', 'Fixed price items deal'),
    )

    AUDIENCE_CHOICES = (
        ('public', 'public'),
        ('pre-set-users', 'pre-set-users'),
    )

    CODE_CHOICES = (
        ('unique', 'unique'),
        ('generic', 'generic'),
    )

    CUSTOMER_TYPE_CHOICES = (
        ('any', 'any'),
        ('lead', 'lead'),
        ('new', 'new'),
        ('regular', 'regular'),
        ('lapsed', 'lapsed'),
    )

    USAGE_LIMIT_CHOICES = (
        ('unlimited', 'unlimited'),
        ('limited', 'limited'),
    )

    VALIDITY_CHOICES = (
        ("from-start-to-end-date" , "from-start-to-end-date"),
        ("days-from-start-date" , "days-from-start-date"),
        ("months-from-start-date" , "months-from-start-date"),
        ("years-from-start-date" , "years-from-start-date"),
    )

    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    title = models.CharField(default='', max_length=999)

    deal_type = models.CharField(default='Fixed Amount Discount Deal', max_length=999, choices=DEAL_TYPE_CHOICES)
    category = models.ForeignKey(DealCategory, on_delete=models.SET_NULL, null=True, related_name='deal_category')

    audience = models.CharField(default='public', max_length=999, choices=AUDIENCE_CHOICES)
    codeGeneration = models.CharField(default='unique', max_length=999, choices=CODE_CHOICES)
    customerType = models.CharField(default='any', max_length=999, choices=CUSTOMER_TYPE_CHOICES)
    usageLimitType = models.CharField(default='limited', max_length=999, choices=USAGE_LIMIT_CHOICES)
    validityPeriodType = models.CharField(default='from-start-to-end-date', max_length=999, choices=VALIDITY_CHOICES)

    brand = models.ManyToManyField(Brand)
    redeemableChannels = models.ManyToManyField(RedeemableChannel)

    minimumSpend = models.PositiveIntegerField(default=0)
    minimumSpendOn = models.CharField(default='all', max_length=999)

    typeId = models.CharField(default='', max_length=999)
    validPeriod = models.PositiveIntegerField(default=0)
    usagePerCustomer = models.PositiveIntegerField(default=0)

    description = models.TextField()
    code = models.CharField(default='', max_length=999)
    status = models.CharField(default='', max_length=999)

    startDate = models.DateTimeField()
    endDate = models.DateTimeField(null=True)

    terms = models.TextField(default='')


    # "usagePerCustomer": null,



class DealRestriction(models.Model):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='deal_restrictions')

    excluded_products = models.ManyToManyField(Product)
    excluded_services = models.ManyToManyField(Service)

    block_dates = models.ManyToManyField(DealDate)
    excluded_locations = models.ManyToManyField(BusinessAddress)


class DealDay(models.Model):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='deal_days')
    day = models.CharField(default='', max_length=999)

class DealDate(models.Model):
    date = models.DateTimeField()

class DealMedia(models.Model):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='deal_medias')
    file = models.FileField(upload_to='business/deals/images/')