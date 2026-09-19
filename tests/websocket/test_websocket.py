import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.test import TestCase
from channels.testing import WebsocketCommunicator
from core.asgi import application


class WebSocketConsumerTests(TestCase):
    async def test_vehicle_tracking_websocket_connection(self):
        communicator = WebsocketCommunicator(application, "/ws/vehicles/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Broadcast test message via channel layer
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "vehicle_updates",
            {
                "type": "vehicle.update",
                "data": {"vehicle_id": "BUS-WS-99", "latitude": 12.9716, "longitude": 80.2440, "speed": 45.0},
            },
        )

        response = await communicator.receive_from()
        data = json.loads(response)
        self.assertEqual(data["vehicle_id"], "BUS-WS-99")
        self.assertEqual(data["latitude"], 12.9716)

        await communicator.disconnect()

    async def test_alerts_websocket_connection(self):
        communicator = WebsocketCommunicator(application, "/ws/alerts/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "alerts",
            {
                "type": "alert.notification",
                "data": {"alert_type": "OVERSPEED", "severity": "CRITICAL", "message": "Overspeed detected"},
            },
        )

        response = await communicator.receive_from()
        data = json.loads(response)
        self.assertEqual(data["alert_type"], "OVERSPEED")

        await communicator.disconnect()
