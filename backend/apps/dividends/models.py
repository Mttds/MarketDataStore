from django.db import models
from django import forms
from djongo import models as djongo_models
from apps.equities.models import Equity
from datetime import date, datetime

# Create your models here.
class DividendList(djongo_models.Model):
    ex_div_date = models.DateField(default=date.fromisoformat('1900-01-01'))
    # DecimalField used in djongo models ArrayField will actually
    # return a conversion error from MongoDB's Decimal128 to Django's Decimal
    # TypeError: conversion from Decimal128 to Decimal is not supported
    # this does not happen for DecimalFields in the Equity model for example
    # even if they get stored as Decimal128 by MongoDB, but then the serialization
    # with the rest_framework library works without returning the conversion error
    # hence the problem seems related to djongo_models.ArrayField
    #dividend = models.DecimalField(max_digits=16, decimal_places=6)
    dividend = models.FloatField()

    # never instantiated and cannot have as a serializer
    # created just to be embedded as a structure inside ArrayField
    # in order to have multiple ex_div_date/dividend tuples in our
    # Dividend object/document
    class Meta:
        abstract = True

class DividendListForm(forms.ModelForm):
    class Meta:
        model = DividendList
        fields = (
            'ex_div_date',
            'dividend'
        )

class Dividend(models.Model):
    year = models.CharField(max_length=4)
    date_time = models.DateTimeField(auto_now_add=True)
    
    equity = models.ForeignKey(
        Equity,
        on_delete = models.CASCADE
    )

    dividends = djongo_models.ArrayField(
        model_container=DividendList,
        model_form_class=DividendListForm
    )

    #objects = djongo_models.DjongoManager()

    def __str__(self):
        return self.equity
