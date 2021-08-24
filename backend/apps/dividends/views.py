from django.shortcuts import render
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response
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

    # override ModelViewSet list method
    def list(self, request):
        queryset = self.queryset
        serializer = DividendSerializer(queryset, many=True)
        print("DividendsViewSet list method", serializer.data)
        return Response(serializer.data)