from django.db import models

from uuid import uuid4
from Product.models import Category, Brand
# Create your models here.


class DealCategory(models.Model):
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
        ('Public', 'public'),
        ('Pre Set Customer', 'pre-set-users'),
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
        ("From deal start date to end date" , "from-start-to-end-date"),
        ("Days from deal activation date" , "days-from-start-date"),
        ("Months from deal activation date" , "months-from-start-date"),
        ("Years from deal activation date" , "years-from-start-date"),
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

    minimumSpend = models.PositiveIntegerField(default=0)

    description = models.TextField()
    code = models.CharField(default='', max_length=999)
    status = models.CharField(default='', max_length=999)

    startDate = models.DateTimeField()
    endDate = models.DateTimeField()

    # "usagePerCustomer": null,
    # "redeemableChannelIds": [
    #     "pos"
    # ],
    # "minimumSpendOn": "all",
