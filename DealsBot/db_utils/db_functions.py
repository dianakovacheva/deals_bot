from django.contrib.auth.models import User
from DealsBot.models import Profile, SentDeal, UserSentDeal, NotificationMethod, DealSubscription, BotUser
from django.core.exceptions import ObjectDoesNotExist


def create_bot_user(telegram_username, telegram_user_id, telegram_user_first_name, telegram_user_last_name, telegram_chat_id):
    if telegram_user_id is None:
        raise ValueError("telegram_user_id is required.")

    if telegram_chat_id is None:
        raise ValueError("telegram_chat_id is required.")

    args = {"telegram_user_id": telegram_user_id, "telegram_chat_id": telegram_chat_id}

    if telegram_username is not None:
        args["telegram_username"] = telegram_username
    if telegram_user_first_name is not None:
        args["telegram_user_first_name"] = telegram_user_first_name
    if telegram_user_last_name is not None:
        args["telegram_user_last_name"] = telegram_user_last_name

    created_bot_user = BotUser.objects.create(**args)

    return created_bot_user


def create_deal(product, zipcode, communication_channels: str | list, profile=None, bot_user=None):
    if profile is None and bot_user is None:
        raise ValueError("Either profile or bot_user must be passed to the function.")

    try:
        if isinstance(communication_channels, str):
            communication_channels = [communication_channels]

        communication_channels_records = NotificationMethod.objects.filter(type__in=communication_channels)

        args = dict()
        if profile is not None:
            args["profile"] = profile
        else:
            args["bot_user"] = bot_user

        args["product"] = product
        args["zipcode"] = zipcode

        created_deal_data = DealSubscription.objects.create(**args)

        created_deal_data.communication_channels.set(communication_channels_records)
        created_deal_data.save()

        return created_deal_data

    except:
        return None


def save_user_telegram_chat_id(telegram_username, chat_id: int):
    try:
        # Fetch the User object based on the ID
        profile = Profile.objects.get(telegram_username=telegram_username)
    except ObjectDoesNotExist:
        print("Profile with the provided telegram username does not exist.")
        return

    profile.telegram_chat_id = chat_id
    profile.save()

    print("Telegram chat ID saved successfully.")


def save_sent_deal(deal):
    sent_deal = SentDeal.objects.create(id=deal["id"], brand=deal["brand"], advertiser=deal["advertiser"],
                                        category=deal["category"], description=deal["description"], price=deal["price"],
                                        reference_price=deal["referencePrice"],
                                        valid_from=deal["validityDates"][0]["from"],
                                        valid_thru=deal["validityDates"][0]["to"],
                                        requires_loyalty_membership=deal["requiresLoyaltyMembership"],
                                        product=deal["product"], unit=deal["unit"])

    return sent_deal


def save_user_sent_deal(deal, profile, notification_method_type):
    notification_method = NotificationMethod.objects.get(type=notification_method_type)
    user_sent_deal = UserSentDeal.objects.create(sent_deal=deal, profile=profile,
                                                 notification_method=notification_method)
