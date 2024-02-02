from django.db import models

from uuid import uuid4
# Create your models here.


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

    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    title = models.CharField(default='', max_length=999)

    deal_type = models.CharField(default='', max_length=999, choices=DEAL_TYPE_CHOICES)


    # "categoryId": "A0AAB170418504922248",
    # "audience": "Public",
    # "codeGeneration": "generic",
    # "usageLimitType": "unlimited",
    # "usagePerCustomer": null,
    # "brandsIds": [
    #     "nstyle-uae",
    #     "uml-uae",
    #     "nstyle-bahrain",
    #     "nstyle-jordan",
    #     "home-service",
    #     "nstyle-canada",
    #     "training"
    # ],
    # "redeemableChannelIds": [
    #     "pos"
    # ],
    # "startDate": "2024-01-01 12:00:00",
    # "minimumSpendOn": "all",
    # "minimumSpend": 30,
    # "description": "Description 6",
    # "validPeriod": null,
    # "validityPeriodTypeId": "from-start-to-end-date",
    # "code": "EUVM",
    # "customerType": "Any",
    # "status": "Draft",
    # "dealId": "A0AAA170421554093919"
