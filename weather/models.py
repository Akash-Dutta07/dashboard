from django.db import models
from django.contrib.auth.models import User
import pyotp

# Create your models here.
class WeatherReading(models.Model):
    city = models.CharField(max_length=100)   # "London"
    latitude = models.FloatField()            # 51.5
    longitude = models.FloatField()           # -0.1
    temperature = models.FloatField()         # 14.2  (°C)
    recorded_at = models.DateTimeField()      # WHEN the weather happened
    fetched_at = models.DateTimeField(auto_now_add=True)  # WHEN we saved it
  
  
    def __str__(self):
        return f"{self.city} — {self.temperature}°C at {self.recorded_at}"

    class Meta:
        ordering = ['-recorded_at']
        indexes = [models.Index(fields=['city', 'recorded_at'])]


class OTPCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='otp')
    secret = models.CharField(max_length=64)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_otp(self):
        totp = pyotp.TOTP(self.secret, interval=300)  # code valid for 5 min
        return totp.now()

    def verify_otp(self, code):
        totp = pyotp.TOTP(self.secret, interval=300)
        return totp.verify(code)

    def __str__(self):
        return f"OTP for {self.user.username}"