from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
import pyotp
from .models import OTPCode, WeatherReading
from django.core.mail import send_mail


@receiver(post_save, sender=User)
def create_otp_for_new_user(sender, instance, created, **kwargs):
    if created:
        OTPCode.objects.create(
            user=instance,
            secret=pyotp.random_base32(),
        )

@receiver(post_save, sender=WeatherReading)
def alert_on_extreme_temperature(sender, instance, created, **kwargs):
    if created and instance.temperature > 40:
        send_mail(
            subject=f"Heat alert: {instance.city}",
            message=f"{instance.city} hit {instance.temperature}°C",
            from_email="alerts@dashboard.com",
            recipient_list=["admin@dashboard.com"],
        )