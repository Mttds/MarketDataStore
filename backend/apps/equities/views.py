from django.shortcuts import render
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import viewsets
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Equity
from apps.dividends.models import Dividend
from apps.dividends.views import DividendSerializer

class EquitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Equity
        fields = '__all__'

# Create your views here.
class EquitiesViewSet(viewsets.ModelViewSet):
    serializer_class = EquitySerializer
    queryset = Equity.objects.all()

    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ('label','md_date')
    search_fields = ('label','md_date')
    ordering = ('md_date')

class EquityDividendsViewSet(viewsets.ModelViewSet):
    serializer_class = DividendSerializer
    queryset = Dividend.objects.all()

    # override method of ModelViewSet
    def list(self, request, equity_pk):
        dividends = Dividend.objects.filter(equity = equity_pk)
        serializer = self.get_serializer(dividends, many=True)
        return Response(serializer.data)