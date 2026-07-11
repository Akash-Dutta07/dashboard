from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import WeatherReading
from .forms import OTPVerifyForm
from .tasks import fetch_weather


def dashboard(request):
    # The "tap that draws from the tank" — reads OUR database, never the API.

    # ── Step 1: glance at the sticky note (cache) ──
    context = cache.get('dashboard_data')

    if context is None:
        # ── MISS: note is blank → walk to the kitchen (real DB queries) ──
        latest = WeatherReading.objects.order_by('-recorded_at').first()   # headline (1 row)
        readings = list(WeatherReading.objects.order_by('-recorded_at')[:24])  # table (24 rows)

        context = {
            'latest': latest,
            'readings': readings,
        }

        # ── Write the note so the next visitors skip the walk (5 min) ──
        cache.set('dashboard_data', context, 300)

    # ── Step 2: render — from the note OR fresh ──
    return render(request, 'weather/dashboard.html', context)


class WeatherChartData(APIView):
    # The "numbers-only address." No page — just data for the chart.

    def get(self, request):
        # ── Step 1: glance at THIS chart's own sticky note ──
        data = cache.get('weather_London_24h')

        if data is None:
            # ── MISS: build the numbers from the DB ──
            since = timezone.now() - timedelta(hours=24)
            readings = (
                WeatherReading.objects
                .filter(city='London', recorded_at__gte=since)
                .order_by('recorded_at')          # oldest → newest, so the line reads left→right
                .values('recorded_at', 'temperature')   # keep ONLY these two columns
            )
            data = list(readings)                  # force the promise into concrete rows

            # ── Write the note (5 min) ──
            cache.set('weather_London_24h', data, 300)

        # ── Step 2: hand back plain numbers ──
        return Response(data)


@login_required
def send_otp(request):
    # ── Step 1: grab THIS user's OTP record (auto-made by the signal at signup) ──
    otp_record = request.user.otp        # via OneToOneField related_name='otp'

    # ── Step 2: make a fresh 6-digit code from the model method ──
    code = otp_record.generate_otp()

    # ── Step 3: email it. On console backend, this PRINTS in your terminal. ──
    send_mail(
        subject='Your Dashboard Verification Code',
        message=f'Your OTP code is: {code}\n\nValid for 5 minutes.',
        from_email='noreply@dashboard.com',
        recipient_list=[request.user.email],
    )

    # ── Step 4: tell the user, then show the "we sent it" page ──
    messages.info(request, f'OTP sent to {request.user.email}')
    return render(request, 'weather/otp_sent.html')


@login_required
def verify_otp(request):
    if request.method == 'POST':
        # ── User submitted the code → check it ──
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            otp_record = request.user.otp

            if otp_record.verify_otp(code):
                # ── Correct code → mark them verified ──
                otp_record.is_verified = True
                otp_record.save()
                messages.success(request, 'Email verified successfully!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid or expired code. Try again.')
    else:
        # ── First visit (GET) → show a blank box ──
        form = OTPVerifyForm()

    return render(request, 'weather/verify_email.html', {'form': form})


def trigger_fetch(request):
    # This is the "Place Order" tap:
    # .delay() drops the job into Redis and returns instantly.
    # The worker (delivery guy) picks it up and does the slow fetch later.
    fetch_weather.delay('London', 51.5, -0.1)
    return HttpResponse('Weather fetch handed to the background worker ✅')
