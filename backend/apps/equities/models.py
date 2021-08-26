from django.db import models
from datetime import date
from django.utils import timezone
from djongo import models as djongo_models

# Create your models here.
class TickData(models.Model):
    timestamp = models.DateTimeField(default=timezone.now())
    p_mkt = models.FloatField()
    class Meta:
        abstract = True


class Equity(models.Model):
    date_time = models.DateTimeField(default=timezone.now())
    md_date = models.DateField(default=date.fromisoformat('1900-01-01'))
    label = models.CharField(max_length=20)
    description = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    country = models.CharField(max_length=50)
    currency = models.CharField(max_length=5)
    market = models.CharField(max_length=50)
    exchange = models.CharField(max_length=20)
    market_cap = models.DecimalField(max_digits=22, decimal_places=6)
    p_high = models.DecimalField(max_digits=16, decimal_places=6)
    p_close = models.DecimalField(max_digits=16, decimal_places=6)
    p_low = models.DecimalField(max_digits=16, decimal_places=6)
    p_open = models.DecimalField(max_digits=16, decimal_places=6)

    tickdata = djongo_models.ArrayField(
        model_container=TickData
    )

    constraints = [
        models.UniqueConstraint(fields=['label', 'md_date'], name='unique_label_md_date')
    ]

    def __str__(self):
        return self.label
