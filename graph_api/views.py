from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.http import JsonResponse

class HiView(APIView):
    def get(self, request, format=None):
        data = {'message': 'Hi'}
        return JsonResponse(data)

 