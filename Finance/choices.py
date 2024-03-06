from django.db import models

class RefundChoices(models.TextChoices):
        CREDIT_REFUND = 'Credit Refund', 'Credit Refund'
        CASH_REFUND = 'Cash Refund', 'Cash Refund'
        