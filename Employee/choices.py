from django.db import models

class Status(models.TextChoices):
        CANCEL = 'Cancel', 'Cancel'
        ACCEPT = 'Accept', 'Accept'
        REJECT = 'Reject', 'Reject'
        PENDING = 'Pending', 'Pending'
        

class Skills(models.TextChoices):
        HAIR = 'Hair Cutting ', 'Hair Cutting '
        COLORING = 'Hair Coloring', 'Hair Coloring'
        WAXING = 'Waxing', 'Waxing'
        THREADING = 'Threading', 'Threading'
        FACIAL = 'Facial', 'Facial'
        MAKEUP = 'Makeup', 'Makeup'
        SKIN = 'Skin Care', 'Skin Care'
