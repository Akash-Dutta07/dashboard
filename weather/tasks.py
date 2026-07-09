import httpx
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.core.cache import cache
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

    # Fresh data just landed → the dashboard's sticky note is now stale.
    # Tear it off so the next page-load rebuilds it from the new rows.
    cache.delete('dashboard_data')

    # bulk_create skips post_save, so the alert signal never fires here.
    # Do the "is it hot?" check explicitly, where the batch happens.
    hot = [r for r in readings if r.temperature > 40]
    if hot:
        peak = max(hot, key=lambda r: r.temperature)
        send_mail(
            subject=f"Heat alert: {city}",
            message=(
                f"{len(hot)} reading(s) over 40°C for {city}. "
                f"Peak {peak.temperature}°C at {peak.recorded_at}."
            ),
            from_email="alerts@dashboard.com",
            recipient_list=["admin@dashboard.com"],
        )

    return f"Fetched {len(readings)} readings for {city}"
