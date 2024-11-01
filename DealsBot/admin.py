from django.contrib import admin
from .models import Profile, NotificationMethod, DealSubscription


# Register your models here.


@admin.display(description="Communication")
def communication_channels_list(obj):
    return ", ".join([ch.display_text for ch in obj.communication_channels.all()])


class DealSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["profile", "product", "zipcode", "is_active", communication_channels_list]


admin.site.register(Profile)
admin.site.register(NotificationMethod)
admin.site.register(DealSubscription, DealSubscriptionAdmin)
