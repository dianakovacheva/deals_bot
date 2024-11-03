import django.contrib.auth.models
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.deletion import ProtectedError


# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_username = models.CharField(max_length=64, blank=True, unique=True)
    telegram_chat_id = models.IntegerField(default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.user.email})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class NotificationMethod(models.Model):
    type = models.CharField(max_length=15, primary_key=True)
    display_text = models.CharField(max_length=64)

    def __str__(self):
        return self.display_text

    def delete(self, *args, **kwargs):
        if self.dealsubscription_set.exists():
            raise ProtectedError("Cannot delete NotificationMethod because it is in use.", self)
        super().delete(*args, **kwargs)


class DealSubscription(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="subscriptions")
    product = models.CharField(max_length=64)
    zipcode = models.CharField(max_length=8)
    communication_channels = models.ManyToManyField(NotificationMethod)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return (f"{self.profile.user.username} -> {self.product} -> {self.zipcode} -> "
                f"{'Active' if self.is_active else 'Inactive'}")


class SentDeal(models.Model):
    id = models.BigIntegerField(primary_key=True, null=False)
    brand = models.CharField(max_length=64)
    product = models.CharField(max_length=64)
    advertiser = models.CharField(max_length=64)
    category = models.CharField(max_length=64)
    description = models.TextField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    reference_price = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_thru = models.DateTimeField()
    requires_loyalty_membership = models.BooleanField()
    unit = models.CharField(max_length=64)


class UserSentDeal(models.Model):
    sent_deal = models.ForeignKey(SentDeal, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date_sent = models.DateTimeField(auto_now_add=True)
    notification_method = models.ForeignKey(NotificationMethod, on_delete=models.SET(None))

    class Meta:
        unique_together = ("sent_deal", "profile", "notification_method")


SentDeal.sent_to = models.ManyToManyField(Profile, through=UserSentDeal, related_name="sent_deals")