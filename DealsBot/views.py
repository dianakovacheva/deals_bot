from django.http import HttpResponse
from django.shortcuts import render

from DealsBot.tasks import check_for_deals_and_notify


# Create your views here.

def index(request):
    check_for_deals_and_notify()

    return HttpResponse("Function called.")
