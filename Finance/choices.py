from django.db import models

class RefundChoices(models.TextChoices):
        CREDIT_REFUND = 'credit_refund', 'Credit Refund'
        CASH_REFUND = 'cash_refund', 'Cash Refund'
        