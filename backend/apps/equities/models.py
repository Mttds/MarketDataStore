from django.db import models
from datetime import date

# Create your models here.
class Equity(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)
    md_date = models.DateField(default=date.fromisoformat('1900-01-01'))
    label = models.CharField(max_length=20)
    description = models.CharField(max_length=255)
    p_high = models.DecimalField(max_digits=16, decimal_places=6)
    p_close = models.DecimalField(max_digits=16, decimal_places=6)
    p_low = models.DecimalField(max_digits=16, decimal_places=6)
    p_open = models.DecimalField(max_digits=16, decimal_places=6)

    def __str__(self):
        return self.label
