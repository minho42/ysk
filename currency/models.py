from django.db import models
from ysk.models import TimeStampedModel


class Currency(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True)
    rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fee = models.DecimalField(max_digits=4, decimal_places=2, default=0, null=True)
    real_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    url = models.CharField(max_length=400)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-real_rate", "name"]
        verbose_name_plural = "Currencies"
