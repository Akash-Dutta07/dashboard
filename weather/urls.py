from django.urls import path
from . import views

urlpatterns = [
    # Homepage '/' → the dashboard page (draws from the DB "tank").
    path('', views.dashboard, name='dashboard'),
    # Visiting /fetch/ runs trigger_fetch, which drops the job into Redis.
    path('fetch/', views.trigger_fetch, name='trigger_fetch'),
    # The numbers-only address: returns raw temperature data for the chart.
    path('api/chart-data/', views.WeatherChartData.as_view(), name='chart_data'),
]
