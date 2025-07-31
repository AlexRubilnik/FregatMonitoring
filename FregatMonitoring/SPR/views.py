from django.shortcuts import render

from django.http import HttpResponse
from .models import Equipment


def index(request):
    eqp = Equipment.objects.all()
    return HttpResponse(f"{eqp[0].name}")
