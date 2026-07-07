from django.urls import path
from . import views

urlpatterns = [
    # Visiting /fetch/ runs trigger_fetch, which drops the job into Redis.
    path('fetch/', views.trigger_fetch, name='trigger_fetch'),
]
