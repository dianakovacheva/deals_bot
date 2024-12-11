from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.deletion import ProtectedError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Profile(models.Model):
    profile_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    profile_object = GenericForeignKey('profile_type', 'id')
    joined_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile linked to {self.profile_object}"


class TelegramUser(models.Model):
    username = models.CharField(max_length=64, blank=True, unique=True)
    user_id = models.IntegerField(null=True, blank=True, unique=True)
    user_first_name = models.CharField(default=None, max_length=64, null=True, blank=True)
    user_last_name = models.CharField(default=None, max_length=64, null=True, blank=True)
    chat_id = models.IntegerField()
    joined_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Telegram User: {self.username or 'Anonymous'} ({self.chat_id})"


class DjangoUserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    joined_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Django User: {self.user.username}"


class NotificationMethod(models.Model):
    type = models.CharField(max_length=15, primary_key=True)
    display_text = models.CharField(max_length=64)

    def __str__(self):
        return self.display_text

    def delete(self, *args, **kwargs):
        if self.dealsubscription_set.exists():
            raise ProtectedError("Cannot delete NotificationMethod because it is in use.", self)
        super().delete(*args, **kwargs)


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


class DealSubscription(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="subscriptions")
    product = models.CharField(max_length=64)
    zipcode = models.CharField(max_length=8)
    communication_channels = models.ManyToManyField(NotificationMethod)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return f"Profile {self.profile} -> {self.product} -> {self.zipcode} -> {'Active' if self.is_active else 'Inactive'}"


class UserSentDeal(models.Model):
    sent_deal = models.ForeignKey(SentDeal, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date_sent = models.DateTimeField(auto_now_add=True)
    notification_method = models.ForeignKey(NotificationMethod, on_delete=models.SET(None))

    class Meta:
        unique_together = ("sent_deal", "profile", "notification_method")


SentDeal.sent_to = models.ManyToManyField(Profile, through=UserSentDeal, related_name="sent_deals")


# Signal to create a Profile when a TelegramUser is created
@receiver(post_save, sender=TelegramUser)
def create_profile_for_telegram_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(profile_type=ContentType.objects.get_for_model(instance), id=instance.id)


# Signal to create a Profile when a DjangoUserProfile is created
@receiver(post_save, sender=DjangoUserProfile)
def create_profile_for_django_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(profile_type=ContentType.objects.get_for_model(instance), id=instance.id)


# Signal to delete a Profile when a TelegramUser is deleted
@receiver(post_delete, sender=TelegramUser)
def delete_profile_for_telegram_user(sender, instance, **kwargs):
    Profile.objects.filter(
        profile_type=ContentType.objects.get_for_model(instance),
        id=instance.id
    ).delete()


# Signal to delete a Profile when a DjangoUserProfile is deleted
@receiver(post_delete, sender=DjangoUserProfile)
def delete_profile_for_django_user(sender, instance, **kwargs):
    Profile.objects.filter(
        profile_type=ContentType.objects.get_for_model(instance),
        id=instance.id
    ).delete()
