from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import OTPCode
import pyotp


@receiver(post_save, sender=User)
def create_otp_for_new_user(sender, instance, created, **kwargs):
    if created:
        OTPCode.objects.create(
            user=instance,
            secret=pyotp.random_base32(),
        )
