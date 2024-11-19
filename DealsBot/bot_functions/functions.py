from django.core.mail import send_mail
from django.db import IntegrityError

from DealsBot.db_utils.db_functions import save_sent_deal, save_user_sent_deal
from DealsBot.models import DealSubscription, UserSentDeal, User, Profile, SentDeal
from DealsBot.telegram_utils.telegram_functions import get_telegram_chat_id, \
    send_telegram_message


def get_active_deal_subscriptions():
    active_deals = DealSubscription.objects.filter(is_active=True)
    return active_deals


def filter_out_user_sent_deals(unfiltered_list):
    filtered_list = []

    for subscription in unfiltered_list:
        not_sent_deals = []
        for result in subscription["results"]:
            sent_deal = UserSentDeal.objects.filter(sent_deal=result["id"], profile=subscription["userId"])
            if len(sent_deal) == 0:
                not_sent_deals.append(result)
        if len(not_sent_deals) != 0:
            filtered_list.append({
                "dealSubscriptionId": subscription["dealSubscriptionId"],
                "userId": subscription["userId"],
                "results": not_sent_deals
            })

    return filtered_list


def prepare_telegram_message(deal=None, search_params: dict = None):
    if "dealSubscriptionId" not in deal:
        message = f"<b>Deals found for</b> <i>{search_params["product"]}</i> <b>in</b> <u>{search_params["zipcode"]}</u>\n\n"
    else:
        deal_subscription = DealSubscription.objects.get(id=deal["dealSubscriptionId"])
        message = f"<b>Deals found for</b> <i>{deal_subscription.product}</i> <b>in</b> <u>{deal_subscription.zipcode}</u>\n\n"

    for result in deal["results"]:
        brand = result['brand']
        product = result['product']
        description = result['description']
        price = result['price']
        advertiser = result['advertiser']
        start_date = result['validityDates'][0]['from'].strftime('%d.%m.%Y')
        end_date = result['validityDates'][0]['to'].strftime('%d.%m.%Y')

        message += (
            f"<b>{brand} {product}</b>\n"
            f"{description}\n"
            f"<b>Price:</b> <u>€{price}</u>\n"
            f"<b>Store:</b> <i>{advertiser}</i>\n"
            f"<b>Valid:</b> <u>{start_date}</u> <b>to</b> <u>{end_date}</u>\n\n"
        )

        if result['requiresLoyaltyMembership']:
            message += "<i>Membership required</i>"

    return message


def send_deal_per_email(deal):
    user = User.objects.get(id=deal["userId"])
    deal_subscription = DealSubscription.objects.get(id=deal["dealSubscriptionId"])
    user_email = user.email
    send_mail(
        subject="New Deals Available!",
        message=f"Deals found for {deal_subscription.product} in {deal_subscription.zipcode}",
        from_email="no-reply@yourapp.com",
        recipient_list=[user_email],
    )


def send_deal(deal):
    profile = Profile.objects.get(id=deal["userId"])
    deal_subscription = DealSubscription.objects.get(id=deal["dealSubscriptionId"])
    communication_channels = deal_subscription.communication_channels.values()

    sent_deals = list()
    for result in deal["results"]:
        try:
            sent_deals.append(save_sent_deal(result))
        except IntegrityError:
            print("Deal already in the database.")
            existing_deal = SentDeal.objects.get(id=result["id"])
            sent_deals.append(existing_deal)

    for channel in communication_channels:
        if channel["type"] == "telegram":
            send_deal_per_telegram(deal, profile)
            for sent_deal in sent_deals:
                save_user_sent_deal(sent_deal, profile, channel["type"])

        if channel["type"] == "email":
            pass
            # send_deal_per_email(deal)


def send_deal_per_telegram(deal, profile):
    user_telegram_username = profile.telegram_username
    found_chat_id = get_telegram_chat_id(user_telegram_username)
    print(found_chat_id)
    if found_chat_id != -1:
        formatted_message = prepare_telegram_message(deal)
        send_telegram_message(found_chat_id, formatted_message)
