from django.http import HttpResponse
from .tasks import fetch_weather


def trigger_fetch(request):
    # This is the "Place Order" tap:
    # .delay() drops the job into Redis and returns instantly.
    # The worker (delivery guy) picks it up and does the slow fetch later.
    fetch_weather.delay('London', 51.5, -0.1)
    return HttpResponse('Weather fetch handed to the background worker ✅')
