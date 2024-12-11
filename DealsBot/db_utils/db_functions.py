from django.contrib.auth.models import User
from DealsBot.models import Profile, SentDeal, UserSentDeal, NotificationMethod, DealSubscription, TelegramUser
from django.core.exceptions import ObjectDoesNotExist


def create_telegram_user(username, user_id, user_first_name, user_last_name, chat_id):
    if user_id is None:
        raise ValueError("user_id is required.")

    if chat_id is None:
        raise ValueError("chat_id is required.")

    args = {"user_id": user_id, "chat_id": chat_id}

    if username is not None:
        args["username"] = username
    if user_first_name is not None:
        args["user_first_name"] = user_first_name
    if user_last_name is not None:
        args["user_last_name"] = user_last_name

    created_telegram_user = TelegramUser.objects.create(**args)

    return created_telegram_user


def create_deal(product, zipcode, communication_channels: str | list, profile=None):
    if profile is None:
        raise ValueError("Profile must be passed to the function.")

    try:
        if isinstance(communication_channels, str):
            communication_channels = [communication_channels]

        communication_channels_records = NotificationMethod.objects.filter(type__in=communication_channels)

        args = dict()
        args["profile"] = profile
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
