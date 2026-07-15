from django.core.management.base import BaseCommand
from weather.tasks import fetch_weather


class Command(BaseCommand):
    help = 'Fetch weather data for all cities'

    def handle(self, *args, **kwargs):
        # The list of cities we want weather for.
        cities = [
            ('London', 51.5, -0.1),
            ('New York', 40.7, -74.0),
            ('Tokyo', 35.7, 139.7),
        ]

        # For each city, hand the fetch job to the background worker.
        for city, lat, lon in cities:
            fetch_weather.delay(city, lat, lon)
            self.stdout.write(f'Queued fetch for {city}')
