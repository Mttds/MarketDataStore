from django.shortcuts import render
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import viewsets
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter
from .models import Dividend, DividendList

class DividendSerializer(serializers.ModelSerializer):
    #dividend_list = DividendList()
    class Meta:
        model = Dividend
        fields = '__all__'

    # override method of ModelSerializer
    def create(self, data):
        print("DividendSerializer create method",data)
        dividend_instance = Dividend.objects.create(**data)
        return dividend_instance

class DividendsViewSet(viewsets.ModelViewSet):
    serializer_class = DividendSerializer
    queryset = Dividend.objects.all()
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('equity', 'year')
    ordering = ('year')
