from django.contrib.auth.models import User
from DealsBot.models import Profile, SentDeal, UserSentDeal, NotificationMethod
from django.core.exceptions import ObjectDoesNotExist


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
