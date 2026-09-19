"""
UniTransit - Seed Data Management Command
Populates the database with realistic initial multi-transport modes, routes, stops, trips, and vehicles.
"""

from datetime import datetime, time, timezone
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.vehicles.models import TransportMode, Vehicle
from apps.routes.models import Route
from apps.stops.models import Stop
from apps.trips.models import Trip, StopTime
from apps.alerts.models import ServiceAlert


class Command(BaseCommand):
    help = "Seeds the database with initial multi-modal transit networks, routes, stops, vehicles, and trips."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding UniTransit multi-transport database..."))

        # 1. Transport Modes
        modes_data = [
            {"name": "bus", "display_name": "City Bus", "icon_name": "bus", "description": "Urban and suburban bus networks"},
            {"name": "metro", "display_name": "Metro / Rapid Transit", "icon_name": "train-subway", "description": "High-capacity underground and elevated rapid rail"},
            {"name": "train", "display_name": "Commuter Rail", "icon_name": "train", "description": "Intercity and regional heavy rail"},
            {"name": "tram", "display_name": "Streetcar / Tram", "icon_name": "tram", "description": "Light rail and streetcar lines"},
            {"name": "ferry", "display_name": "Harbor Ferry", "icon_name": "ship", "description": "Waterborne transit and passenger ferries"},
            {"name": "aircraft", "display_name": "Regional Aircraft", "icon_name": "plane", "description": "Regional feeder flights"},
        ]

        modes = {}
        for m in modes_data:
            obj, created = TransportMode.objects.update_or_create(
                name=m["name"],
                defaults=m,
            )
            modes[m["name"]] = obj
            if created:
                self.stdout.write(f"  [+] Mode created: {obj.display_name}")

        # 2. Stops
        stops_data = [
            # Bus Stops (Downtown to Tech Park corridor)
            {"stop_id": "STOP-DT-01", "name": "Central Terminal Station", "code": "CTS", "latitude": 12.9716, "longitude": 80.2440, "transport_mode": modes["bus"]},
            {"stop_id": "STOP-DT-02", "name": "Victoria Square", "code": "VSQ", "latitude": 12.9800, "longitude": 80.2480, "transport_mode": modes["bus"]},
            {"stop_id": "STOP-DT-03", "name": "Innovation Hub Boulevard", "code": "IHB", "latitude": 12.9880, "longitude": 80.2530, "transport_mode": modes["bus"]},
            {"stop_id": "STOP-DT-04", "name": "Cyber Towers North", "code": "CTN", "latitude": 12.9960, "longitude": 80.2600, "transport_mode": modes["bus"]},
            {"stop_id": "STOP-DT-05", "name": "Silicon Gateway Tech Park", "code": "SGTP", "latitude": 13.0040, "longitude": 80.2650, "transport_mode": modes["bus"]},

            # Metro Stops (Blue Line)
            {"stop_id": "STOP-METRO-01", "name": "Airport Hub Terminal", "code": "AHT", "latitude": 12.9900, "longitude": 80.1700, "transport_mode": modes["metro"]},
            {"stop_id": "STOP-METRO-02", "name": "Southern Junction Metro", "code": "SJM", "latitude": 13.0100, "longitude": 80.2000, "transport_mode": modes["metro"]},
            {"stop_id": "STOP-METRO-03", "name": "Central Interchange", "code": "CIN", "latitude": 13.0300, "longitude": 80.2300, "transport_mode": modes["metro"]},
            {"stop_id": "STOP-METRO-04", "name": "Marina Coast North", "code": "MCN", "latitude": 13.0600, "longitude": 80.2700, "transport_mode": modes["metro"]},

            # Ferry Piers
            {"stop_id": "STOP-FERRY-01", "name": "Harbor Wharf Gate 1", "code": "HW1", "latitude": 13.0850, "longitude": 80.2950, "transport_mode": modes["ferry"]},
            {"stop_id": "STOP-FERRY-02", "name": "Port Marina Terminal", "code": "PMT", "latitude": 13.1200, "longitude": 80.3150, "transport_mode": modes["ferry"]},
        ]

        stops = {}
        for s in stops_data:
            obj, created = Stop.objects.update_or_create(
                stop_id=s["stop_id"],
                defaults=s,
            )
            stops[s["stop_id"]] = obj

        self.stdout.write(f"  [+] Loaded {len(stops)} transit stops.")

        # 3. Routes with Polyline Geometries
        routes_data = [
            {
                "route_id": "ROUTE-12",
                "transport_mode": modes["bus"],
                "short_name": "R12",
                "long_name": "Downtown Terminal — Tech Park Express",
                "color": "#3B82F6",
                "text_color": "#FFFFFF",
                "polyline_geojson": {
                    "type": "LineString",
                    "coordinates": [
                        [80.2440, 12.9716],
                        [80.2480, 12.9800],
                        [80.2530, 12.9880],
                        [80.2600, 12.9960],
                        [80.2650, 13.0040],
                    ],
                },
            },
            {
                "route_id": "ROUTE-METRO-BLUE",
                "transport_mode": modes["metro"],
                "short_name": "M-BLUE",
                "long_name": "Airport Hub — Marina Coast Rapid Line",
                "color": "#06B6D4",
                "text_color": "#FFFFFF",
                "polyline_geojson": {
                    "type": "LineString",
                    "coordinates": [
                        [80.1700, 12.9900],
                        [80.2000, 13.0100],
                        [80.2300, 13.0300],
                        [80.2700, 13.0600],
                    ],
                },
            },
            {
                "route_id": "ROUTE-FERRY-01",
                "transport_mode": modes["ferry"],
                "short_name": "F1",
                "long_name": "Wharf Gate 1 — Port Marina Ferry",
                "color": "#10B981",
                "text_color": "#FFFFFF",
                "polyline_geojson": {
                    "type": "LineString",
                    "coordinates": [
                        [80.2950, 13.0850],
                        [80.3150, 13.1200],
                    ],
                },
            },
        ]

        routes = {}
        for r in routes_data:
            obj, created = Route.objects.update_or_create(
                route_id=r["route_id"],
                defaults=r,
            )
            routes[r["route_id"]] = obj

        self.stdout.write(f"  [+] Loaded {len(routes)} active transit routes.")

        # 4. Vehicles
        vehicles_data = [
            {"vehicle_id": "BUS-101", "transport_mode": modes["bus"], "label": "Volvo 8400 City Bus", "capacity": 60, "current_latitude": 12.9716, "current_longitude": 80.2440, "current_speed": 38.5, "current_heading": 45.0, "status": "MOVING", "current_route": routes["ROUTE-12"]},
            {"vehicle_id": "BUS-102", "transport_mode": modes["bus"], "label": "Electric Low-Floor EV-Bus", "capacity": 55, "current_latitude": 12.9880, "current_longitude": 80.2530, "current_speed": 42.0, "current_heading": 50.0, "status": "MOVING", "current_route": routes["ROUTE-12"]},
            {"vehicle_id": "BUS-103", "transport_mode": modes["bus"], "label": "Standard Transit Bus", "capacity": 65, "current_latitude": 12.9960, "current_longitude": 80.2600, "current_speed": 0.0, "current_heading": 180.0, "status": "STOPPED", "current_route": routes["ROUTE-12"]},
            {"vehicle_id": "METRO-B01", "transport_mode": modes["metro"], "label": "Alstom Metropolis 6-Car", "capacity": 1200, "current_latitude": 13.0100, "current_longitude": 80.2000, "current_speed": 72.0, "current_heading": 30.0, "status": "MOVING", "current_route": routes["ROUTE-METRO-BLUE"]},
            {"vehicle_id": "FERRY-SEA-01", "transport_mode": modes["ferry"], "label": "Catamaran Fast Ferry", "capacity": 150, "current_latitude": 13.0900, "current_longitude": 80.3000, "current_speed": 22.0, "current_heading": 25.0, "status": "MOVING", "current_route": routes["ROUTE-FERRY-01"]},
        ]

        vehicles = {}
        for v in vehicles_data:
            obj, created = Vehicle.objects.update_or_create(
                vehicle_id=v["vehicle_id"],
                defaults=v,
            )
            vehicles[v["vehicle_id"]] = obj

        self.stdout.write(f"  [+] Loaded {len(vehicles)} fleet vehicles.")

        # 5. Trips & StopTimes
        trip_obj, created = Trip.objects.update_or_create(
            trip_id="TRIP-R12-001",
            defaults={
                "route": routes["ROUTE-12"],
                "vehicle": vehicles["BUS-101"],
                "service_id": "DAILY",
                "headsign": "Silicon Gateway Tech Park via Innovation Blvd",
                "direction": 0,
                "status": "IN_PROGRESS",
            },
        )

        r12_stops = [
            stops["STOP-DT-01"],
            stops["STOP-DT-02"],
            stops["STOP-DT-03"],
            stops["STOP-DT-04"],
            stops["STOP-DT-05"],
        ]

        for seq, stop in enumerate(r12_stops, start=1):
            StopTime.objects.update_or_create(
                trip=trip_obj,
                stop_sequence=seq,
                defaults={
                    "stop": stop,
                    "arrival_time": time(8, (seq - 1) * 10, 0),
                    "departure_time": time(8, (seq - 1) * 10 + 2, 0),
                },
            )

        # 6. Service Alerts
        ServiceAlert.objects.update_or_create(
            alert_id="ALERT-SRV-2026-01",
            defaults={
                "title": "Road Maintenance on Innovation Boulevard",
                "header_text": "Minor delays expected on Route R12",
                "description_text": "Lane closure between Victoria Sq and Innovation Blvd due to fiber optic maintenance. Expect +5 to +10 minute delays.",
                "cause": "CONSTRUCTION",
                "effect": "SIGNIFICANT_DELAYS",
                "is_active": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("✓ Successfully initialized and seeded UniTransit multi-transport database!"))
