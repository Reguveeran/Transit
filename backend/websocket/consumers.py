"""
UniTransit - Real-Time WebSocket Consumers
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger("unitransit.websocket")


class VehicleTrackingConsumer(AsyncWebsocketConsumer):
    """Broadcasts all vehicle position telemetry to connected clients."""

    async def connect(self):
        self.group_name = "vehicle_updates"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f"WebSocket client connected to {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(f"WebSocket client disconnected from {self.group_name}")

    async def vehicle_update(self, event):
        """Handler for 'vehicle.update' group messages."""
        await self.send(text_data=json.dumps(event.get("data", event)))


class RouteTrackingConsumer(AsyncWebsocketConsumer):
    """Streams live telemetry filtered for a specific transit route."""

    async def connect(self):
        self.route_id = self.scope["url_route"]["kwargs"]["route_id"]
        self.group_name = f"route_{self.route_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def route_update(self, event):
        await self.send(text_data=json.dumps(event.get("data", event)))


class AlertsConsumer(AsyncWebsocketConsumer):
    """Streams real-time system and vehicle operational alerts."""

    async def connect(self):
        self.group_name = "alerts"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def alert_notification(self, event):
        await self.send(text_data=json.dumps(event.get("data", event)))
