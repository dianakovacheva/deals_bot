import threading

from celery import shared_task
from celery.signals import worker_ready

from DealsBot.api_utils import fetch_offers, parse_response
from DealsBot.bot_functions import get_active_deal_subscriptions, filter_out_user_sent_deals
from .bot_functions.functions import send_deal
from .db_utils import save_user_telegram_chat_id
from .models import Profile
from .telegram_utils.telegram_functions import find_telegram_chat_ids
from .messanger_bots.telegram_bot import run_telegram_bot


@shared_task
def check_for_deals_and_notify():
    print('Starting "check_for_deals_and_notify..."')
    active_subscriptions = get_active_deal_subscriptions()
    unfiltered_list = []

    for subscription in active_subscriptions:
        res = parse_response(fetch_offers(subscription.product, subscription.zipcode))
        unfiltered_list.append({
            "dealSubscriptionId": subscription.id,
            "userId": subscription.profile.id,
            "results": res["results"]
        })

    filtered_list = filter_out_user_sent_deals(unfiltered_list)

    for deal in filtered_list:
        try:
            send_deal(deal)
        except Exception as e:
            print(e)



def obtain_and_save_telegram_chat_ids():
    telegram_user_names = Profile.objects.values_list("telegram_username", flat=True)
    telegram_user_names_list = list(telegram_user_names)

    found_telegram_chat_ids = find_telegram_chat_ids(telegram_user_names_list)

    for result in found_telegram_chat_ids:
        print(result["username"])
        save_user_telegram_chat_id(result["username"], result["chat_id"])

@shared_task(queue='telegram_bot')
def run_telegram_bot_task():
    run_telegram_bot()

@worker_ready.connect
def run_telegram_bot_celery_task(**kwargs):
    # Trigger the task in the 'telegram_bot' queue
    run_telegram_bot_task.apply_async()
