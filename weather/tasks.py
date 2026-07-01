import httpx
from celery import shared_task
from django.utils import timezone
from .models import WeatherReading


@shared_task
def fetch_weather(city, latitude, longitude):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        f"&hourly=temperature_2m&forecast_days=1"
    )
    response = httpx.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    readings = [
        WeatherReading(
            city=city,
            latitude=latitude,
            longitude=longitude,
            temperature=temp,
            recorded_at=timezone.datetime.fromisoformat(time_str),
        )
        for time_str, temp in zip(data["hourly"]["time"], data["hourly"]["temperature_2m"])
    ]

    WeatherReading.objects.bulk_create(readings, ignore_conflicts=True)
    return f"Fetched {len(readings)} readings for {city}"
