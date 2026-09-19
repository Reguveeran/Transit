from django.urls import path
from apps.analytics.views import VehicleAnalyticsView, DelayAnalyticsView

urlpatterns = [
    path("vehicles/", VehicleAnalyticsView.as_view(), name="analytics-vehicles"),
    path("delays/", DelayAnalyticsView.as_view(), name="analytics-delays"),
]
