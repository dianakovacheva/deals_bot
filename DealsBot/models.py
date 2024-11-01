import django.contrib.auth.models
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.deletion import ProtectedError


# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram = models.CharField(max_length=64, blank=True)

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
