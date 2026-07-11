from django.urls import path
from . import views

urlpatterns = [
    # Homepage '/' → the dashboard page (draws from the DB "tank").
    path('', views.dashboard, name='dashboard'),
    # Visiting /fetch/ runs trigger_fetch, which drops the job into Redis.
    path('fetch/', views.trigger_fetch, name='trigger_fetch'),
    # The numbers-only address: returns raw temperature data for the chart.
    path('api/chart-data/', views.WeatherChartData.as_view(), name='chart_data'),
    # Visiting /otp/send/ generates a code and emails (prints) it.
    path('otp/send/', views.send_otp, name='send_otp'),
    # /otp/verify/ shows the code box and checks what's typed.
    path('otp/verify/', views.verify_otp, name='verify_otp'),
]
