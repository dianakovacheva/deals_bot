import time
from datetime import datetime

from celery import shared_task
from django.core.mail import send_mail
import requests
# from .models import DealSubscription


@shared_task
def get_time():
    now = datetime.now()
    print(now.strftime("%H:%M:%S"))


