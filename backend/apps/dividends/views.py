from django.shortcuts import render
from rest_framework import serializers
from rest_framework import viewsets
from .models import Dividend

# Create your views here.
class DividendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dividend
        fields = '__all__'

class DividendsViewSet(viewsets.ModelViewSet):
    serializer_class = DividendSerializer
    queryset = Dividend.objects.all()