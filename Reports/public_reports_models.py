

from django.db import models

from uuid import uuid4
class SaleReport(models.Model):
    SALE_TYPE_CHOICES = (
        ('Service', 'Service'),
        ('Product', 'Product'),
    )
    unique_id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)

    instance_id = models.CharField(max_length=999, default='')
    sale_type = models.CharField(choices=SALE_TYPE_CHOICES, default='Service', max_length=999)
    name = models.CharField(default='', max_length=999)
    total_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.unique_id}'