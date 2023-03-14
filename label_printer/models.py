from django.db import models


class Label(models.Model):
    text = models.CharField(max_length=100)
    barcode = models.CharField(max_length=16)
    quantity = models.IntegerField(default=1)
    date = models.BooleanField(default=True)
