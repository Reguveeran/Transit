"""
UniTransit - Live Background Telemetry Streaming Command
Continuously updates vehicles along realistic paths and broadcasts
live coordinates directly to connected WebSocket clients and the database.
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.management.base import BaseCommand

from adapters.simulator.simulator import CORRIDORS, SimulatedVehicleState
from apps.routes.models import Route
from apps.vehicles.models import TransportMode, Vehicle
from apps.alerts.models import Alert

logger = logging.getLogger("unitransit.live_stream")


class Command(BaseCommand):
    help = "Runs continuous background vehicle telemetry generation and WebSocket broadcasting."

    def add_arguments(self, parser):
        parser.add_argument("--vehicles", type=int, default=15, help="Active fleet size to stream")
        parser.add_argument("--interval", type=float, default=2.0, help="Broadcast interval in seconds")

    def handle(self, *args, **options):
        vehicle_count = options["vehicles"]
        interval = options["interval"]
        channel_layer = get_channel_layer()

        self.stdout.write(self.style.SUCCESS(f"🚀 Starting UniTransit Live Telemetry Broadcaster ({vehicle_count} vehicles, {interval}s interval)..."))

        # Initialize fleet states along routes
        corridor_keys = list(CORRIDORS.keys())
        fleet = []
        for i in range(1, vehicle_count + 1):
            route_key = corridor_keys[i % len(corridor_keys)]
            waypoints = CORRIDORS[route_key]
            v_mode = "bus" if "12" in route_key else "metro" if "METRO" in route_key else "ferry"
            v_id = f"{v_mode.upper()}-{100 + i}"
            mode_obj, _ = TransportMode.objects.get_or_create(
                name=v_mode,
                defaults={"display_name": v_mode.capitalize(), "icon_name": v_mode},
            )
            route_obj = Route.objects.filter(route_id=route_key).first()

            # Ensure in DB
            db_veh, _ = Vehicle.objects.get_or_create(
                vehicle_id=v_id,
                defaults={
                    "transport_mode": mode_obj,
                    "current_route": route_obj,
                    "current_latitude": waypoints[0][0],
                    "current_longitude": waypoints[0][1],
                    "current_speed": 35.0,
                    "status": "MOVING",
                },
            )

            state = SimulatedVehicleState(
                vehicle_id=v_id,
                mode=v_mode,
                route_id=route_key,
                waypoints=waypoints,
                current_index=i % len(waypoints),
                sub_progress=0.0,
                speed=35.0 + (i % 5) * 4.0,
            )
            fleet.append((state, db_veh))

        tick = 0
        try:
            while True:
                tick += 1
                now_iso = datetime.now(timezone.utc).isoformat()

                # Stream simulated fleet
                for state, db_veh in fleet:
                    event = state.step(interval_sec=interval, fault_rate=0.03)
                    if not event:
                        continue

                    # 1. Update Database
                    Vehicle.objects.filter(id=db_veh.id).update(
                        current_latitude=event.latitude,
                        current_longitude=event.longitude,
                        current_speed=event.speed,
                        current_heading=event.heading,
                        status=event.status,
                        delay_seconds=event.delay_seconds,
                        last_seen=datetime.now(timezone.utc),
                    )

                    # 2. Broadcast to Django Channels group (Hot Path)
                    msg_payload = {
                        "type": "vehicle.update",
                        "vehicle_id": event.vehicle_id,
                        "mode": event.mode,
                        "route_id": event.route_id,
                        "latitude": event.latitude,
                        "longitude": event.longitude,
                        "speed": event.speed,
                        "heading": event.heading,
                        "status": event.status,
                        "delay_seconds": event.delay_seconds,
                        "timestamp": now_iso,
                    }

                    if channel_layer:
                        async_to_sync(channel_layer.group_send)(
                            "vehicle_updates",
                            {
                                "type": "vehicle_update",
                                "data": msg_payload,
                            },
                        )

                # Poll and stream real live aircraft from OpenSky Network every 10s
                if tick % 5 == 0 and os.getenv("ENABLE_OPENSKY") == "true":
                    try:
                        from adapters.adsb.opensky_adapter import fetch_live_flights, normalize_opensky_vector
                        # Bounding box around regional airspace: lat [10.0, 16.0], lon [76.0, 83.0]
                        flights = fetch_live_flights(bbox=(10.0, 16.0, 76.0, 83.0))
                        if not flights:
                            # Fallback to broader sample if regional box has no current flights
                            flights = fetch_live_flights()
                        
                        plane_mode, _ = TransportMode.objects.get_or_create(
                            name="aircraft",
                            defaults={"display_name": "Commercial Aircraft", "icon_name": "plane"},
                        )

                        for f_state in (flights or [])[:10]:
                            ev = normalize_opensky_vector(f_state)
                            if not ev:
                                continue

                            veh_obj, _ = Vehicle.objects.get_or_create(
                                vehicle_id=ev.vehicle_id,
                                defaults={
                                    "transport_mode": plane_mode,
                                    "current_latitude": ev.latitude,
                                    "current_longitude": ev.longitude,
                                    "current_speed": ev.speed,
                                    "current_heading": ev.heading,
                                    "status": ev.status,
                                    "label": f"Flight {ev.route_id} ({ev.metadata.get('origin_country', 'Air')})",
                                },
                            )
                            Vehicle.objects.filter(id=veh_obj.id).update(
                                current_latitude=ev.latitude,
                                current_longitude=ev.longitude,
                                current_speed=ev.speed,
                                current_heading=ev.heading,
                                status=ev.status,
                                last_seen=datetime.now(timezone.utc),
                            )

                            if channel_layer:
                                async_to_sync(channel_layer.group_send)(
                                    "vehicle_updates",
                                    {
                                        "type": "vehicle_update",
                                        "data": {
                                            "type": "vehicle.update",
                                            "vehicle_id": ev.vehicle_id,
                                            "mode": "aircraft",
                                            "route_id": ev.route_id,
                                            "latitude": ev.latitude,
                                            "longitude": ev.longitude,
                                            "speed": ev.speed,
                                            "heading": ev.heading,
                                            "status": ev.status,
                                            "delay_seconds": 0,
                                            "timestamp": now_iso,
                                        },
                                    },
                                )
                        self.stdout.write(self.style.SUCCESS(f"  ✈️ Streamed {min(10, len(flights or []))} live OpenSky aircraft into live map."))
                    except Exception as air_err:
                        logger.error(f"Live aircraft stream note: {air_err}")

                if tick % 5 == 0:
                    self.stdout.write(f"  [~] Broadcast tick #{tick}: stream active for {len(fleet)} vehicles")

                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write("Live stream stopped.")
