from django.contrib import admin
from .models import WeatherReading, OTPCode

# Register your models here.

@admin.register(WeatherReading)
class WeatherReadingAdmin(admin.ModelAdmin):
    list_display = ['city', 'temperature', 'recorded_at', 'fetched_at']
    list_filter = ['city']
    search_fields = ['city']
    date_hierarchy = 'recorded_at'
    ordering = ['-recorded_at']


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_verified', 'created_at']
    list_filter = ['is_verified']
    search_fields = ['user__username']