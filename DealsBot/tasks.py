from celery import shared_task
from DealsBot.bot_functions import get_active_deal_subscriptions, filter_out_user_sent_deals
from DealsBot.api_utils import fetch_offers, parse_response
from .bot_functions.functions import send_deal
from .db_utils import save_user_telegram_chat_id
from .models import Profile
from .telegram_utils.telegram_functions import find_telegram_chat_ids


@shared_task
def check_for_deals_and_notify():
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
            print(e.args)
            pass

@shared_task
def obtain_and_save_telegram_chat_ids():
    telegram_user_names = Profile.objects.values_list("telegram_username", flat=True)
    telegram_user_names_list = list(telegram_user_names)

    found_telegram_chat_ids = find_telegram_chat_ids(telegram_user_names_list)

    for result in found_telegram_chat_ids:
        print(result["username"])
        save_user_telegram_chat_id(result["username"], result["chat_id"])
