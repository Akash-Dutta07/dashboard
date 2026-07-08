from django.http import HttpResponse
from django.shortcuts import render
from .models import WeatherReading
from .tasks import fetch_weather


def dashboard(request):
    # The "tap that draws from the tank" — reads OUR database, never the API.
    # ── Step 1: get the data ──
    latest = WeatherReading.objects.order_by('-recorded_at').first()   # headline (1 row)
    readings = WeatherReading.objects.order_by('-recorded_at')[:24]    # table (24 rows)

    # ── Step 2: pack the bag (context) ──
    context = {
        'latest': latest,
        'readings': readings,
    }

    # ── Step 3: render ──
    return render(request, 'weather/dashboard.html', context)


def trigger_fetch(request):
    # This is the "Place Order" tap:
    # .delay() drops the job into Redis and returns instantly.
    # The worker (delivery guy) picks it up and does the slow fetch later.
    fetch_weather.delay('London', 51.5, -0.1)
    return HttpResponse('Weather fetch handed to the background worker ✅')
