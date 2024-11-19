from django.contrib import admin
from .models import Profile, NotificationMethod, DealSubscription, SentDeal, UserSentDeal, BotUser


# Register your models here.


@admin.display(description="Communication")
def communication_channels_list(obj):
    return ", ".join([ch.display_text for ch in obj.communication_channels.all()])


class DealSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["profile", "product", "zipcode", "is_active", communication_channels_list]


class SentDealAdmin(admin.ModelAdmin):
    list_display = ("brand", "product", "advertiser", "price", "valid_from", "valid_thru")


class UserSentDealAdmin(admin.ModelAdmin):
    list_display = ("sent_deal", "profile", "date_sent", "notification_method")


admin.site.register(Profile)
admin.site.register(BotUser)
admin.site.register(NotificationMethod)
admin.site.register(DealSubscription, DealSubscriptionAdmin)
admin.site.register(SentDeal, SentDealAdmin)
admin.site.register(UserSentDeal, UserSentDealAdmin)
