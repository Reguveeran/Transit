"""
UniTransit - WebSocket URL Patterns
"""

from django.urls import re_path
from websocket.consumers import (
    VehicleTrackingConsumer,
    RouteTrackingConsumer,
    AlertsConsumer,
)

websocket_urlpatterns = [
    re_path(r"^ws/vehicles/?$", VehicleTrackingConsumer.as_asgi()),
    re_path(r"^ws/routes/(?P<route_id>[\w-]+)/?$", RouteTrackingConsumer.as_asgi()),
    re_path(r"^ws/alerts/?$", AlertsConsumer.as_asgi()),
]
