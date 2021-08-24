from django.db import models
from apps.equities.models import Equity
from datetime import date

# Create your models here.
class Dividend(models.Model):
    year = models.CharField(max_length=4)
    date_time = models.DateTimeField(auto_now_add=True)
    ex_div_date = models.DateField(default=date.fromisoformat('1900-01-01'))
    dividend = models.DecimalField(max_digits=20, decimal_places=10)
    equity = models.ForeignKey(
        Equity,
        on_delete = models.CASCADE
    )

    def __str__(self):
        return self.ex_div_date
